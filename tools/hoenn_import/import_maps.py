#!/usr/bin/env python3
"""Import pokeemerald maps (Hoenn) into pokefirered. Phase 1: geography.
Layouts, map headers, connections, warps, always-present NPCs with their first
line of dialogue, signs, Pokémon Center nurses, marts and wild encounters.
Story scripts, trainers, items and Emerald-only sprites/music come later."""
import json, os, re, shutil, sys, collections
EM = '/root/src/pokeemerald'
FR = '/workspaces/pokefirered'
sys.path.insert(0, '/root/qa-tools/hoenn')
import import_tilesets

EXCLUDE = re.compile(r'^(SecretBase_|BattleColosseum_|TradeCenter$|RecordCorner$|UnionRoom$|BirthIsland_|NavelRock_|'
                     r'Route104_Prototype|UnusedContestHall)')
RENAME = {'VictoryRoad_1F': 'HoennVictoryRoad_1F', 'SafariZone_North': 'HoennSafariZone_North'}
RENAME_ID = {'MAP_VICTORY_ROAD_1F': 'MAP_HOENN_VICTORY_ROAD_1F', 'MAP_SAFARI_ZONE_NORTH': 'MAP_HOENN_SAFARI_ZONE_NORTH'}
# FR/LG stand-ins until the Emerald sprites are imported
GFX = {
 'OBJ_EVENT_GFX_BOY_1': 'OBJ_EVENT_GFX_LITTLE_BOY', 'OBJ_EVENT_GFX_BOY_2': 'OBJ_EVENT_GFX_YOUNGSTER', 'OBJ_EVENT_GFX_BOY_3': 'OBJ_EVENT_GFX_BOY',
 'OBJ_EVENT_GFX_GIRL_1': 'OBJ_EVENT_GFX_LITTLE_GIRL', 'OBJ_EVENT_GFX_GIRL_2': 'OBJ_EVENT_GFX_LASS', 'OBJ_EVENT_GFX_GIRL_3': 'OBJ_EVENT_GFX_LASS',
 'OBJ_EVENT_GFX_MAN_1': 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_MAN_2': 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_MAN_3': 'OBJ_EVENT_GFX_BALDING_MAN',
 'OBJ_EVENT_GFX_MAN_4': 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_MAN_5': 'OBJ_EVENT_GFX_FAT_MAN', 'OBJ_EVENT_GFX_WOMAN_4': 'OBJ_EVENT_GFX_WOMAN_2',
 'OBJ_EVENT_GFX_WOMAN_5': 'OBJ_EVENT_GFX_WOMAN_3', 'OBJ_EVENT_GFX_OLD_MAN': 'OBJ_EVENT_GFX_OLD_MAN_1', 'OBJ_EVENT_GFX_EXPERT_M': 'OBJ_EVENT_GFX_OLD_MAN_2',
 'OBJ_EVENT_GFX_EXPERT_F': 'OBJ_EVENT_GFX_OLD_WOMAN', 'OBJ_EVENT_GFX_FISHERMAN': 'OBJ_EVENT_GFX_FISHER', 'OBJ_EVENT_GFX_MART_EMPLOYEE': 'OBJ_EVENT_GFX_CLERK',
 'OBJ_EVENT_GFX_SCIENTIST_1': 'OBJ_EVENT_GFX_SCIENTIST', 'OBJ_EVENT_GFX_SCIENTIST_2': 'OBJ_EVENT_GFX_SCIENTIST', 'OBJ_EVENT_GFX_POKEFAN_F': 'OBJ_EVENT_GFX_WOMAN_1',
 'OBJ_EVENT_GFX_POKEFAN_M': 'OBJ_EVENT_GFX_GENTLEMAN', 'OBJ_EVENT_GFX_MANIAC': 'OBJ_EVENT_GFX_POKE_MANIAC', 'OBJ_EVENT_GFX_NINJA_BOY': 'OBJ_EVENT_GFX_YOUNGSTER',
 'OBJ_EVENT_GFX_TWIN': 'OBJ_EVENT_GFX_LITTLE_GIRL', 'OBJ_EVENT_GFX_SWIMMER_F': 'OBJ_EVENT_GFX_SWIMMER_F_LAND', 'OBJ_EVENT_GFX_SWIMMER_M': 'OBJ_EVENT_GFX_SWIMMER_M_LAND',
 'OBJ_EVENT_GFX_TUBER_M': 'OBJ_EVENT_GFX_TUBER_M_LAND', 'OBJ_EVENT_GFX_TUBER_M_SWIMMING': 'OBJ_EVENT_GFX_TUBER_M_WATER', 'OBJ_EVENT_GFX_PSYCHIC_M': 'OBJ_EVENT_GFX_CHANNELER',
 'OBJ_EVENT_GFX_HEX_MANIAC': 'OBJ_EVENT_GFX_CHANNELER', 'OBJ_EVENT_GFX_RICH_BOY': 'OBJ_EVENT_GFX_BOY', 'OBJ_EVENT_GFX_SCHOOL_KID_M': 'OBJ_EVENT_GFX_BOY',
 'OBJ_EVENT_GFX_GAMEBOY_KID': 'OBJ_EVENT_GFX_GBA_KID', 'OBJ_EVENT_GFX_COOK': 'OBJ_EVENT_GFX_CHEF', 'OBJ_EVENT_GFX_LINK_RECEPTIONIST': 'OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST',
 'OBJ_EVENT_GFX_UNION_ROOM_NURSE': 'OBJ_EVENT_GFX_NURSE', 'OBJ_EVENT_GFX_CUTTABLE_TREE': 'OBJ_EVENT_GFX_CUT_TREE', 'OBJ_EVENT_GFX_BREAKABLE_ROCK': 'OBJ_EVENT_GFX_ROCK_SMASH_ROCK',
 'OBJ_EVENT_GFX_MYSTERY_GIFT_MAN': 'OBJ_EVENT_GFX_MG_DELIVERYMAN', 'OBJ_EVENT_GFX_PROF_BIRCH': 'OBJ_EVENT_GFX_PROF_OAK', 'OBJ_EVENT_GFX_REPORTER_F': 'OBJ_EVENT_GFX_WOMAN_1',
 'OBJ_EVENT_GFX_REPORTER_M': 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_CAMERAMAN': 'OBJ_EVENT_GFX_FAT_MAN', 'OBJ_EVENT_GFX_ARTIST': 'OBJ_EVENT_GFX_GENTLEMAN',
 'OBJ_EVENT_GFX_CYCLING_TRIATHLETE_M': 'OBJ_EVENT_GFX_BIKER', 'OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F': 'OBJ_EVENT_GFX_BIKER',
 'OBJ_EVENT_GFX_RUNNING_TRIATHLETE_M': 'OBJ_EVENT_GFX_COOLTRAINER_M', 'OBJ_EVENT_GFX_RUNNING_TRIATHLETE_F': 'OBJ_EVENT_GFX_COOLTRAINER_F',
 'OBJ_EVENT_GFX_DEVON_EMPLOYEE': 'OBJ_EVENT_GFX_WORKER_M', 'OBJ_EVENT_GFX_CONTEST_JUDGE': 'OBJ_EVENT_GFX_GENTLEMAN', 'OBJ_EVENT_GFX_HOT_SPRINGS_OLD_WOMAN': 'OBJ_EVENT_GFX_OLD_WOMAN',
 'OBJ_EVENT_GFX_ROOFTOP_SALE_WOMAN': 'OBJ_EVENT_GFX_WOMAN_3', 'OBJ_EVENT_GFX_TEALA': 'OBJ_EVENT_GFX_UNION_ROOM_RECEPTIONIST',
 'OBJ_EVENT_GFX_AQUA_MEMBER_M': 'OBJ_EVENT_GFX_ROCKET_M', 'OBJ_EVENT_GFX_AQUA_MEMBER_F': 'OBJ_EVENT_GFX_ROCKET_F', 'OBJ_EVENT_GFX_MAGMA_MEMBER_M': 'OBJ_EVENT_GFX_ROCKET_M',
 'OBJ_EVENT_GFX_MAGMA_MEMBER_F': 'OBJ_EVENT_GFX_ROCKET_F', 'OBJ_EVENT_GFX_WINGULL': 'OBJ_EVENT_GFX_PIDGEY', 'OBJ_EVENT_GFX_ZIGZAGOON_1': 'OBJ_EVENT_GFX_MEOWTH',
 'OBJ_EVENT_GFX_ZIGZAGOON_2': 'OBJ_EVENT_GFX_MEOWTH', 'OBJ_EVENT_GFX_POOCHYENA': 'OBJ_EVENT_GFX_MEOWTH', 'OBJ_EVENT_GFX_SKITTY': 'OBJ_EVENT_GFX_MEOWTH',
 'OBJ_EVENT_GFX_AZURILL': 'OBJ_EVENT_GFX_PIKABLU', 'OBJ_EVENT_GFX_AZUMARILL': 'OBJ_EVENT_GFX_PIKABLU', 'OBJ_EVENT_GFX_KIRLIA': 'OBJ_EVENT_GFX_CLEFAIRY',
 'OBJ_EVENT_GFX_SUDOWOODO': 'OBJ_EVENT_GFX_CUT_TREE', 'OBJ_EVENT_GFX_DEOXYS': 'OBJ_EVENT_GFX_DEOXYS_N', 'OBJ_EVENT_GFX_HOOH': 'OBJ_EVENT_GFX_HO_OH',
 'OBJ_EVENT_GFX_STEVEN': 'OBJ_EVENT_GFX_COOLTRAINER_M', 'OBJ_EVENT_GFX_WALLY': 'OBJ_EVENT_GFX_BOY', 'OBJ_EVENT_GFX_SCOTT': 'OBJ_EVENT_GFX_MAN',
}
GFX_DEFAULT = 'OBJ_EVENT_GFX_MAN'
# Emerald map sections that FR/LG's enum lacks: use the section the place sits in
MAPSEC_FALLBACK = {'MAPSEC_UNDERWATER_129': 'MAPSEC_ROUTE_129', 'MAPSEC_UNDERWATER_105': 'MAPSEC_ROUTE_105', 'MAPSEC_AQUA_HIDEOUT': 'MAPSEC_LILYCOVE_CITY',
    'MAPSEC_UNDERWATER_SEAFLOOR_CAVERN': 'MAPSEC_SEAFLOOR_CAVERN', 'MAPSEC_MAGMA_HIDEOUT': 'MAPSEC_JAGGED_PASS', 'MAPSEC_MIRAGE_TOWER': 'MAPSEC_ROUTE_111',
    'MAPSEC_DESERT_UNDERPASS': 'MAPSEC_ROUTE_114', 'MAPSEC_ARTISAN_CAVE': 'MAPSEC_BATTLE_FRONTIER', 'MAPSEC_UNDERWATER_MARINE_CAVE': 'MAPSEC_ROUTE_128',
    'MAPSEC_MARINE_CAVE': 'MAPSEC_ROUTE_128', 'MAPSEC_TERRA_CAVE': 'MAPSEC_ROUTE_114', 'MAPSEC_FARAWAY_ISLAND': 'MAPSEC_ROUTE_131', 'MAPSEC_TRAINER_HILL': 'MAPSEC_ROUTE_111'}
MUSIC = {'MAP_TYPE_TOWN': 'MUS_PALLET', 'MAP_TYPE_CITY': 'MUS_CELADON', 'MAP_TYPE_ROUTE': 'MUS_ROUTE1', 'MAP_TYPE_OCEAN_ROUTE': 'MUS_SURF',
         'MAP_TYPE_UNDERGROUND': 'MUS_MT_MOON', 'MAP_TYPE_UNDERWATER': 'MUS_SURF', 'MAP_TYPE_INDOOR': 'MUS_POKE_CENTER'}

def fr_defs(path, prefix):
    return set(re.findall(r'#define (%s\w+)' % prefix, open(path).read()))

def em_texts():
    """label -> list of .string lines, from every Emerald script/text file"""
    texts = {}
    files = [f'{EM}/data/maps/{m}/scripts.inc' for m in os.listdir(EM + '/data/maps') if os.path.exists(f'{EM}/data/maps/{m}/scripts.inc')]
    files += [f'{EM}/data/text/{f}' for f in os.listdir(EM + '/data/text') if f.endswith('.inc')]
    files += [f'{EM}/data/maps/{m}/text.inc' for m in os.listdir(EM + '/data/maps') if os.path.exists(f'{EM}/data/maps/{m}/text.inc')]
    for f in files:
        cur = None
        for line in open(f, encoding='utf-8'):
            m = re.match(r'^(\w+)::?\s*$', line)
            if m: cur = m.group(1); continue
            if cur and line.strip().startswith('.string'):
                texts.setdefault(cur, []).append(line.rstrip('\n'))
            elif line.strip() and not line.startswith((' ', '\t')):
                cur = None
    return texts

def em_scripts():
    scripts = {}
    for m in os.listdir(EM + '/data/maps'):
        f = f'{EM}/data/maps/{m}/scripts.inc'
        if not os.path.exists(f): continue
        cur = None
        for line in open(f, encoding='utf-8'):
            mm = re.match(r'^(\w+)::?\s*$', line)
            if mm: cur = mm.group(1); scripts[cur] = []; continue
            if cur: scripts[cur].append(line.strip())
    return scripts

def main():
    groups = json.load(open(EM + '/data/maps/map_groups.json'))
    maps = [m for g in groups['group_order'] for m in groups[g] if not EXCLUDE.match(m)]
    newname = lambda m: RENAME.get(m, m)
    em_map_ids = {}
    for m in maps:
        em_map_ids[json.load(open(f'{EM}/data/maps/{m}/map.json'))['id']] = m
    def map_const(emid):
        if emid in ('MAP_DYNAMIC', 'MAP_UNDEFINED'): return emid
        m = em_map_ids.get(emid)
        if m is None: return None
        return RENAME_ID.get(emid, emid)
    frgfx = fr_defs(FR + '/include/constants/event_objects.h', 'OBJ_EVENT_GFX_')
    frmus = fr_defs(FR + '/include/constants/songs.h', 'MUS_')
    frsec = set(re.findall(r'(MAPSEC_\w+)', open(FR + '/include/constants/region_map_sections.h').read()))
    frflag = fr_defs(FR + '/include/constants/flags.h', 'FLAG_')
    frmove = fr_defs(FR + '/include/constants/event_object_movement.h', 'MOVEMENT_TYPE_')
    def movement(mt):
        if mt in frmove: return mt
        for cand in (mt.replace('WALK_SLOWLY_IN_PLACE', 'WALK_IN_PLACE'), mt.replace('JOG_IN_PLACE', 'WALK_IN_PLACE'), mt.replace('RUN_IN_PLACE', 'WALK_IN_PLACE')):
            if cand in frmove: return cand
        return 'MOVEMENT_TYPE_FACE_DOWN'
    frscene = set(re.findall(r'(MAP_BATTLE_SCENE_\w+)', open(FR + '/include/constants/map_types.h').read()))
    tm_alias = {}
    for n in re.findall(r'#define (ITEM_(?:TM|HM)\d+_\w+) ', open(FR + '/include/constants/items.h').read()):
        kind, rest = n.split('_')[1], n.split('_', 2)[2]
        tm_alias['ITEM_%s_%s' % (kind[:2], rest)] = n
    texts, scripts = em_texts(), em_scripts()
    # layouts
    lays = json.load(open(EM + '/data/layouts/layouts.json'))['layouts']
    lay_by_id = {l['id']: l for l in lays if l}
    used_layouts, used_tilesets = [], []
    stats = collections.Counter()
    out_texts = {}
    for m in maps:
        j = json.load(open(f'{EM}/data/maps/{m}/map.json'))
        if j['layout'] not in used_layouts: used_layouts.append(j['layout'])
    frlays = json.load(open(FR + '/data/layouts/layouts.json'))
    frlays['layouts'] = [l for l in frlays['layouts'] if not (l and l.get('id', '').startswith('LAYOUT_HOENN_'))]
    for lid in used_layouts:
        l = lay_by_id[lid]
        name = 'Hoenn' + l['name'].replace('_Layout', '')
        d = f'data/layouts/{name}'
        os.makedirs(FR + '/' + d, exist_ok=True)
        shutil.copy(f"{EM}/{l['blockdata_filepath']}", f'{FR}/{d}/map.bin')
        shutil.copy(f"{EM}/{l['border_filepath']}", f'{FR}/{d}/border.bin')
        for ts in (l['primary_tileset'], l['secondary_tileset']):
            t = ts.replace('gTileset_', '')
            if t not in used_tilesets: used_tilesets.append(t)
        frlays['layouts'].append({'id': 'LAYOUT_HOENN_' + lid[len('LAYOUT_'):], 'name': name + '_Layout', 'width': l['width'], 'height': l['height'],
                                  'border_width': l.get('border_width', 2), 'border_height': l.get('border_height', 2),
                                  'primary_tileset': 'gTileset_Em' + l['primary_tileset'][len('gTileset_'):],
                                  'secondary_tileset': 'gTileset_Em' + l['secondary_tileset'][len('gTileset_'):],
                                  'border_filepath': f'{d}/border.bin', 'blockdata_filepath': f'{d}/map.bin'})
    open(FR + '/data/layouts/layouts.json', 'w').write(json.dumps(frlays, indent=2, ensure_ascii=False) + '\n')
    import_tilesets.main(used_tilesets)
    # maps
    frgroups = json.load(open(FR + '/data/maps/map_groups.json'))
    for g in list(frgroups['group_order']):
        if g.startswith('gMapGroup_Hoenn'):
            frgroups['group_order'].remove(g); del frgroups[g]
    frgroups['connections_include_order'] = [m for m in frgroups['connections_include_order'] if not os.path.exists(f'{FR}/data/maps/{m}/.hoenn')]
    for g in groups['group_order']:
        ng = 'gMapGroup_Hoenn' + g[len('gMapGroup_'):]
        ms = [newname(m) for m in groups[g] if not EXCLUDE.match(m)]
        if not ms: continue
        frgroups['group_order'].append(ng); frgroups[ng] = ms
    for m in maps:
        j = json.load(open(f'{EM}/data/maps/{m}/map.json'))
        nm = newname(m)
        src = j
        if 'shared_events_map' in j:
            src = json.load(open(f"{EM}/data/maps/{j['shared_events_map']}/map.json"))
        out = {'id': map_const(j['id']), 'name': nm, 'layout': 'LAYOUT_HOENN_' + j['layout'][len('LAYOUT_'):],
               'music': j['music'] if j['music'] in frmus else MUSIC.get(j['map_type'], 'MUS_ROUTE1'),
               'region_map_section': j['region_map_section'] if j['region_map_section'] in frsec else MAPSEC_FALLBACK.get(j['region_map_section'], 'MAPSEC_NONE'),
               'requires_flash': j.get('requires_flash', False), 'weather': j['weather'], 'map_type': j['map_type'],
               'allow_cycling': j.get('allow_cycling', True), 'allow_escaping': j.get('allow_escaping', False),
               'allow_running': j.get('allow_running', True), 'show_map_name': j.get('show_map_name', True),
               'floor_number': j.get('floor_number', 0), 'battle_scene': j.get('battle_scene', 'MAP_BATTLE_SCENE_NORMAL') if j.get('battle_scene') in frscene else 'MAP_BATTLE_SCENE_NORMAL'}
        conns = []
        for c in j.get('connections') or []:
            t = map_const(c['map'])
            if t: conns.append({'map': t, 'offset': c['offset'], 'direction': c['direction']})
        out['connections'] = conns or None
        sc_lines = [f'{nm}_MapScripts::', '\t.byte 0', '']; tx_labels = []
        def script_for(label, kind):
            """Returns a new script label for an Emerald script, or None"""
            body = scripts.get(label, [])
            # Pokémon Center nurse
            if any('Common_EventScript_PkmnCenterNurse' in b for b in body):
                return 'EventScript_PkmnCenterNurse'
            # mart
            mart = next((b.split()[1] for b in body if b.startswith('pokemart ')), None)
            new = f'{nm}_EventScript_H{len(tx_labels)}'
            if mart and mart in scripts:
                items = [b for b in scripts[mart] if b.startswith('.2byte')]
                items = ['.2byte ' + tm_alias.get(b.split()[1], b.split()[1]) for b in items]
                sc_lines.extend([f'{new}::', '\tlock', '\tfaceplayer', '\tmessage Text_MayIHelpYou', '\twaitmessage', f'\tpokemart {new}_Items',
                                 '\tmsgbox Text_PleaseComeAgain', '\trelease', '\tend', '', '\t.align 2', f'{new}_Items::']
                                + ['\t' + b for b in items] + ['\trelease', '\tend', ''])
                tx_labels.append(new); stats['mart'] += 1
                return new
            # first message the script shows
            for b in body:
                mm = re.match(r'msgbox (\w+)', b) or re.match(r'message (\w+)', b)
                if mm and mm.group(1) in texts:
                    t = f'{nm}_Text_H{len(tx_labels)}'
                    out_texts[t] = texts[mm.group(1)]
                    box = 'MSGBOX_SIGN' if kind == 'sign' else 'MSGBOX_NPC'
                    sc_lines.extend([f'{new}::', f'\tmsgbox {t}, {box}', '\tend', ''])
                    tx_labels.append(new); stats['text'] += 1
                    return new
            stats['noscript'] += 1
            return None
        objs = []
        for o in src.get('object_events', []):
            if o.get('type', 'object') != 'object': continue
            if o.get('flag', '0') not in ('0', ''):
                stats['hidden_obj'] += 1; continue
            g = o['graphics_id']
            if g not in frgfx:
                g = GFX.get(g, GFX_DEFAULT)
            s = script_for(o['script'], 'npc') if o['script'] not in ('0x0', '0', '') else None
            objs.append({'type': 'object', 'graphics_id': g, 'x': o['x'], 'y': o['y'], 'elevation': o['elevation'],
                         'movement_type': movement(o['movement_type']), 'movement_range_x': o['movement_range_x'], 'movement_range_y': o['movement_range_y'],
                         'trainer_type': 'TRAINER_TYPE_NONE', 'trainer_sight_or_berry_tree_id': '0', 'script': s or '0x0', 'flag': '0'})
        out['object_events'] = objs
        warps = []
        for w in src.get('warp_events', []):
            t = map_const(w['dest_map'])
            if t is None: t = 'MAP_DYNAMIC'; stats['warp_dropped'] += 1
            warps.append({'x': w['x'], 'y': w['y'], 'elevation': w['elevation'], 'dest_map': t, 'dest_warp_id': str(w['dest_warp_id'])})
        out['warp_events'] = warps
        out['coord_events'] = []
        bgs = []
        for b in src.get('bg_events', []):
            if b.get('type') != 'sign': continue
            s = script_for(b['script'], 'sign')
            if s:
                bgs.append({'type': 'sign', 'x': b['x'], 'y': b['y'], 'elevation': b['elevation'], 'player_facing_dir': b['player_facing_dir'], 'script': s})
        out['bg_events'] = bgs
        d = f'{FR}/data/maps/{nm}'
        os.makedirs(d, exist_ok=True)
        open(d + '/.hoenn', 'w').write('imported from pokeemerald\n')
        open(d + '/map.json', 'w').write(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
        open(d + '/scripts.inc', 'w').write('\n'.join(sc_lines) + '\n')
        tx = ''.join(f'{k}::\n' + '\n'.join(v) + '\n\n' for k, v in out_texts.items() if k.startswith(nm + '_Text_H'))
        open(d + '/text.inc', 'w').write(tx)
        if out['connections']: frgroups['connections_include_order'].append(nm)
        stats['maps'] += 1
    open(FR + '/data/maps/map_groups.json', 'w').write(json.dumps(frgroups, indent=2, ensure_ascii=False) + '\n')
    names = [newname(m) for m in maps]
    open(FR + '/data/maps/hoenn_scripts.inc', 'w').write('@ Maps imported from pokeemerald (Hoenn)\n' + ''.join(f'\t.include "data/maps/{n}/scripts.inc"\n' for n in names))
    open(FR + '/data/maps/hoenn_text.inc', 'w').write('@ Maps imported from pokeemerald (Hoenn)\n' + ''.join(f'\t.include "data/maps/{n}/text.inc"\n' for n in names))
    print(dict(stats))
    return maps

if __name__ == '__main__':
    main()
