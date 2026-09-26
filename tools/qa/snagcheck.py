#!/usr/bin/env python3
"""Build check for trainer-battle snagging (v0.10.0, docs/v0.10.0-plan.md 9.1).

    tools/qa/snagcheck.py [--rom pokemonthyl.gba] [-v]

Reads the built ROM (gTrainers, the parties, and src/snag.c's family tables
through the .sym) and fails when:
  - the Kanto rival, Tournament BLUE or JESSIE & JAMES (who remember what was
    taken from them) have a species with no family slot in src/snag.c, or
    JESSIE & JAMES's MEOWTH (which refuses the BALL) has one;
  - a slot is outside its group's range, or its flag is not one of the
    FLAG_SNAG_* constants, or another flag constant lands in the reserved
    Hoenn flags 0x780..0x79F;
  - the number of rival or JESSIE & JAMES battles differs from the plan's
    (19 + Tournament BLUE, 14): a new battle needs its species checked here;
  - some trainer's snagged POKéMON would get an empty original trainer name
    or one longer than 7 characters (the rules of GetSnagOtName, plan 3.2).
-v also lists the names the rules shorten.
"""

import argparse
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emu import fresh_syms                                   # noqa: E402
from gamedata import DEFAULT_ROM, REPO, consts               # noqa: E402
from textwidth import load_charmap                           # noqa: E402

TRAINER_SIZE = 0x28          # struct Trainer (include/battle.h)
FAMILY_SIZE = 4              # struct SnagFamily in src/snag.c
PLAN_RIVALS = 20             # 19 Kanto rival battles + Tournament BLUE (plan 5.3)
PLAN_ROCKETS = 14            # JESSIE & JAMES #1..#13 + the tournament
OT_NAME_LENGTH = 7           # PLAYER_NAME_LENGTH


def load_sym_table(sym_path):
    syms = {}
    with open(sym_path) as f:
        for line in f:
            p = line.split()
            if len(p) >= 4:
                syms[p[3]] = (int(p[0], 16), int(p[2], 16))
    return syms


def decode_charset():
    chars, _ = load_charmap()
    back = {}
    for c, bs in chars.items():
        if len(bs) == 1 and len(c) == 1:
            back.setdefault(bs[0], c)
    return back


class Game:
    def __init__(self, rom_path):
        with open(rom_path, 'rb') as f:
            self.data = f.read()
        self.syms = load_sym_table(fresh_syms(rom_path))
        self.chars = decode_charset()

    def at(self, addr, n):
        o = addr - 0x08000000
        return self.data[o:o + n]

    def text(self, raw):
        out = []
        for b in raw:
            if b == 0xFF:
                break
            out.append(self.chars.get(b, '?'))
        return ''.join(out)

    def trainers(self):
        addr, size = self.syms['gTrainers']
        for num in range(size // TRAINER_SIZE):
            raw = self.at(addr + num * TRAINER_SIZE, TRAINER_SIZE)
            flags, tclass, music_gender, pic = raw[0], raw[1], raw[2], raw[3]
            party_size = raw[0x20]
            party_ptr = struct.unpack_from('<I', raw, 0x24)[0]
            # every TrainerMon* struct starts u16 iv, u8 lvl, u16 species (offset 4);
            # custom movesets make it 16 bytes, otherwise 8
            mon_size = 16 if flags & 1 else 8
            species = []
            if party_ptr >= 0x08000000:
                for i in range(party_size):
                    species.append(struct.unpack_from('<H', self.at(party_ptr + i * mon_size + 4, 2))[0])
            yield {'num': num, 'class': tclass, 'female': bool(music_gender & 0x80), 'pic': pic,
                   'raw_name': raw[4:4 + 13], 'name': self.text(raw[4:4 + 13]), 'species': species}

    def families(self, name):
        addr, size = self.syms[name]
        out = []
        for i in range(size // FAMILY_SIZE):
            species, slot = struct.unpack_from('<HB', self.at(addr + i * FAMILY_SIZE, 3))
            if species == 0:
                break
            out.append((species, slot))
        return out


def snag_group(t, c):
    """src/snag.c GetSnagGroup."""
    if t['pic'] == c['TRAINER_PIC_JESSIE_JAMES']:
        return 'rocket'
    if t['num'] == c['TRAINER_TOURNEY_BLUE']:
        return 'rival'
    if t['num'] < c['HOENN_TRAINERS_START'] and t['class'] in (
            c['TRAINER_CLASS_RIVAL_EARLY'], c['TRAINER_CLASS_RIVAL_LATE'], c['TRAINER_CLASS_CHAMPION']):
        return 'rival'
    return None


def ot_name(name):
    """src/snag.c GetSnagOtName for everyone but the rival and JESSIE & JAMES."""
    if name.startswith('LT.'):
        name = name[3:].lstrip(' ')
    name = name.split('&')[0][:OT_NAME_LENGTH]
    return name.rstrip(' ')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rom', default=DEFAULT_ROM)
    ap.add_argument('-v', '--verbose', action='store_true')
    a = ap.parse_args()

    names = ['TRAINER_PIC_JESSIE_JAMES', 'TRAINER_TOURNEY_BLUE', 'HOENN_TRAINERS_START',
             'TRAINER_CLASS_RIVAL_EARLY', 'TRAINER_CLASS_RIVAL_LATE', 'TRAINER_CLASS_CHAMPION',
             'SPECIES_MEOWTH', 'HOENN_FLAGS_START']
    c = consts(names)
    snag_h = open(os.path.join(REPO, 'include', 'constants', 'snag.h')).read()
    snag_consts = sorted(set(re.findall(r'#define ((?:SNAG|FLAG_SNAG)_\w+)', snag_h)))
    c.update(consts(snag_consts))
    species_names = {}
    for line in open(os.path.join(REPO, 'include', 'constants', 'species.h')):
        m = re.match(r'#define (SPECIES_\w+)\s+(\d+)\s*$', line)
        if m:
            species_names.setdefault(int(m.group(2)), m.group(1)[8:])

    g = Game(a.rom)
    fails = []
    tables = {'rival': dict(g.families('sRivalFamilies')), 'rocket': dict(g.families('sRocketFamilies'))}
    ranges = {'rival': (c['SNAG_SLOTS_RIVAL_FIRST'], c['SNAG_SLOTS_RIVAL_END']),
              'rocket': (c['SNAG_SLOTS_ROCKET_FIRST'], c['SNAG_SLOTS_ROCKET_END'])}
    slot_flags = {v - c['SNAG_FLAGS_START'] for k, v in c.items() if k.startswith('FLAG_SNAG_')}

    # the tables themselves
    for group, table in tables.items():
        lo, hi = ranges[group]
        for sp, slot in table.items():
            if not lo <= slot < hi:
                fails.append('%s table: %s has slot %d, outside %d..%d' % (group, species_names.get(sp), slot, lo, hi - 1))
            if slot not in slot_flags:
                fails.append('%s table: slot %d has no FLAG_SNAG_* constant' % (group, slot))
    if c['SPECIES_MEOWTH'] in tables['rocket']:
        fails.append('rocket table: MEOWTH has a slot, but it refuses the BALL')
    if c['SNAG_FLAGS_START'] != c['HOENN_FLAGS_START'] + 0x780 or c['SNAG_SLOT_COUNT'] != 32:
        fails.append('SNAG_FLAGS_START/SNAG_SLOT_COUNT moved off the reservation 0x780..0x79F (docs/team/log.md)')

    # nothing else in the reserved flags
    flag_names = set()
    for fn in os.listdir(os.path.join(REPO, 'include', 'constants')):
        if fn.startswith('flags') and fn.endswith('.h'):
            flag_names |= set(re.findall(r'#define (FLAG_\w+)\s', open(os.path.join(REPO, 'include', 'constants', fn)).read()))
    lo, hi = c['SNAG_FLAGS_START'], c['SNAG_FLAGS_START'] + c['SNAG_SLOT_COUNT']
    for n, v in consts(sorted(flag_names)).items():
        if lo <= v < hi:
            fails.append('%s = 0x%X is inside the snag flags' % (n, v))

    # the parties
    counts = {'rival': 0, 'rocket': 0}
    shortened = []
    for t in g.trainers():
        group = snag_group(t, c)
        if group:
            counts[group] += 1
            for sp in t['species']:
                if group == 'rocket' and sp == c['SPECIES_MEOWTH']:
                    continue
                if sp not in tables[group]:
                    fails.append('trainer %d %s (%s): %s has no family slot in src/snag.c'
                                 % (t['num'], t['name'], group, species_names.get(sp, sp)))
        else:
            if not t['name'] or not t['species']:
                continue            # unused entries
            ot = ot_name(t['name'])
            if not 1 <= len(ot) <= OT_NAME_LENGTH:
                fails.append('trainer %d %r: original trainer name %r' % (t['num'], t['name'], ot))
            elif ot != t['name']:
                shortened.append('%-4d %-13s -> %s' % (t['num'], t['name'], ot))
    if counts['rival'] != PLAN_RIVALS:
        fails.append('%d rival battles, the plan has %d: check the new ones\' species here' % (counts['rival'], PLAN_RIVALS))
    if counts['rocket'] != PLAN_ROCKETS:
        fails.append('%d JESSIE & JAMES battles, the plan has %d' % (counts['rocket'], PLAN_ROCKETS))

    if a.verbose:
        print('\n'.join(shortened))
    print('rival battles %d, JESSIE & JAMES battles %d, family slots %d + %d, names shortened %d'
          % (counts['rival'], counts['rocket'], len(tables['rival']), len(tables['rocket']), len(shortened)))
    for f in fails:
        print('FAIL ' + f)
    print('snagcheck: %s' % ('OK' if not fails else '%d failure(s)' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
