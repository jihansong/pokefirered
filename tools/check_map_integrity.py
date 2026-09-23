#!/usr/bin/env python3
"""check_map_integrity.py [--upstream-ref upstream/master] [--no-upstream] [--limit N] [--no-fail]

Static checks over the map data and the flag/var constants. Read-only.

  warps       warp events and scripted warps to a map that does not exist, or to a
              warp id the destination does not have (WARP_ID_DYNAMIC is skipped);
              warps whose destination does not lead back are counted (INFO: holes,
              one-way doors and several doors into one room are normal); a warp
              event on a tile whose behavior does not warp is INFO when retail has
              the same warp there (holes, cave mouths, script-opened doors) and
              WARN when this project added the warp, because our own doors are
              meant to work (this is how the v0.6.0 airport door was found)
  connections map connections to unknown maps; connections the other map does not
              mirror (opposite direction, negated offset)
  flags/vars  #define values that share a number. An explicit alias
              (#define A B) or a pair that upstream pret/pokefirered already has is
              reported as INFO; a name that looks free (FLAG_0xNNN, FLAG_UNUSED_*,
              VAR_0xNNNN) sharing a number with a used one, or two used names
              sharing one, is an ERROR. Trainer "defeated" flags
              (TRAINER_FLAGS_START + id) and var ranges written in comments
              ("0x4094-0x40A7", "array of 4") are included.
  obj flags   object-event / hidden-item flags used on more than one map. Item
              balls or hidden items sharing a flag are ERRORs; other shared hide
              flags are WARN, or INFO when upstream shares them the same way.
              FLAG_TEMP_* is ignored.
  movement    objects whose movement type has a NULL callback in
              src/event_object_movement.c (the sprite callback is called every
              frame, so the game crashes/resets when the object is loaded)
  trainers    trainer ids battled on several maps (shared defeat flag), Hoenn
              trainer ids past the hoennTrainerFlags capacity
  layouts     map.json layouts missing from layouts.json; groups over 255 maps

Exit status 1 when there is an ERROR (0 with --no-fail).
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapdata_common as C  # noqa: E402

FLAG_HEADERS = ['include/constants/opponents.h', 'include/constants/flags.h',
                'include/constants/flags_hoenn.h', 'include/constants/flags_hoenn_map.h']
VAR_HEADERS = ['include/constants/vars.h']
FREE_RE = re.compile(r'^(FLAG_0x[0-9A-Fa-f]+|FLAG_UNUSED_\w+|VAR_0x[0-9A-Fa-f]+|VAR_UNUSED_\w+|FLAG_SPECIAL_FLAG_0x\w+)$')
MARKER_RE = re.compile(r'(_START|_END|_COUNT|_USED)$|^(SYS_FLAGS|TEMP_FLAGS|VARS_START|SPECIAL_VARS)')


class Report:
    def __init__(self, limit):
        self.items = collections.defaultdict(list)  # section -> [(level, text)]
        self.limit = limit

    def add(self, section, level, text):
        self.items[section].append((level, text))

    def count(self, level):
        return sum(1 for v in self.items.values() for lv, _ in v if lv == level)

    def write(self, out):
        out.write(f'# check_map_integrity: {self.count("ERROR")} ERROR, {self.count("WARN")} WARN, '
                  f'{self.count("INFO")} INFO\n')
        for section, entries in self.items.items():
            c = collections.Counter(lv for lv, _ in entries)
            out.write(f'\n## {section} ({", ".join(f"{k} {v}" for k, v in sorted(c.items()))})\n\n')
            shown = collections.Counter()
            for lv, text in sorted(entries, key=lambda e: ('ERROR', 'WARN', 'INFO', 'NOTE').index(e[0])):
                shown[lv] += 1
                if self.limit and shown[lv] > self.limit:
                    if shown[lv] == self.limit + 1:
                        out.write(f'- {lv}: ... {c[lv] - self.limit} more (use --limit 0)\n')
                    continue
                out.write(f'- {lv}: {text}\n')


def retail_warp_tiles(name):
    """The (x, y) of every warp retail FR/LG has on this map, or None when the map is ours."""
    raw = C.git_show('upstream/master', f'data/maps/{name}/map.json')
    if raw is None:
        return set()  # a map this project added: none of its warps come from retail
    try:
        return {(w['x'], w['y']) for w in (json.loads(raw).get('warp_events') or [])}
    except (ValueError, KeyError):
        return None


def check_warps(maps, ids, scripts, rep):
    for name, d in maps.items():
        for i, w in enumerate(d.get('warp_events') or []):
            dm, wid = w['dest_map'], str(w['dest_warp_id'])
            if dm in ('MAP_DYNAMIC', 'MAP_UNDEFINED'):
                continue
            t = ids.get(dm)
            if t is None:
                rep.add('warps', 'ERROR', f'{name} warp {i} ({w["x"]},{w["y"]}) -> unknown map {dm}')
                continue
            if not wid.isdigit():
                continue
            tw = maps[t].get('warp_events') or []
            k = int(wid)
            if k >= len(tw):
                rep.add('warps', 'ERROR', f'{name} warp {i} ({w["x"]},{w["y"]}) -> {t} warp id {k}, which has {len(tw)} warps')
                continue
            back = tw[k]
            if back['dest_map'] in ('MAP_DYNAMIC', 'MAP_UNDEFINED') or not str(back['dest_warp_id']).isdigit():
                continue
            if ids.get(back['dest_map']) != name:
                rep.add('warps', 'INFO', f'{name} warp {i} -> {t} warp {k}, which leads to {back["dest_map"]} (not back)')
    # warp events on tiles that are not warp tiles: they only work once a script
    # swaps the metatile (E4 doors, TERRA CAVE, ALTERING CAVE...), or never
    mt = C.Metatiles()
    inert = collections.defaultdict(list)
    ours = collections.defaultdict(list)
    for name, d in maps.items():
        retail = retail_warp_tiles(name)
        for i, w in enumerate(d.get('warp_events') or []):
            if mt.warp_is_live(d, w) is not False:
                continue
            entry = (f'{i} ({w["x"]},{w["y"]})->{w["dest_map"].replace("MAP_", "")}'
                     f' [{mt.mb_name.get(mt.behavior(d["layout"], w["x"], w["y"]), "?")}]')
            # A door this project put on the map is meant to work. Retail's own dead
            # warp tiles are the normal kind (holes, cave mouths, doors a script opens).
            if retail is not None and (w['x'], w['y']) not in retail and not d['_hoenn']:
                ours[name].append(entry)
            else:
                inert[name].append(entry)
    for name, lst in sorted(ours.items()):
        rep.add('inert warps', 'WARN', f'{name}: warp we added sits on a tile that does not warp: {", ".join(lst)}')
    for name, lst in sorted(inert.items()):
        region = 'Hoenn' if maps[name]['_hoenn'] else 'Kanto'
        rep.add('inert warps', 'INFO', f'{region} {name}: {", ".join(lst)}')
    rep.add('inert warps', 'NOTE', f'warp events on a non-warp tile: {sum(len(v) for v in inert.values())} on {len(inert)} maps '
            f'(Hoenn {sum(len(v) for n, v in inert.items() if maps[n]["_hoenn"])}); most are arrival-only spots or '
            'entrances a script opens')
    # scripted warps
    for lab, info in scripts.labels.items():
        for cmd, target, line in info['warps']:
            if target in ('MAP_DYNAMIC', 'MAP_UNDEFINED') or not target.startswith('MAP_'):
                continue
            t = ids.get(target)
            if t is None:
                rep.add('warps', 'ERROR', f'{info["file"]}:{line} {cmd} to unknown map {target}')


def check_connections(maps, ids, rep, upstream_ref):
    def upstream_same(name, c):
        t = C.git_show(upstream_ref, f'data/maps/{name}/map.json') if upstream_ref else None
        return bool(t) and c in (json.loads(t).get('connections') or [])

    for name, d in maps.items():
        for c in d.get('connections') or []:
            t = ids.get(c['map'])
            if t is None:
                rep.add('connections', 'ERROR', f'{name} {c["direction"]} -> unknown map {c["map"]}')
                continue
            want = C.CONNECTION_OPPOSITE[c['direction']]
            back = [b for b in maps[t].get('connections') or [] if ids.get(b['map']) == name and b['direction'] == want]
            msg = None
            if not back:
                msg = f'{name} --{c["direction"]}--> {t}: {t} has no {want} connection back'
            elif c['direction'] not in ('dive', 'emerge') and all(int(b['offset']) != -int(c['offset']) for b in back):
                msg = (f'{name} --{c["direction"]} offset {c["offset"]}--> {t}: '
                       f'back offset {back[0]["offset"]} (expected {-int(c["offset"])})')
            if msg:
                if upstream_same(name, c):
                    rep.add('connections', 'INFO', msg + ' (same in upstream)')
                else:
                    rep.add('connections', 'WARN', msg)


def comment_ranges(ev, names):
    """Extra (name, value) pairs for ranges written in comments."""
    extra = []
    for n in names:
        v = ev.value(n)
        cm = ev.comment.get(n, '')
        if v is None or not cm:
            continue
        m = re.search(r'0x([0-9A-Fa-f]+)\s*-\s*0x([0-9A-Fa-f]+)', cm)
        if m and int(m.group(1), 16) == v:
            for x in range(v + 1, int(m.group(2), 16) + 1):
                extra.append((f'{n}[+{x - v}]', x))
        m = re.search(r'array of (\d+)', cm)
        if m:
            for x in range(1, int(m.group(1))):
                extra.append((f'{n}[+{x}]', v + x))
    return extra


def number_check(section, ev, prefix, rep, upstream_ev, extra=(), free_range=None):
    names = [n for n in ev.order if n.startswith(prefix) and not (prefix == 'FLAG_' and MARKER_RE.search(n))]
    byval = collections.defaultdict(list)
    for n in dict.fromkeys(names):
        v = ev.value(n)
        if v is not None and v != 0:
            byval[v].append(n)
    for n, v in extra:
        byval[v].append(n)
    free_total, free_taken = 0, 0
    for v, ns in sorted(byval.items()):
        def is_free(n):
            return FREE_RE.match(n) and (free_range is None or v in free_range)
        free = [n for n in ns if is_free(n)]
        used = [n for n in ns if not is_free(n)]
        free_total += len(free) > 0
        if len(ns) < 2:
            continue
        where = ', '.join(f'{n} ({ev.origin[n][0].split("/")[-1]}:{ev.origin[n][1]})' if n in ev.origin else n for n in ns)
        if free and used:
            free_taken += 1
            rep.add(section, 'ERROR', f'0x{v:X}: "free" {", ".join(free)} is in use by {", ".join(used)} -- {where}')
            continue
        if not used:
            continue
        explicit = all(any(ev.raw.get(a) == b or ev.raw.get(b) == a for b in used if b != a) for a in used)
        if explicit:
            rep.add(section, 'INFO', f'0x{v:X}: explicit alias {where}')
            continue
        if upstream_ev is not None:
            same = [n for n in used if upstream_ev.value(n) == v]
            if len(same) == len(used):
                rep.add(section, 'INFO', f'0x{v:X}: upstream alias {where}')
                continue
        rep.add(section, 'ERROR', f'0x{v:X}: {where}')
    return free_total - free_taken


def check_numbers(rep, upstream_ref):
    fl = C.ConstEval(FLAG_HEADERS)
    up_fl = None
    if upstream_ref:
        texts = {p: C.git_show(upstream_ref, p) for p in FLAG_HEADERS}
        if texts['include/constants/flags.h']:
            up_fl = C.ConstEval(FLAG_HEADERS, {p: t or '' for p, t in texts.items()})
    # trainer "defeated" flags live at TRAINER_FLAGS_START + id (FR/LG ids only;
    # Hoenn trainers use gSaveBlock2Ptr->hoennTrainerFlags)
    tstart, tmax = fl.value('TRAINER_FLAGS_START'), fl.value('MAX_TRAINERS_COUNT')
    extra = []
    for n in fl.order:
        if n.startswith('TRAINER_') and not n.startswith('TRAINER_HOENN_') and not MARKER_RE.search(n):
            v = fl.value(n)
            if v is not None and 0 <= v < (tmax or 0) and fl.origin[n][0].endswith('opponents.h'):
                extra.append((f'trainer flag of {n}', tstart + v))
    free_flags = number_check('flag numbers', fl, 'FLAG_', rep, up_fl, extra)
    vr = C.ConstEval(VAR_HEADERS)
    up_vr = None
    if upstream_ref:
        t = C.git_show(upstream_ref, VAR_HEADERS[0])
        if t:
            up_vr = C.ConstEval(VAR_HEADERS, {VAR_HEADERS[0]: t})
    var_names = [n for n in vr.order if n.startswith('VAR_')]
    # VAR_0x8000.. are the special (scratch) vars, not free save vars
    free_vars = number_check('var numbers', vr, 'VAR_', rep, up_vr, comment_ranges(vr, var_names),
                             free_range=range(0x4000, 0x4100))
    rep.add('flag numbers', 'NOTE', f'flags named free (FLAG_0x*/FLAG_UNUSED_*) that nothing else shares: {free_flags}')
    rep.add('var numbers', 'NOTE', f'save vars named free (VAR_0x40xx) that nothing else shares: {free_vars}')
    # Hoenn flag block capacity
    hs, hc = fl.value('HOENN_FLAGS_START'), fl.value('HOENN_FLAGS_COUNT')
    if hs is not None and hc:
        hv = [fl.value(n) for n in fl.order if n.startswith('FLAG_HOENN_')]
        hv = [v - hs for v in hv if v is not None and hs <= v < hs + 0x10000]
        over = [v for v in hv if v >= hc]
        rep.add('flag numbers', 'ERROR' if over else 'NOTE',
                f'hoennFlags: {len(hv)} named Hoenn-block flags, highest offset 0x{max(hv):X} of 0x{hc:X}'
                + (f'; {len(over)} past the block' if over else ''))
    return fl


def check_object_flags(maps, fl, rep, upstream_ref):
    uses = collections.defaultdict(list)
    for name, d in maps.items():
        for i, o in enumerate(d.get('object_events') or [], 1):
            f = str(o.get('flag', '0'))
            if f not in ('0', '', '0x0'):
                kind = 'item' if o.get('graphics_id') == 'OBJ_EVENT_GFX_ITEM_BALL' else 'obj'
                uses[f].append((name, kind, f'obj {i}'))
        for b in d.get('bg_events') or []:
            if b.get('type') == 'hidden_item':
                uses[b['flag']].append((name, 'hidden', f'hidden ({b["x"]},{b["y"]})'))
    # the same flag number under two names counts as the same flag
    bynum = collections.defaultdict(list)
    for f, lst in uses.items():
        v = fl.value(f) if not f.isdigit() else int(f)
        bynum[v if v is not None else f].extend((f,) + x for x in lst)
    up_cache = {}

    def upstream_flags(m):
        if m not in up_cache:
            t = C.git_show(upstream_ref, f'data/maps/{m}/map.json') if upstream_ref else None
            up_cache[m] = {str(o.get('flag')) for o in json.loads(t).get('object_events') or []} if t else None
        return up_cache[m]
    for key, lst in bynum.items():
        mapset = {x[1] for x in lst}
        names = sorted({x[0] for x in lst})
        if any(n.startswith('FLAG_TEMP_') for n in names):
            continue
        kinds = {x[2] for x in lst}
        desc = '; '.join(f'{m} {w} [{f}]' for f, m, k, w in lst)
        if ('item' in kinds or 'hidden' in kinds) and len(lst) > 1:
            rep.add('object/hidden-item flags', 'ERROR', f'{names}: pickup flag shared by {len(lst)} events: {desc}')
            continue
        if len(mapset) < 2:
            continue
        if upstream_ref and all((upstream_flags(m) or set()) & set(names) for m in mapset):
            rep.add('object/hidden-item flags', 'INFO', f'{names} on {len(mapset)} maps (as upstream): {", ".join(sorted(mapset))}')
        else:
            rep.add('object/hidden-item flags', 'WARN', f'{names} hides objects on {len(mapset)} maps: {", ".join(sorted(mapset))}')


def check_movement(maps, rep):
    src = open(C.rel('src/event_object_movement.c')).read()
    m = re.search(r'sMovementTypeCallbacks\[[^\]]*\]\)\(struct Sprite \*\) = \{(.*?)\n\};', src, re.S)
    nulls = set(re.findall(r'\[(MOVEMENT_TYPE_\w+)\]\s*=\s*NULL', m.group(1))) if m else set()
    per = collections.defaultdict(list)
    for name, d in maps.items():
        for i, o in enumerate(d.get('object_events') or [], 1):
            if o.get('movement_type') in nulls:
                per[(o['movement_type'], name)].append(f'{i}@({o["x"]},{o["y"]})')
    total = sum(len(v) for v in per.values())
    for (mt, name), objs in sorted(per.items()):
        rep.add('movement types', 'ERROR', f'{name}: {len(objs)} object(s) with {mt} (NULL callback): {", ".join(objs)}')
    if nulls:
        rep.add('movement types', 'NOTE', f'NULL callbacks: {", ".join(sorted(nulls))}; objects using them: {total}')


def check_trainers(maps, scripts, fl, rep):
    by = collections.defaultdict(set)
    for name, d in maps.items():
        for lab in scripts.map_labels.get(name, []):
            info = scripts.labels[lab]
            text = open(C.rel(info['file']), encoding='utf-8', errors='replace').read().splitlines()
            for ln in text[info['line']:]:
                if C.LABEL_RE.match(ln):
                    break
                mm = re.match(r'\s*trainerbattle_?\w*\s+(TRAINER_\w+)', ln)
                if mm:
                    by[mm.group(1)].add(name)
    for t, ms in sorted(by.items()):
        if len(ms) > 1:
            rep.add('trainers', 'INFO', f'{t} battled on {len(ms)} maps (one defeat flag): {", ".join(sorted(ms))}')
    hs = fl.value('HOENN_TRAINERS_START')
    ids = [fl.value(n) for n in fl.order if n.startswith('TRAINER_HOENN_')]
    ids = [v for v in ids if v is not None]
    src = open(C.rel('include/global.h')).read()
    m = re.search(r'u8 hoennTrainerFlags\[(0x[0-9A-Fa-f]+|\d+)\]', src)
    cap = int(m.group(1), 0) * 8 if m else None
    if ids and hs is not None and cap:
        hi = max(ids) - hs
        rep.add('trainers', 'ERROR' if hi >= cap else 'NOTE',
                f'Hoenn trainers: {len(ids)} ids, highest offset {hi}, hoennTrainerFlags holds {cap} bits ({cap - hi - 1} free after the last)')
    nt, mx = fl.value('NUM_TRAINERS'), fl.value('MAX_TRAINERS_COUNT')
    if nt is not None and mx is not None:
        rep.add('trainers', 'ERROR' if nt > mx else 'NOTE', f'FR/LG trainers: NUM_TRAINERS {nt} of MAX_TRAINERS_COUNT {mx} ({mx - nt} free)')


def check_layouts(maps, rep):
    lays = {l['id'] for l in json.load(open(C.rel('data/layouts/layouts.json')))['layouts'] if l}
    for name, d in maps.items():
        if d['layout'] not in lays:
            rep.add('layouts/groups', 'ERROR', f'{name}: layout {d["layout"]} not in layouts.json')
    groups = C.load_groups()
    for g in groups['group_order']:
        if len(groups[g]) > 255:
            rep.add('layouts/groups', 'ERROR', f'{g} has {len(groups[g])} maps (max 255)')
    rep.add('layouts/groups', 'NOTE', f'{len(maps)} maps in {len(groups["group_order"])} groups, {len(lays)} layouts')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--upstream-ref', default='upstream/master')
    ap.add_argument('--no-upstream', action='store_true')
    ap.add_argument('--limit', type=int, default=40, help='entries shown per level and section (0 = all)')
    ap.add_argument('--no-fail', action='store_true')
    ap.add_argument('--out')
    a = ap.parse_args()
    ref = None if a.no_upstream else a.upstream_ref
    if ref and C.git_show(ref, 'include/constants/flags.h') is None:
        print(f'note: {ref} not available, upstream comparison skipped', file=sys.stderr)
        ref = None
    maps, _ = C.load_maps()
    ids = C.map_ids(maps)
    scripts = C.ScriptIndex(maps)
    rep = Report(a.limit)
    check_warps(maps, ids, scripts, rep)
    check_connections(maps, ids, rep, ref)
    fl = check_numbers(rep, ref)
    check_object_flags(maps, fl, rep, ref)
    check_movement(maps, rep)
    check_trainers(maps, scripts, fl, rep)
    check_layouts(maps, rep)
    out = open(a.out, 'w') if a.out else sys.stdout
    rep.write(out)
    sys.exit(1 if rep.count('ERROR') and not a.no_fail else 0)


if __name__ == '__main__':
    main()
