#!/usr/bin/env python3
"""apply_patches.py [map ...]

Copies tools/hoenn_import/patches/<Map>.{json,scripts.inc,text.inc} into the
imported maps under data/maps. The import scripts do the same thing at the end
of a re-import; this applies a patch on its own while the story is being
written, and can be run again after editing one.

The appended parts sit between BEGIN/END PATCH markers and objects are matched
by their script name, so re-running replaces what the last run added instead of
piling up another copy.
"""
import json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, 'tools/hoenn_import/patches')
BEGIN = '@ BEGIN PATCH (tools/hoenn_import/patches)\n'
END = '@ END PATCH\n'


def strip(text):
    return re.sub(re.escape(BEGIN) + '.*?' + re.escape(END), '', text, flags=re.S)


def apply(name):
    d = os.path.join(R, 'data/maps', name)
    if not os.path.isdir(d):
        sys.exit('no such map: ' + name)
    if os.path.exists(os.path.join(P, name + '.json')):
        m = json.load(open(os.path.join(d, 'map.json')))
        extra = json.load(open(os.path.join(P, name + '.json')))
        for key, items in extra.items():
            if key == 'map_fields':
                m.update(items)          # header fields (requires_flash, weather...)
                continue
            if key == 'coord_overrides':
                for ov in items:
                    ov = dict(ov)
                    at = (ov.pop('x'), ov.pop('y'))
                    for c in m.get('coord_events') or []:
                        if (c['x'], c['y']) == at:
                            c.update(ov)
                            break
                    else:
                        sys.exit('%s: no trigger at %s' % (name, at))
                continue
            if key == 'bg_overrides':
                # point imported signs/triggers at scripts of the story's own, by tile
                for ov in items:
                    ov = dict(ov)
                    at = (ov.pop('x'), ov.pop('y'))
                    for b in m.get('bg_events') or []:
                        if (b['x'], b['y']) == at:
                            b.update(ov)
                            break
                    else:
                        sys.exit('%s: no sign at %s' % (name, at))
                continue
            if key == 'object_overrides':
                # change fields of an imported object (usually to point it at a new script)
                for ov in items:
                    ov = dict(ov)
                    if 'x' in ov and 'y' in ov:      # matched by tile, the reliable key
                        at = (ov.pop('x'), ov.pop('y'))
                        for o in m.get('object_events') or []:
                            if (o['x'], o['y']) == at:
                                o.update(ov)
                                break
                        else:
                            sys.exit('%s: no object at %s' % (name, at))
                        continue
                    match = ov.pop('match_script')
                    # an already patched map matches on the new script instead
                    for o in m['object_events']:
                        if o.get('script') in (match, ov.get('script')):
                            o.update(ov)
                            break
                    else:
                        sys.exit('%s: no object with script %s' % (name, match))
                continue
            scripts = {i.get('script') for i in items}
            m[key] = [o for o in (m.get(key) or []) if o.get('script') not in scripts] + items
        open(os.path.join(d, 'map.json'), 'w').write(json.dumps(m, indent=2, ensure_ascii=False) + '\n')
    ms = os.path.join(P, name + '.mapscripts')
    if os.path.exists(ms):
        lines = [l for l in open(ms).read().split('\n') if l.strip()]
        sc = os.path.join(d, 'scripts.inc')
        cur = open(sc).read()
        for l in lines:
            cur = cur.replace(l + '\n', '')
        head = '%s_MapScripts::\n' % name
        i = cur.index(head) + len(head)
        j = cur.index('\t.byte 0', i)
        open(sc, 'w').write(cur[:j] + ''.join(l + '\n' for l in lines) + cur[j:])
    for kind in ('scripts.inc', 'text.inc'):
        p = os.path.join(P, '%s.%s' % (name, kind))
        cur = strip(open(os.path.join(d, kind)).read()).rstrip('\n') + '\n'
        if os.path.exists(p):
            patch = open(p).read().rstrip('\n')
            # A patch that defines a label the import generated replaces it: that is how
            # the rewritten dialogue gets in front of Emerald's text without the import
            # and the patch both defining it.
            for lbl in re.findall(r'^(\w+)::', patch, re.M):
                cur = re.sub(r'^%s::\n(?:[ \t].*\n)+\n?' % re.escape(lbl), '', cur, flags=re.M)
            cur = cur.rstrip('\n') + '\n'
            cur += '\n' + BEGIN + patch + '\n' + END
        open(os.path.join(d, kind), 'w').write(cur)
    print('patched ' + name)


if __name__ == '__main__':
    names = sys.argv[1:] or sorted({f.split('.')[0] for f in os.listdir(P)})
    for n in names:
        apply(n)
