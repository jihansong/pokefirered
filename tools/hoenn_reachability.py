#!/usr/bin/env python3
"""hoenn_reachability.py [--start MAP_PALLET_TOWN] [--format md|tsv|json] [--out FILE]
                         [--all] [--emerald /root/src/pokeemerald]

Inventory of the imported Hoenn maps and whether the player can reach each one
from KANTO. Read-only; rerun it after any map change.

The map graph has an edge for
  - every map connection (up/down/left/right; dive/emerge are kept apart
    because this engine has no way to use DIVE yet, see below),
  - every warp event (map.json warp_events),
  - every scripted warp (warp, warpsilent, warpdoor, warphole, warpteleport,
    warpspinenter and the set*warp macros) in a label that the map's scripts
    reach through goto/call/fall-through, shared data/scripts/*.inc included,
  - every C special that warps by itself (the airplane, the Seagallop ferry):
    its destination table is read from the C source (mapdata_common.py).

Reachability is a map-level graph walk from --start. It does not model story
flags, HMs or where inside a map a warp sits (a warp on an island still counts
once the map is reached), so "reachable" means "connected", not "walkable
today"; the airplane itself only boards after FLAG_SYS_GAME_CLEAR.

A warp event only fires on a warp tile (door, stairs, ladder, cave door,
arrow...); one on plain ground waits for a script to swap the metatile (the
E4 doors, TERRA CAVE, the TRICK HOUSE). Such "inert" warps are followed last.

Columns: reach (Y = connected without DIVE, D = also needs a dive/emerge
connection, W = also needs an inert warp tile to be opened, - = not connected), via (edge that first reached it), conn/warp
(outgoing edges), in (incoming edges from any map), npc (talk-only NPCs), trn
(trainers), item (item balls), svc (nurse/mart), bt (berry-tree placeholders:
objects with MOVEMENT_TYPE_BERRY_TREE_GROWTH), sign, hid (hidden items), coord
(coord events), wild (L land, W water, R rock smash, F fishing), heal (heal
location), em_obj/em_coord (object/coord events in pokeemerald, with --emerald).
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapdata_common as C  # noqa: E402


def classify_objects(name, d, scripts):
    """Counts per object kind for one map."""
    c = collections.Counter()
    trainers = set()
    for o in d.get('object_events') or []:
        if o.get('movement_type') == 'MOVEMENT_TYPE_BERRY_TREE_GROWTH':
            c['bt'] += 1
            continue
        s = o.get('script', '0x0')
        if o.get('graphics_id') == 'OBJ_EVENT_GFX_ITEM_BALL':
            c['item'] += 1
            continue
        if s in ('0x0', '0', ''):
            c['noscript'] += 1
            continue
        body = scripts.labels.get(s)
        text = ''
        if body:
            text = open(C.rel(body['file']), encoding='utf-8', errors='replace').read()
        # the label's own lines
        seg = ''
        if body:
            lines = text.splitlines()[body['line']:]
            out = []
            for ln in lines:
                if C.LABEL_RE.match(ln):
                    break
                out.append(ln.strip())
            seg = '\n'.join(out)
        if s == 'EventScript_PkmnCenterNurse' or 'pokemart' in seg:
            c['svc'] += 1
        elif 'trainerbattle' in seg:
            c['trn'] += 1
            trainers.update(re.findall(r'trainerbattle_\w+\s+(TRAINER_\w+)', seg))
        elif re.fullmatch(r'msgbox \w+, MSGBOX_\w+\nend', seg.strip()):
            c['npc'] += 1
        else:
            c['other'] += 1
    for b in d.get('bg_events') or []:
        if b.get('type') == 'hidden_item':
            c['hid'] += 1
        else:
            c['sign'] += 1
    c['coord'] = len(d.get('coord_events') or [])
    return c, trainers


def wild_summary():
    j = json.load(open(C.rel('src/data/wild_encounters.json')))
    out = collections.defaultdict(set)
    for g in j['wild_encounter_groups']:
        for e in g['encounters']:
            for key, letter in (('land_mons', 'L'), ('water_mons', 'W'), ('rock_smash_mons', 'R'), ('fishing_mons', 'F')):
                if any(k.startswith(key) for k in e):
                    out[e['map']].add(letter)
    return {m: ''.join(x for x in 'LWRF' if x in s) for m, s in out.items()}


def heal_maps():
    j = json.load(open(C.rel('src/data/heal_locations.json')))
    return {h['map'] for h in j['heal_locations']}


def build_graph(maps, scripts, metatiles=None):
    """edges[src] = [(dst_name, kind, detail)]. With metatiles, a warp event on a
    tile that is not a warp behavior becomes kind 'inert' (a script has to open it)."""
    ids = C.map_ids(maps)
    specials = C.special_destinations()
    edges = collections.defaultdict(list)
    for name, d in maps.items():
        for c in d.get('connections') or []:
            t = ids.get(c['map'])
            if t:
                kind = 'dive' if c['direction'] in ('dive', 'emerge') else 'conn'
                edges[name].append((t, kind, c['direction']))
        for i, w in enumerate(d.get('warp_events') or []):
            t = ids.get(w['dest_map'])
            if t:
                live = metatiles.warp_is_live(d, w) if metatiles else True
                edges[name].append((t, 'warp' if live is not False else 'inert', f'warp {i}'))
        for lab in scripts.closure(scripts.map_roots(name, d)):
            info = scripts.labels[lab]
            for cmd, target, _ in info['warps']:
                t = ids.get(target)
                if t:
                    edges[name].append((t, 'script', f'{cmd} in {lab}'))
            for sp in info['specials']:
                for target in specials.get(sp, []):
                    t = ids.get(target)
                    if t and t != name:
                        edges[name].append((t, 'special', f'special {sp} ({lab})'))
    return edges


def walk(edges, start, allow_dive, allow_inert=False):
    via = {start: None}
    queue = collections.deque([start])
    while queue:
        cur = queue.popleft()
        for t, kind, detail in edges.get(cur, []):
            if (kind == 'dive' and not allow_dive) or (kind == 'inert' and not allow_inert):
                continue
            if t not in via:
                via[t] = (cur, kind, detail)
                queue.append(t)
    return via


def emerald_counts(em_root, name):
    # imported names are Emerald's, except the two renamed ones
    back = {'HoennVictoryRoad_1F': 'VictoryRoad_1F', 'HoennSafariZone_North': 'SafariZone_North'}
    p = os.path.join(em_root, 'data/maps', back.get(name, name), 'map.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    if d.get('shared_events_map'):
        d = json.load(open(os.path.join(em_root, 'data/maps', d['shared_events_map'], 'map.json')))
    return len(d.get('object_events') or []), len(d.get('coord_events') or [])


# Zones of docs/hoenn-open-plan.md: region map section -> zone. A map name
# prefix in ZONE_BY_NAME wins over its section (facilities and event maps that
# borrow a nearby section, see MAPSEC_FALLBACK in tools/hoenn_import/import_maps.py).
ZONE_BY_SECTION = {
    'Z1': 'SLATEPORT_CITY ROUTE_109 DEWFORD_TOWN GRANITE_CAVE ROUTE_106 ROUTE_107 ROUTE_108 ABANDONED_SHIP',
    'Z2': 'ROUTE_110 MAUVILLE_CITY NEW_MAUVILLE ROUTE_117 VERDANTURF_TOWN ROUTE_118',
    'Z3': 'RUSTURF_TUNNEL RUSTBORO_CITY ROUTE_104 ROUTE_115 ROUTE_116 PETALBURG_WOODS PETALBURG_CITY ROUTE_101 '
          'ROUTE_102 ROUTE_103 OLDALE_TOWN LITTLEROOT_TOWN ROUTE_105 ALTERING_CAVE',
    'Z4': 'ROUTE_111 ROUTE_112 ROUTE_113 ROUTE_114 FIERY_PATH MT_CHIMNEY JAGGED_PASS LAVARIDGE_TOWN FALLARBOR_TOWN '
          'METEOR_FALLS DESERT_RUINS',
    'Z5': 'ROUTE_119 FORTREE_CITY ROUTE_120 ROUTE_121 SAFARI_ZONE LILYCOVE_CITY MT_PYRE ROUTE_122 ROUTE_123 '
          'SCORCHED_SLAB ANCIENT_TOMB',
    'Z6': 'ROUTE_124 ROUTE_125 ROUTE_126 ROUTE_127 ROUTE_128 ROUTE_129 ROUTE_130 ROUTE_131 ROUTE_132 ROUTE_133 '
          'ROUTE_134 MOSSDEEP_CITY SHOAL_CAVE PACIFIDLOG_TOWN SOOTOPOLIS_CITY SEAFLOOR_CAVERN CAVE_OF_ORIGIN SKY_PILLAR '
          'SEALED_CHAMBER UNDERWATER_124 UNDERWATER_125 UNDERWATER_126 UNDERWATER_127 UNDERWATER_128 '
          'UNDERWATER_SEALED_CHAMBER UNDERWATER_SOOTOPOLIS ISLAND_CAVE',
    'Z7': 'EVER_GRANDE_CITY VICTORY_ROAD',
    'Z8': 'BATTLE_FRONTIER SOUTHERN_ISLAND INSIDE_OF_TRUCK DYNAMIC',
}
ZONE_BY_NAME = [
    ('TerraCave_', 'Z8'), ('MarineCave_', 'Z8'), ('Underwater_MarineCave', 'Z8'), ('ArtisanCave_', 'Z8'),
    ('FarawayIsland_', 'Z8'), ('SSTidal', 'Z8'), ('ContestHall', 'Z8'), ('BattlePyramidSquare', 'Z8'),
    ('SlateportCity_BattleTent', 'Z8'), ('VerdanturfTown_BattleTent', 'Z8'), ('FallarborTown_BattleTent', 'Z8'),
    ('MirageTower_', 'Z4'), ('Route110_TrickHouse', 'Z2'),
]


def zone_of(name, d):
    for prefix, z in ZONE_BY_NAME:
        if name.startswith(prefix):
            return z
    sec = d['region_map_section'].replace('MAPSEC_', '')
    for z, secs in ZONE_BY_SECTION.items():
        if sec in secs.split():
            return z
    return '?'


def write_zones(maps, rows, edges, out):
    zone = {r['map']: zone_of(r['map'], maps[r['map']]) for r in rows}
    agg = collections.defaultdict(collections.Counter)
    for r in rows:
        a = agg[zone[r['map']]]
        a['maps'] += 1
        a['reach_Y'] += r['reach'] == 'Y'
        for k in ('npc', 'trn', 'item', 'hid', 'bt', 'sign'):
            a[k] += r[k]
        a['wild'] += bool(r['wild'])
        a['heal'] += bool(r['heal'])
    out.write('| zone | maps | reach Y | npc | trn | item | hid | bt | sign | wild maps | heal |\n|---|---|---|---|---|---|---|---|---|---|---|\n')
    for z in sorted(agg):
        a = agg[z]
        out.write(f'| {z} | {a["maps"]} | {a["reach_Y"]} | {a["npc"]} | {a["trn"]} | {a["item"]} | {a["hid"]} | '
                  f'{a["bt"]} | {a["sign"]} | {a["wild"]} | {a["heal"]} |\n')
    out.write('\nCross-zone edges (where a blocker or a story gate has to sit):\n\n')
    seen = set()
    for src in sorted(zone):
        for t, kind, detail in edges.get(src, []):
            if t in zone and zone[t] != zone[src]:
                key = (src, t, kind, detail)
                if key not in seen:
                    seen.add(key)
                    out.write(f'- {zone[src]} -> {zone[t]}: `{src}` -> `{t}` ({kind} {detail})\n')
    out.write('\nMaps per zone:\n\n')
    for z in sorted(agg):
        out.write(f'- {z}: ' + ', '.join(sorted(m for m in zone if zone[m] == z)) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--zones', action='store_true', help='print the zone table of docs/hoenn-open-plan.md and the '
                    'connections/warps that cross zones instead of the map table')
    ap.add_argument('--start', default='MAP_PALLET_TOWN')
    ap.add_argument('--format', choices=('md', 'tsv', 'json'), default='md')
    ap.add_argument('--out')
    ap.add_argument('--all', action='store_true', help='list every map, not only the Hoenn ones')
    ap.add_argument('--emerald', default=None, help='pokeemerald checkout for the em_obj/em_coord columns')
    a = ap.parse_args()

    maps, order = C.load_maps()
    ids = C.map_ids(maps)
    start = ids.get(a.start, a.start)
    if start not in maps:
        sys.exit(f'unknown start map {a.start}')
    scripts = C.ScriptIndex(maps)
    edges = build_graph(maps, scripts, C.Metatiles())
    reach = walk(edges, start, allow_dive=False)
    reach_dive = walk(edges, start, allow_dive=True)
    reach_inert = walk(edges, start, allow_dive=True, allow_inert=True)
    incoming = collections.Counter()
    for src, lst in edges.items():
        for t, _, _ in lst:
            if t != src:
                incoming[t] += 1
    wild = wild_summary()
    heals = heal_maps()

    rows = []
    for name in order:
        d = maps[name]
        if not (a.all or d['_hoenn']):
            continue
        cnt, trainers = classify_objects(name, d, scripts)
        if name in reach:
            r = 'Y'
            v = reach[name]
        elif name in reach_dive:
            r = 'D'
            v = reach_dive[name]
        elif name in reach_inert:
            r = 'W'
            v = reach_inert[name]
        else:
            r = '-'
            v = None
        via = '' if v is None else f'{v[0]} ({v[1]})' if v[1] != 'special' else f'{v[0]} ({v[2].split(" (")[0]})'
        conns = [c['direction'] for c in d.get('connections') or []]
        row = {
            'map': name, 'group': d['_group'].replace('gMapGroup_', ''), 'type': d['map_type'].replace('MAP_TYPE_', ''),
            'reach': r, 'via': via,
            'conn': len(conns), 'dive': sum(1 for x in conns if x in ('dive', 'emerge')),
            'warp': len(d.get('warp_events') or []), 'in': incoming[name],
            'npc': cnt['npc'], 'trn': cnt['trn'], 'item': cnt['item'], 'svc': cnt['svc'], 'other': cnt['other'],
            'bt': cnt['bt'], 'sign': cnt['sign'], 'hid': cnt['hid'], 'coord': cnt['coord'],
            'wild': wild.get(d['id'], ''), 'heal': 'Y' if d['id'] in heals else '',
            'trainers': sorted(trainers),
        }
        if a.emerald:
            ec = emerald_counts(a.emerald, name)
            row['em_obj'], row['em_coord'] = ec if ec else ('?', '?')
        rows.append(row)

    hoenn = [r for r in rows if maps[r['map']]['_hoenn']]
    summary = collections.Counter(r['reach'] for r in hoenn)
    entries = sorted({(src, t, kind, detail) for src, lst in edges.items() if not maps[src]['_hoenn']
                      for t, kind, detail in lst if maps[t]['_hoenn']})

    out = open(a.out, 'w') if a.out else sys.stdout
    if a.zones:
        write_zones(maps, hoenn, edges, out)
        return
    if a.format == 'json':
        json.dump({'start': start, 'summary': dict(summary), 'kanto_to_hoenn_edges': entries, 'maps': rows}, out, indent=1)
        out.write('\n')
        return
    cols = ['map', 'group', 'type', 'reach', 'via', 'conn', 'dive', 'warp', 'in', 'npc', 'trn', 'item', 'svc',
            'other', 'bt', 'sign', 'hid', 'coord', 'wild', 'heal']
    if a.emerald:
        cols += ['em_obj', 'em_coord']
    if a.format == 'tsv':
        out.write('\t'.join(cols) + '\n')
        for r in rows:
            out.write('\t'.join(str(r[c]) for c in cols) + '\n')
        return
    tot = lambda k: sum(r[k] for r in hoenn if isinstance(r[k], int))
    out.write(f'Start: `{start}`. Hoenn maps: {len(hoenn)}; reachable (Y): {summary["Y"]}; '
              f'only through DIVE (D): {summary["D"]}; only through a closed warp tile (W): {summary["W"]}; '
              f'not connected (-): {summary["-"]}.\n\n')
    out.write('Edges from non-Hoenn maps into Hoenn:\n\n')
    for src, t, kind, detail in entries:
        out.write(f'- `{src}` -> `{t}` ({kind}: {detail})\n')
    out.write(f'\nTotals over Hoenn maps: npc {tot("npc")}, trn {tot("trn")}, item {tot("item")}, svc {tot("svc")}, '
              f'other {tot("other")}, bt {tot("bt")}, sign {tot("sign")}, hid {tot("hid")}, coord {tot("coord")}, '
              f'maps with wild data {sum(1 for r in hoenn if r["wild"])}, heal locations {sum(1 for r in hoenn if r["heal"])}.\n\n')
    out.write('| ' + ' | '.join(cols) + ' |\n|' + '---|' * len(cols) + '\n')
    for r in rows:
        out.write('| ' + ' | '.join(str(r[c]) for c in cols) + ' |\n')


if __name__ == '__main__':
    main()
