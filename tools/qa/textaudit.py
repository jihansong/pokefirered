#!/usr/bin/env python3
"""textaudit.py [--zone Z2 ...] [--map MauvilleCity ...] [--all-labels] [--unused] [-v] [--fail]
               [--emerald /root/src/pokeemerald]

Finds dialogue in the imported Hoenn maps that is still pokeemerald's original
text. Read-only.

  maps       --zone takes the zones of docs/hoenn-open-plan.md 4.2 (read from
             tools/hoenn_reachability.py --zones); --map takes map names.
             Default: the zones opened so far (OPEN_ZONES).
  texts      every label with .string lines in data/maps/<Map>/text.inc and
             scripts.inc (the rewritten dialogue from
             tools/hoenn_import/patches/ ends up in the same files).
  in use     import_maps.py leaves its generated scripts and texts in place
             when a patch gives an object a script of its own, so a map can
             hold original text nothing shows any more. A label counts only
             if the game can reach it: from the scripts named in any map.json
             (objects, signs, triggers), any <Map>_MapScripts, any label named
             in src/ or in the shared scripts (data/scripts, event_scripts.s),
             then through every label a reached label names, plus fall-through.
             --all-labels counts the unreachable ones too; --unused lists them.
  original   the import renamed Emerald's labels (<Map>_Text_H<n>) and
             re-wrapped the lines, so labels cannot be paired by name. A text
             is an original when, after joining its .string lines, turning
             \\n \\l \\p into spaces and squeezing whitespace, it equals a text
             of the same map in pokeemerald (data/maps/<Map>/scripts.inc or
             text.inc, or a <Map>_Text_ label of data/text/trainers.inc). An
             equal text anywhere else in Emerald is reported as "elsewhere"
             (shared or copied lines) and counted the same.
  harmless   originals there is nothing to rewrite in:
               sign    no lower-case letter once {...} codes are removed:
                       direction signs ("ROUTE 110 {DOWN_ARROW} SLATEPORT
                       CITY") and name boards ("WANDA'S HOUSE")
               cry     an optional "NAME: " speaker, then at most 3 words that
                       are all the same word ("Pika pika!") or each (hyphens
                       dropped) a repeated syllable, ends in a drawn-out vowel
                       or holds a letter three times ("La-lalala…", "Guguu?",
                       "Kyuuu…", "Fffnyaaaah…")
Exit status 0; with --fail, 1 if an original that is not harmless is in use.
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
EMERALD = '/root/src/pokeemerald'
# Zones opened so far: Z1 in v0.7.0, Z2 in v0.8.0.
OPEN_ZONES = ('Z1', 'Z2')
# tools/hoenn_import/import_maps.py RENAME, the other way round
EM_NAME = {'HoennVictoryRoad_1F': 'VictoryRoad_1F', 'HoennSafariZone_North': 'SafariZone_North'}

LABEL_RE = re.compile(r'^(\w+)::?')
STRING_RE = re.compile(r'^\s*\.string\s+"(.*)"')
IDENT_RE = re.compile(r'\b[A-Za-z_]\w*\b')
ENDING = {'end', 'return', 'goto', 'releaseall_end', 'goto_if_questlog', 'step_end', 'end_movement'}


def parse(path):
    """-> (texts: label -> [(line, contents)], labels: label -> {'refs', 'next', 'closed', 'line'})"""
    texts, labels, order = {}, {}, []
    cur = None
    for n, raw in enumerate(open(path, encoding='utf-8', errors='replace'), 1):
        line = raw.split('@')[0].rstrip() if '.string' not in raw else raw.rstrip('\n')
        m = LABEL_RE.match(line)
        if m:
            cur = m.group(1)
            labels[cur] = {'refs': set(), 'next': None, 'closed': False, 'line': n}
            if order and not labels[order[-1]]['closed']:
                labels[order[-1]]['next'] = cur
            order.append(cur)
            line = line[m.end():]
            if not line.strip():
                continue
        if cur is None:
            continue
        s = line.strip()
        if not s:
            continue
        ms = STRING_RE.match(line)
        if ms:
            texts.setdefault(cur, []).append((n, ms.group(1)))
            labels[cur]['closed'] = True
            continue
        cmd, _, args = s.partition(' ')
        labels[cur]['refs'].update(IDENT_RE.findall(args))
        labels[cur]['closed'] = cmd in ENDING or cmd.startswith('.')
    return texts, labels


def norm(pieces):
    s = ''.join(p for _, p in pieces)
    if s.endswith('$'):
        s = s[:-1]
    s = re.sub(r'\\[nlp]', ' ', s)
    return ' '.join(s.split())


def zone_maps():
    out = subprocess.run([sys.executable, os.path.join(REPO, 'tools/hoenn_reachability.py'), '--zones'],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    zones = {}
    for line in out.split('\n'):
        m = re.match(r'^- (Z\d+): (.*)$', line)
        if m:
            zones[m.group(1)] = m.group(2).split(', ')
    return zones


def reachable(all_labels):
    """labels the game can reach (see "in use" above)"""
    roots = set()
    for p in glob.glob(os.path.join(REPO, 'data/maps/*/map.json')):
        d = json.load(open(p))
        roots.add(d.get('name', '') + '_MapScripts')
        for key in ('object_events', 'bg_events', 'coord_events'):
            for ev in d.get(key) or []:
                if ev.get('script'):
                    roots.add(ev['script'])
    for pat in ('src/**/*.c', 'src/**/*.h', 'include/**/*.h'):
        for p in glob.glob(os.path.join(REPO, pat), recursive=True):
            roots.update(w for w in IDENT_RE.findall(open(p, encoding='utf-8', errors='replace').read())
                         if w in all_labels)
    for lab, info in all_labels.items():
        if info['shared']:
            roots.add(lab)
    seen, stack = set(), [r for r in roots if r in all_labels]
    while stack:
        lab = stack.pop()
        if lab in seen:
            continue
        seen.add(lab)
        info = all_labels[lab]
        stack.extend(r for r in info['refs'] if r in all_labels and r not in seen)
        if info['next'] and not info['closed']:
            stack.append(info['next'])
    return seen


def emerald_index(em):
    """normalised text -> [(emerald map or file, label)]"""
    idx = collections.defaultdict(list)
    files = [(p, os.path.basename(os.path.dirname(p))) for p in glob.glob(em + '/data/maps/*/*.inc')]
    files += [(p, os.path.relpath(p, em)) for p in glob.glob(em + '/data/text/*.inc') + glob.glob(em + '/data/scripts/*.inc')]
    for p, owner in files:
        for lab, pieces in parse(p)[0].items():
            idx[norm(pieces)].append((owner, lab))
    return idx


def is_repeat(word):
    w = word.lower()
    # a drawn-out ending ("Guguu", "Kyuuu") or a letter held three times ("Fffnyaaaah", "Zzz")
    if re.search(r'([aeiouy])\1+h?$', w) or re.search(r'(.)\1\1', w):
        return True
    return bool(re.fullmatch(r'(.{1,4})\1+.?', w))


def harmless(text):
    bare = re.sub(r'\{[^}]*\}', ' ', text)
    if not re.search(r'[a-zé]', bare):
        return 'sign'
    body = re.sub(r'^[A-Z][A-Z0-9 .\'é]*:\s*', '', bare)
    words = [w.replace('-', '') for w in re.findall(r"[A-Za-zé'][A-Za-zé'-]*", body)]
    if not words or len(words) > 3:
        return None
    if len({w.lower() for w in words}) == 1:
        return 'cry'
    if all(is_repeat(w) for w in words):
        return 'cry'
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--zone', action='append', default=[], help='Z1..Z8 (repeatable)')
    ap.add_argument('--map', action='append', default=[], help='map name (repeatable)')
    ap.add_argument('--emerald', default=EMERALD)
    ap.add_argument('--all-labels', action='store_true', help='also count labels nothing reaches')
    ap.add_argument('--unused', action='store_true', help='list the text labels nothing reaches')
    ap.add_argument('-v', '--verbose', action='store_true', help='print every original, harmless ones too')
    ap.add_argument('--fail', action='store_true', help='exit 1 if an original that is not harmless is in use')
    a = ap.parse_args()

    zones = zone_maps()
    names = list(a.map)
    for z in a.zone or ([] if a.map else OPEN_ZONES):
        if z not in zones:
            sys.exit(f'unknown zone {z} (have {", ".join(sorted(zones))})')
        names += zones[z]
    zone_of = {m: z for z, ms in zones.items() for m in ms}
    for m in names:
        if not os.path.isdir(os.path.join(REPO, 'data/maps', m)):
            sys.exit(f'no such map: {m}')

    # every label of every script/text file, for the reachability walk
    all_labels, map_texts = {}, {}
    shared = glob.glob(os.path.join(REPO, 'data/scripts/*.inc')) + [os.path.join(REPO, 'data/event_scripts.s')]
    mapfiles = glob.glob(os.path.join(REPO, 'data/maps/*/scripts.inc')) + glob.glob(os.path.join(REPO, 'data/maps/*/text.inc'))
    textfiles = glob.glob(os.path.join(REPO, 'data/text/*.inc'))
    for p in shared + mapfiles + textfiles:
        texts, labels = parse(p)
        for lab, info in labels.items():
            info['shared'] = p in shared
            all_labels[lab] = info
        m = os.path.basename(os.path.dirname(p))
        if p in mapfiles and m in names:
            for lab, pieces in texts.items():
                map_texts.setdefault(m, []).append((os.path.relpath(p, REPO), lab, pieces))
    used = reachable(all_labels)
    idx = emerald_index(a.emerald)

    tot = collections.Counter()
    bad, unused = [], []
    print(f'{"map":44} {"zone":4} {"texts":>5} {"orig":>5} {"harml":>5} {"fix":>5} {"unused":>6}')
    for m in names:
        em = EM_NAME.get(m, m)
        c = collections.Counter()
        rows = []
        for rel, lab, pieces in map_texts.get(m, []):
            live = lab in used
            if not live:
                unused.append((rel, pieces[0][0], lab))
                c['unused'] += 1
                if not a.all_labels:
                    continue
            c['texts'] += 1
            key = norm(pieces)
            hits = idx.get(key)
            if not hits:
                continue
            # Emerald keeps trainer lines in data/text/trainers.inc under the map's own prefix
            same = [l for o, l in hits if o == em or l.startswith(em + '_Text_')]
            where = same[0] if same else 'elsewhere: ' + ', '.join(f'{o}:{l}' for o, l in hits[:2])
            kind = harmless(key)
            c['orig'] += 1
            c['harmless'] += bool(kind)
            rows.append((rel, pieces[0][0], lab, kind, where, key, live))
            if not kind:
                bad.append(rows[-1])
        tot.update(c)
        print(f'{m:44} {zone_of.get(m, "-"):4} {c["texts"]:5} {c["orig"]:5} {c["harmless"]:5} '
              f'{c["orig"] - c["harmless"]:5} {c["unused"]:6}')
        for rel, line, lab, kind, where, key, live in rows:
            if a.verbose or not kind:
                tag = kind or 'ORIGINAL'
                print(f'    {rel}:{line}: {tag:8} {lab} = {where}{"" if live else " (unused)"}')
                print(f'        "{key[:100]}{"…" if len(key) > 100 else ""}"')
    print(f'\n{len(names)} maps, {tot["texts"]} texts{"" if a.all_labels else " in use"}: '
          f'{tot["orig"]} still the Emerald original, {tot["harmless"]} of them harmless '
          f'(sign/cry), {tot["orig"] - tot["harmless"]} to rewrite; '
          f'{tot["unused"]} text labels nothing reaches')
    if a.unused:
        print('\nunused text labels:')
        for rel, line, lab in unused:
            print(f'  {rel}:{line}: {lab}')
    sys.exit(1 if a.fail and bad else 0)


if __name__ == '__main__':
    main()
