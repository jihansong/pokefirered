#!/usr/bin/env python3
"""port_events.py <MapName> [--objects] [--bg] [--coord] [--scripts] [--check-only]

Ports one imported Hoenn map's event machinery from pokeemerald into a patch
under tools/hoenn_import/patches/. The maps came across byte for byte, so
Emerald's coordinates, metatile ids and script logic all still apply; what does
not come across is its text, which this tool deliberately leaves behind (every
_Text_ label is dropped, to be written fresh).

Identifiers are renamed through port_renames.json, and every FLAG_/VAR_/ITEM_/
METATILE_/SPECIES_/MOVE_/TRAINER_/SE_/MUS_ name in the result is checked
against this project's headers with cpp, so a name that does not exist here is
reported instead of silently breaking the build.
"""
import argparse, json, os, re, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EM = '/root/src/pokeemerald'
P = os.path.join(R, 'tools/hoenn_import/patches')
RENAMES = json.load(open(os.path.join(R, 'tools/hoenn_import/port_renames.json')))
HDRS = ['constants/flags.h', 'constants/vars.h', 'constants/items.h', 'constants/species.h',
        'constants/moves.h', 'constants/opponents.h', 'constants/songs.h', 'constants/metatile_labels.h',
        'constants/event_objects.h', 'constants/map_groups.h', 'constants/event_object_movement.h', 'constants/map_scripts.h', 'constants/trainer_types.h']
TOKEN = re.compile(r'\b(FLAG_[A-Z0-9_]+|VAR_[A-Z0-9_]+|ITEM_[A-Z0-9_]+|SPECIES_[A-Z0-9_]+|MOVE_[A-Z0-9_]+'
                   r'|TRAINER_[A-Z0-9_]+|SE_[A-Z0-9_]+|MUS_[A-Z0-9_]+|METATILE_[A-Za-z0-9_]+'
                   r'|OBJ_EVENT_GFX_[A-Z0-9_]+|MAP_[A-Z0-9_]+|MULTI_[A-Z0-9_]+)\b')


def rename(text):
    for a, b in RENAMES.get('exact', {}).items():
        text = re.sub(r'\b%s\b' % re.escape(a), b, text)
    for pat, repl in RENAMES.get('regex', []):
        text = re.sub(pat, repl, text)
    return text


def drop_lines(text):
    out = []
    for line in text.split('\n'):
        if any(re.search(p, line) for p in RENAMES.get('drop_lines', [])):
            continue
        out.append(line)
    return '\n'.join(out)


def strip_text_blocks(src):
    """Remove every <label>_Text_* block; Emerald's words are not carried over."""
    out, skip = [], False
    for line in src.split('\n'):
        m = re.match(r'^(\w+)::?$', line.strip())
        if m:
            skip = '_Text_' in m.group(1)
        if not skip:
            out.append(line)
    return '\n'.join(out)


def unknown_macros(script):
    """Script commands pokeemerald has that this project's macros do not."""
    ours = set()
    for f in ('asm/macros/event.inc', 'asm/macros/movement.inc', 'asm/macros/map.inc'):
        text = open(os.path.join(R, f)).read()
        ours |= set(re.findall(r'^\t\.macro (\w+)', text, re.M))
        ours |= set(re.findall(r'^\tcreate_movement_action (\w+)', text, re.M))
    ours |= {'.byte', '.2byte', '.4byte', '.string', '.include', '.align'}
    used = set()
    for line in script.split('\n'):
        m = re.match(r'\t(\.?\w+)', line)
        if m:
            used.add(m.group(1))
    return sorted(used - ours)


def unknown_labels(script):
    """Script labels the port refers to that neither it nor this project defines."""
    defined = set(re.findall(r'^(\w+)::?$', script, re.M))
    used = set(re.findall(r'\b((?:Common_)?(?:EventScript|Movement)_\w+)\b', script))
    used |= set(re.findall(r'\b(Common_Movement_\w+)\b', script))
    missing = []
    for lab in sorted(used - defined):
        found = subprocess.run(['grep', '-rqm1', '^%s::' % lab, os.path.join(R, 'data')],
                               capture_output=True)
        if found.returncode != 0:
            missing.append(lab)
    return missing


def unknown_names(text):
    names = sorted(set(TOKEN.findall(text)))
    if not names:
        return []
    src = ''.join('#include "%s"\n' % h for h in HDRS) + '\n'.join(names) + '\n'
    r = subprocess.run(['cpp', '-P', '-I', os.path.join(R, 'include'), '-I', R],
                       input=src, text=True, capture_output=True)
    bad = []
    for name, line in zip(names, [l for l in r.stdout.strip().split('\n') if l.strip()]):
        if name in line:            # cpp left it untouched: no such #define here
            bad.append(name)
    return bad


def is_defined(name):
    """True when this project's headers already #define the name."""
    src = ''.join('#include "%s"\n' % h for h in HDRS) + '#include "constants/map_event_ids.h"\n' + name + '\n'
    r = subprocess.run(['cpp', '-P', '-I', os.path.join(R, 'include'), '-I', R],
                       input=src, text=True, capture_output=True)
    out = [l for l in r.stdout.strip().split('\n') if l.strip()]
    return bool(out) and name not in out[-1]


def local_ids(name):
    """Emerald names some objects (local_id) and its scripts use those names.
    Our map.json has no names, so emit .equ lines, matching by tile so a dropped
    object cannot shift the numbering."""
    em = json.load(open(os.path.join(EM, 'data/maps', name, 'map.json')))
    ours = json.load(open(os.path.join(R, 'data/maps', name, 'map.json')))
    lines = []
    for ev in (em.get('object_events') or []):
        lid = ev.get('local_id')
        if not lid or not str(lid).startswith('LOCALID_'):
            continue
        if is_defined(lid):
            continue            # this project already defines it (map_event_ids.h)
        for i, o in enumerate(ours.get('object_events') or [], 1):
            if (o['x'], o['y']) == (ev['x'], ev['y']):
                lines.append('.equ %s, %d' % (lid, i))
                break
        else:
            sys.exit('%s: %s has no object at (%s,%s) here' % (name, lid, ev['x'], ev['y']))
    return ('\n'.join(lines) + '\n\n') if lines else ''


def port_scripts(name):
    """The map's scripts, minus its text and minus its MapScripts table (which
    the import already writes); the table's entries come back as a .mapscripts
    patch so apply_patches can splice them into the generated header."""
    src = open(os.path.join(EM, 'data/maps', name, 'scripts.inc')).read()
    body = drop_lines(rename(strip_text_blocks(src)))
    table = ''
    m = re.search(r'^%s_MapScripts::\n((?:\tmap_script .*\n)*)\t\.byte 0\n' % name, body, re.M)
    if m:
        table = m.group(1)
        body = body[:m.start()] + body[m.end():]
    body = re.sub(r'\n{3,}', '\n\n', body).strip() + '\n'
    return body, table


def port_events(name, keys):
    em = json.load(open(os.path.join(EM, 'data/maps', name, 'map.json')))
    ours = json.load(open(os.path.join(R, 'data/maps', name, 'map.json')))
    out = {}
    for key in keys:
        items, overrides, obj_overrides, coord_overrides = [], [], [], []
        taken = {(e.get('x'), e.get('y')): e for e in (ours.get(key) or [])}
        for ev in (em.get(key) or []):
            here = taken.get((ev.get('x'), ev.get('y')))
            if here is not None:
                # the import brought a sign across at this tile but pointed it at
                # its own stub script; point it back at the ported one
                lid = ev.get('local_id')
                if lid and str(lid).startswith('LOCALID_') and here.get('local_id') != lid:
                    obj_overrides.append({'x': ev['x'], 'y': ev['y'], 'local_id': lid})
                want = rename(ev['script']) if ev.get('script') else None
                # the import writes its own scripts for item balls and hidden
                # items, with this project's flags; leave those alone
                if here.get('script', '').split('_EventScript_')[-1].startswith(('HItem', 'Item')):
                    want = None
                if want and here.get('script') != want:
                    if key == 'bg_events':
                        overrides.append({'x': ev['x'], 'y': ev['y'], 'script': want})
                    elif key == 'object_events':
                        obj_overrides.append({'x': ev['x'], 'y': ev['y'], 'script': want})
                    elif key == 'coord_events':
                        coord_overrides.append({'x': ev['x'], 'y': ev['y'], 'script': want})
                continue
            ev = dict(ev)
            for f in ('script', 'flag', 'var', 'graphics_id', 'trainer_type', 'movement_type'):
                if f in ev and isinstance(ev[f], str):
                    ev[f] = rename(ev[f])
            items.append(ev)
        if items:
            out[key] = items
        if overrides:
            out['bg_overrides'] = out.get('bg_overrides', []) + overrides
        if obj_overrides:
            out['object_overrides'] = out.get('object_overrides', []) + obj_overrides
        if coord_overrides:
            out['coord_overrides'] = out.get('coord_overrides', []) + coord_overrides
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--objects', action='store_true')
    ap.add_argument('--bg', action='store_true')
    ap.add_argument('--coord', action='store_true')
    ap.add_argument('--scripts', action='store_true')
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    name = a.map
    scripts, table = port_scripts(name) if a.scripts else ('', '')
    keys = [k for k, on in (('object_events', a.objects), ('bg_events', a.bg), ('coord_events', a.coord)) if on]
    events = port_events(name, keys) if keys else {}
    blob = scripts + json.dumps(events)
    bad = unknown_names(blob) + unknown_macros(scripts) + unknown_labels(scripts)
    if bad:
        print('names this project does not define (%d):' % len(bad))
        for b in bad:
            print('  ', b)
    if a.check_only:
        return 1 if bad else 0
    if bad:
        sys.exit('refusing to write a patch with undefined names; add them to port_renames.json first')
    if table:
        p = os.path.join(P, name + '.mapscripts')
        open(p, 'w').write(table)
        print('wrote', os.path.relpath(p, R))
    if scripts:
        p = os.path.join(P, name + '.scripts.inc')
        open(p, 'w').write('@ Ported from pokeemerald (the map data is identical), text written fresh.\n' + scripts)
        print('wrote', os.path.relpath(p, R))
    if keys:
        p = os.path.join(P, name + '.json')
        cur = json.load(open(p)) if os.path.exists(p) else {}
        for k in keys + ['bg_overrides', 'object_overrides', 'coord_overrides']:
            cur.pop(k, None)      # drop what a previous run of this tool wrote
        cur.update(events)
        if not cur:
            if os.path.exists(p):
                os.remove(p)
                print('removed', os.path.relpath(p, R))
            return
        open(p, 'w').write(json.dumps(cur, indent=2, ensure_ascii=False) + '\n')
        print('wrote', os.path.relpath(p, R))


if __name__ == '__main__':
    sys.exit(main())
