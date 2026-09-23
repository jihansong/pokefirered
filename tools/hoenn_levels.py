#!/usr/bin/env python3
"""hoenn_levels.py [--zone Z1] [--min 45] [--max 55] [--apply]

The Hoenn maps were imported with Emerald's levels, which a KANTO champion
walks straight through. This lifts one zone's trainers into a band, keeping
their order: the weakest trainer of the zone lands on --min, the strongest on
--max, and every mon of a party moves by the same amount, so a party's own
spread survives.

Running it twice changes nothing (levels already inside the band map to
themselves), so it is safe to re-run after tools/hoenn_import/import_trainers.py
has rewritten the parties.
"""
import argparse, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools'))
from hoenn_reachability import zone_of

PARTIES = os.path.join(R, 'src/data/trainer_parties_hoenn.h')
TRAINERS = os.path.join(R, 'src/data/trainers_hoenn.h')
# Gym leaders always sit at the top of their zone's band, whatever the import gave them
LEADERS = ('TRAINER_HOENN_ROXANNE_1', 'TRAINER_HOENN_BRAWLY_1', 'TRAINER_HOENN_WATTSON_1',
           'TRAINER_HOENN_FLANNERY_1', 'TRAINER_HOENN_NORMAN_1', 'TRAINER_HOENN_WINONA_1',
           'TRAINER_HOENN_TATE_AND_LIZA_1', 'TRAINER_HOENN_JUAN_1')


def zone_maps(zone):
    out = []
    for name in sorted(os.listdir(os.path.join(R, 'data/maps'))):
        d = os.path.join(R, 'data/maps', name)
        if not os.path.exists(os.path.join(d, '.hoenn')):
            continue
        if zone_of(name, json.load(open(os.path.join(d, 'map.json')))) == zone:
            out.append(name)
    return out


def trainers_of(maps):
    seen = {}
    for name in maps:
        p = os.path.join(R, 'data/maps', name, 'scripts.inc')
        if not os.path.exists(p):
            continue
        for t in re.findall(r'\bTRAINER_HOENN_[A-Z0-9_]+', open(p).read()):
            seen.setdefault(t, name)
    return seen


def party_symbols():
    txt = open(TRAINERS).read()
    return dict(re.findall(r'\[(TRAINER_HOENN_[A-Z0-9_]+)\]\s*=.*?\.party = \w+\((\w+)\)', txt, re.S))


def party_blocks():
    """symbol -> (start, end) span in the parties file"""
    txt = open(PARTIES).read()
    spans = {}
    for m in re.finditer(r'static const struct \w+ (\w+)\[\] = \{', txt):
        end = txt.index('\n};', m.end())
        spans[m.group(1)] = (m.end(), end)
    return txt, spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zone', default='Z1')
    ap.add_argument('--min', type=int, default=45)
    ap.add_argument('--max', type=int, default=55)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    maps = zone_maps(a.zone)
    where = trainers_of(maps)
    sym = party_symbols()
    txt, spans = party_blocks()

    use = {}
    for t in sorted(where):
        s = sym.get(t)
        if s is None or s not in spans:
            print('!! no party for %s' % t)
            continue
        use.setdefault(s, []).append(t)

    # a party shared with a trainer outside the zone would drag that one along
    outside = {s: [t for t, v in sym.items() if v == s and t not in where] for s in use}
    lvls = {s: [int(x) for x in re.findall(r'\.lvl = (\d+)', txt[slice(*spans[s])])] for s in use}
    tops = {s: max(v) for s, v in lvls.items()}
    zmin, zmax = min(tops.values()), max(tops.values())

    rows, new = [], {}
    for s in sorted(use):
        if any(t in LEADERS for t in use[s]):
            target = a.max
        elif zmax == zmin:
            target = a.min
        else:
            target = round(a.min + (tops[s] - zmin) * (a.max - a.min) / (zmax - zmin))
        d = target - tops[s]
        new[s] = [min(a.max, max(a.min, l + d)) for l in lvls[s]]
        rows.append((use[s][0], where[use[s][0]], lvls[s], new[s], outside[s]))

    print('%s: %d maps, %d trainers, %d parties, original top levels %d..%d -> %d..%d'
          % (a.zone, len(maps), len(where), len(use), zmin, zmax, a.min, a.max))
    for t, m, old, nw, out in rows:
        print('  %-38s %-28s %s -> %s%s'
              % (t.replace('TRAINER_HOENN_', ''), m, old, nw,
                 '  (party shared with %s)' % ', '.join(out) if out else ''))
    if not a.apply:
        print('(dry run; pass --apply to write %s)' % os.path.relpath(PARTIES, R))
        return

    out = []
    pos = 0
    for s in sorted(use, key=lambda s: spans[s][0]):
        st, en = spans[s]
        body, it = txt[st:en], iter(new[s])
        out.append(txt[pos:st])
        out.append(re.sub(r'\.lvl = \d+', lambda m: '.lvl = %d' % next(it), body))
        pos = en
    out.append(txt[pos:])
    open(PARTIES, 'w').write(''.join(out))
    print('wrote %s' % os.path.relpath(PARTIES, R))


if __name__ == '__main__':
    main()
