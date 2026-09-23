#!/usr/bin/env python3
"""dexcheck.py [-v] [--version leafgreen|firered] [--hoenn open|all|none] [--species NAME ...]

Static check that each of the 386 national dex species can be obtained in one
save without trading (the rule of docs/dex-completion.md). Read-only.

Sources, each read from the tree:
  wild     src/data/wild_encounters.json, this version's tables only (the other
           version's _FireRed/_LeafGreen tables are skipped). ALTERING CAVE's
           sets 2-9 count only while field_specials.c rotates them by the
           virtual day. Hoenn maps (those with a .hoenn marker) count only in
           the zones opened so far (--hoenn open, see textaudit.OPEN_ZONES).
  script   givemon / giveegg / setwildbattle / seteventmon in data/maps and
           data/scripts, with a SPECIES_ argument or a var that a setvar
           VAR, SPECIES_X reaching the command (goto/call/fall-through) fills.
           Scripts of Hoenn maps outside the open zones are skipped too.
           Every table of an encounter counts (_night/_morning ones too).
  roamer   every SPECIES_ in src/roamer.c
  C        sContestEncounters (src/bug_contest.c), sHiddenGrottoes
           (src/field_specials.c) and the CreateMon*(gEnemyParty...) calls of
           src/wild_encounter.c (field phenomena)
  trade    src/data/ingame_trades.h (preprocessed for this version): the
           offered species, once the requested one is obtainable
  evolve   src/data/pokemon/evolution.h, every method but EVO_TRADE and
           EVO_TRADE_ITEM (this hack moves those to Lv37 and
           EVO_LEVEL_HOLD_ITEM). Items for stones/held items are assumed on sale
           (docs/dex-completion.md 3: CELADON dept. store 4F).
  breed    a DAY CARE map must exist. An obtainable species that is not in
           EGG_GROUP_UNDISCOVERED gives its line's first stage (the species
           nothing evolves into); a genderless or single-gender parent needs
           DITTO. WYNAUT and AZURILL also need LAX / SEA INCENSE placed on a
           map (src/daycare.c), else the egg is the parent's own species.

Prints "N/386 obtainable" and the missing ones; -v adds one line per species
with the first source found. Exit status 1 if fewer than 386.
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

LABEL_RE = re.compile(r'^(\w+)::?')
IDENT_RE = re.compile(r'\b[A-Za-z_]\w*\b')
ENDING = {'end', 'return', 'goto', 'releaseall_end'}
GIVE = ('givemon', 'giveegg', 'setwildbattle', 'seteventmon')
TRADE_EVOS = ('EVO_TRADE', 'EVO_TRADE_ITEM')


def read(path):
    return open(os.path.join(REPO, path), encoding='utf-8', errors='replace').read()


def national_dex():
    """SPECIES_X -> national number, for the 386 species"""
    enum = read('include/constants/pokedex.h')
    names = re.findall(r'^\s*NATIONAL_DEX_(\w+),', enum, re.M)
    nat = {n: i for i, n in enumerate(names)}              # NATIONAL_DEX_NONE = 0
    out = {}
    for name in re.findall(r'SPECIES_TO_NATIONAL\((\w+)\)', read('src/pokemon.c')):
        if name in nat and 1 <= nat[name] <= 386:
            out['SPECIES_' + name] = nat[name]
    return out


def cpp(path, version):
    return subprocess.run(['cpp', '-P', '-undef', '-D' + version.upper(), '-x', 'c', os.path.join(REPO, path)],
                          capture_output=True, text=True, check=True).stdout


def hoenn_maps_closed(mode):
    """map dir names whose content should not count"""
    hoenn = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(REPO, 'data/maps/*/.hoenn'))}
    if mode == 'all':
        return set()
    if mode == 'none':
        return hoenn
    import textaudit
    zones = textaudit.zone_maps()
    open_maps = {m for z in textaudit.OPEN_ZONES for m in zones.get(z, [])}
    return hoenn - open_maps


def wild_sources(version, closed):
    import gamedata
    dirs = {k: v['dir'] for k, v in gamedata.maps().items()}
    other = '_FireRed' if version == 'leafgreen' else '_LeafGreen'
    rotates = '% NUM_ALTERING_CAVE_TABLES' in read('src/field_specials.c')
    found = collections.defaultdict(list)
    d = json.load(open(os.path.join(REPO, 'src/data/wild_encounters.json')))
    for grp in d['wild_encounter_groups']:
        for enc in grp['encounters']:
            label = enc['base_label']
            if label.endswith(other):
                continue
            if re.search(r'AlteringCave_[2-9]_', label) and not rotates:
                continue
            m = dirs.get(enc['map'], enc['map'])
            if m in closed:
                continue
            for kind, table in enc.items():          # land_mons, fishing_mons, land_mons_night...
                for mon in (table.get('mons', []) if isinstance(table, dict) else []):
                    found[mon['species']].append(f'wild {m} ({kind.replace("_mons", "")})')
    return found


def script_sources(closed):
    labels, files = {}, []
    for p in glob.glob(os.path.join(REPO, 'data/maps/*/scripts.inc')):
        m = os.path.basename(os.path.dirname(p))
        if m not in closed:
            files.append((p, m))
    files += [(p, None) for p in glob.glob(os.path.join(REPO, 'data/scripts/*.inc'))]
    files.append((os.path.join(REPO, 'data/event_scripts.s'), None))
    for p, owner in files:
        cur, prev = None, None
        for raw in open(p, encoding='utf-8', errors='replace'):
            line = raw.split('@')[0].rstrip()
            mm = LABEL_RE.match(line)
            if mm:
                name = mm.group(1)
                if cur is not None and not cur['closed']:
                    cur['next'] = name
                cur = labels[name] = {'map': owner or os.path.relpath(p, REPO), 'refs': set(), 'next': None,
                                      'closed': False, 'sets': [], 'gives': []}
                line = line[mm.end():]
            if cur is None or not line.strip():
                continue
            cmd, _, args = line.strip().partition(' ')
            argv = [x.strip() for x in args.split(',')]
            if cmd in GIVE and argv and argv[0]:
                cur['gives'].append((cmd, argv[0]))
            if cmd == 'setvar' and len(argv) == 2 and argv[1].startswith('SPECIES_'):
                cur['sets'].append((argv[0], argv[1]))
            cur['refs'].update(IDENT_RE.findall(args))
            cur['closed'] = cmd in ENDING or cmd.startswith('.')
    found = collections.defaultdict(list)
    for name, info in labels.items():
        for cmd, arg in info['gives']:
            if arg.startswith('SPECIES_'):
                found[arg].append(f'{cmd} {info["map"]}')
        if not info['sets']:
            continue
        # which var-taking give commands can this label reach?
        seen, stack, uses = set(), [name], set()
        while stack:
            lab = stack.pop()
            if lab in seen or lab not in labels:
                continue
            seen.add(lab)
            li = labels[lab]
            uses.update((cmd, arg) for cmd, arg in li['gives'] if not arg.startswith('SPECIES_'))
            stack.extend(li['refs'] - seen)
            if li['next'] and not li['closed']:
                stack.append(li['next'])
        for var, species in info['sets']:
            for cmd, arg in uses:
                if arg == var:
                    found[species].append(f'{cmd} {info["map"]} (via {var})')
    return found


def c_table(path, name):
    """SPECIES_ names inside the C array `name` of a source file"""
    src = read(path)
    i = src.find(name + '[')
    if i < 0:
        return []
    body = src[src.index('{', i):src.index('};', i)]
    return re.findall(r'\bSPECIES_(?!NONE\b)\w+', body)


def c_sources():
    found = collections.defaultdict(list)
    for sp in re.findall(r'\bSPECIES_(?!NONE\b)\w+', read('src/roamer.c')):
        found[sp].append('roamer (src/roamer.c)')
    for path, table, why in (('src/bug_contest.c', 'sContestEncounters', 'bug catching contest'),
                             ('src/field_specials.c', 'sHiddenGrottoes', 'hidden grotto')):
        for sp in c_table(path, table):
            found[sp].append(f'{why} ({path} {table})')
    # wild battles built in C (field phenomena): CreateMon*(&gEnemyParty... / CreateShinyWildMon(
    for line in read('src/wild_encounter.c').split('\n'):
        if re.search(r'CreateMon\w*\(&?gEnemyParty|CreateShinyWildMon\(', line):
            for sp in re.findall(r'\bSPECIES_(?!NONE\b)\w+', line):
                found[sp].append('field phenomenon / C wild battle (src/wild_encounter.c)')
    return found


def trades(version):
    src = cpp('src/data/ingame_trades.h', version)
    out = []
    for block in re.split(r'\[INGAME_TRADE_\w+\]\s*=', src)[1:]:
        give = re.search(r'\.species\s*=\s*(SPECIES_\w+)', block)
        want = re.search(r'\.requestedSpecies\s*=\s*(SPECIES_\w+)', block)
        if give and want:
            out.append((give.group(1), want.group(1)))
    return out


def evolutions():
    """[(from, method, param, to)]"""
    src = read('src/data/pokemon/evolution.h')
    out = []
    for m in re.finditer(r'\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\}\s*,?\s*(?=\[SPECIES_|\};)', src, re.S):
        for e in re.finditer(r'\{\s*(EVO_\w+)\s*,\s*((?:\w+\([^)]*\))|[^,]+?)\s*,\s*(SPECIES_\w+)\s*\}', m.group(2)):
            out.append((m.group(1), e.group(1), e.group(2), e.group(3)))
    return out


def species_info():
    """SPECIES_X -> (genderRatio, eggGroups)"""
    src = read('src/data/pokemon/species_info.h')
    out = {}
    for m in re.finditer(r'\[(SPECIES_\w+)\]\s*=\s*\{(.*?)\n\s*\},', src, re.S):
        g = re.search(r'\.genderRatio\s*=\s*([^,\n]+)', m.group(2))
        e = re.search(r'\.eggGroups\s*=\s*\{([^}]*)\}', m.group(2))
        out[m.group(1)] = (g.group(1).strip() if g else '', e.group(1) if e else '')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', choices=('leafgreen', 'firered'), default='leafgreen')
    ap.add_argument('--hoenn', choices=('open', 'all', 'none'), default='open',
                    help='which imported Hoenn maps count (default: the opened zones)')
    ap.add_argument('--species', nargs='*', default=[], help='explain these species (e.g. AZURILL)')
    ap.add_argument('-v', '--verbose', action='store_true', help='one line per species')
    a = ap.parse_args()

    dex = national_dex()
    closed = hoenn_maps_closed(a.hoenn)
    base = collections.defaultdict(list)
    for src in (wild_sources(a.version, closed), script_sources(closed), c_sources()):
        for sp, why in src.items():
            base[sp] += why

    source = {sp: why[0] for sp, why in base.items()}
    evos = evolutions()
    info = species_info()
    prevo = {to: frm for frm, _, _, to in evos}
    maps_text = '\n'.join(read(os.path.relpath(p, REPO)) for p in glob.glob(os.path.join(REPO, 'data/maps/*/*.inc'))
                          + glob.glob(os.path.join(REPO, 'data/maps/*/map.json')))
    has_item = lambda item: re.search(r'\b%s\b' % item, maps_text) is not None
    daycare = bool(glob.glob(os.path.join(REPO, 'data/maps/*DayCare*')))
    incense = {'SPECIES_WYNAUT': 'ITEM_LAX_INCENSE', 'SPECIES_AZURILL': 'ITEM_SEA_INCENSE'}

    def first_stage(sp):
        while sp in prevo:
            sp = prevo[sp]
        return sp

    changed = True
    while changed:
        changed = False

        def add(sp, why):
            nonlocal changed
            if sp not in source:
                source[sp] = why
                changed = True
        for give, want in trades(a.version):
            if want in source:
                add(give, f'in-game trade for {want[8:]}')
        for frm, method, param, to in evos:
            if frm in source and method not in TRADE_EVOS:
                add(to, f'evolves from {frm[8:]} ({method[4:].lower()} {param})')
        if daycare:
            ditto = 'SPECIES_DITTO' in source
            for sp in list(source):
                gender, eggs = info.get(sp, ('', ''))
                if 'EGG_GROUP_UNDISCOVERED' in eggs:
                    continue
                if gender in ('MON_GENDERLESS', 'MON_MALE', 'MON_FEMALE') and not ditto:
                    continue
                egg = first_stage(sp)
                if egg in incense and not has_item(incense[egg]):
                    # without the incense the egg skips the baby
                    nxt = [to for frm, _, _, to in evos if frm == egg]
                    egg = nxt[0] if nxt else egg
                add(egg, f'bred from {sp[8:]}' + (f' holding {incense[egg][5:]}' if egg in incense else ''))

    obtainable = {sp for sp in source if sp in dex}
    missing = sorted((n, sp) for sp, n in dex.items() if sp not in source)
    if a.verbose:
        for sp, n in sorted(dex.items(), key=lambda kv: kv[1]):
            print(f'{n:3} {sp[8:]:12} {source.get(sp, "-- NOT OBTAINABLE")}')
        print()
    for name in a.species:
        sp = 'SPECIES_' + name.upper()
        print(f'{sp[8:]}: {source.get(sp, "not obtainable")}')
        for why in base.get(sp, [])[1:]:
            print(f'    also {why}')
    print(f'{len(obtainable)}/{len(dex)} obtainable ({a.version}, Hoenn maps: {a.hoenn}, '
          f'direct sources {sum(1 for sp in base if sp in dex)})')
    if missing:
        print('missing: ' + ', '.join(f'#{n} {sp[8:]}' for n, sp in missing))
    sys.exit(1 if len(obtainable) < len(dex) else 0)


if __name__ == '__main__':
    main()
