#!/usr/bin/env python3
"""Edit a Thunder Yellow save for testing.

    savedit.py IN.sav [-o OUT.sav] COMMAND [ARGS] [COMMAND [ARGS] ...]

Commands (names are the C constant names; numbers work too):
    info                       where the player is, party, a few counters
    flag NAME [0|1]            show or set a flag (Hoenn flags included)
    var NAME [VALUE]           show or set a var (Hoenn vars included)
    trainer NAME [0|1]         show or set a trainer's beaten flag
    warp MAP X Y               put the player on MAP at (X, Y); MAP may be
                               MAP_ROUTE110, ROUTE110 or Route110
    warp MAP @N                ... at that map's warp event N
    strong SLOT LEVEL          party SLOT (0-5) at LEVEL with its experience,
                               IVs 31 and stats set to match, HP full
    mon SLOT SPECIES LEVEL     turn party SLOT into SPECIES at LEVEL (as strong,
                               keeping its moves; the nickname is the species')
    tonext SLOT N              party SLOT's experience N points short of its
                               next level
    held SLOT ITEM             party SLOT holds ITEM (ITEM_NONE takes it away)
    friendship SLOT N          party SLOT's friendship (0-255)
    starterbit SLOT 0|1        party SLOT's isStarterPikachu bit (Oak's PIKACHU)
    otid SLOT N                party SLOT's original trainer ID (N may be 0x...),
                               as if another player's POKéMON had been traded in
    frombox INDEX SLOT         party SLOT becomes a copy of PC box POKéMON
                               INDEX (0-419, box by box)
    lead SLOT                  swap party SLOT with the first POKéMON
    party N                    keep only the first N party POKéMON
    hp SLOT N                  party SLOT's current HP (0 = fainted)
    day N                      move the game clock N days forward (or back)
    hour H                     move the game clock forward to the next H:00
    dex SPECIES                mark a species seen and owned (all 4 places)
    money N / coins N          money and coins (both kept XORed with the save key)
    item ITEM N                exactly N of ITEM in the bag (0 removes it)
    firstitem ITEM N           exactly N of ITEM, first in its pocket, where the
                               cursor is when the bag is first opened
    fillitems [ITEM ...]       fill the ITEMS pocket's free slots with one each
                               of other items, never the ITEMs listed, so
                               giving any of those fails
    fillboxes                  fill every free PC box slot with a copy of the
                               first party POKéMON
    fastbattle                 options: battle style SET, animations off, fast
                               text (A-mashing through singles never switches)
    noquestlog                 empty the quest log, so CONTINUE shows no
                               "Previously on your quest" (whose playback
                               ignores playbgm) and loads the map at once

Without -o the input file is rewritten in place.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gamedata import const, item_name, map_info, maps, off, Rom           # noqa: E402
from savefile import SaveFile                                   # noqa: E402


COMMANDS = {'info', 'flag', 'var', 'trainer', 'warp', 'strong', 'mon', 'tonext', 'held', 'friendship',
            'starterbit', 'otid', 'frombox', 'lead', 'party', 'hp', 'day', 'hour', 'dex',
            'money', 'coins', 'item', 'firstitem', 'fillitems', 'fillboxes', 'fastbattle',
            'noquestlog'}


def _map_name(g, n):
    for m in maps().values():
        if m['group'] == g and m['num'] == n:
            return m['id']
    return '%d.%d' % (g, n)


def cmd_info(s, args):
    g, n, w, x, y = s.location()
    print('location  %s (%d,%d) warp %d' % (_map_name(g, n), x, y, w))
    print('layout    %d' % struct.unpack_from('<H', s.sb1, off('sb1.mapLayoutId'))[0])
    for i in range(s.party_count()):
        m = s.party_mon(i)
        print('party %d   species %d Lv%d' % (i, m.species(), m.level()))
    days = struct.unpack_from('<h', s.sb2, off('sb2.localTimeOffset') + off('time.days'))[0]
    print('day offset %d' % days)
    t = s.clock_minutes()
    print('game clock day %d %02d:%02d (virtual)' % (t // 1440, t % 1440 // 60, t % 60))
    print('money %d' % s.money())
    return 0


def run(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    src = argv.pop(0)
    out = src
    if argv[:1] == ['-o']:
        out = argv[1]
        argv = argv[2:]
    s = SaveFile(src)
    dirty = False
    rom = None
    while argv:
        cmd = argv.pop(0)
        if cmd == 'info':
            cmd_info(s, [])
        elif cmd == 'flag':
            name = argv.pop(0)
            if argv and argv[0] in ('0', '1'):
                s.set_flag(name, argv.pop(0) == '1')
                dirty = True
            print('%s = %d' % (name, s.flag(name)))
        elif cmd == 'trainer':
            name = argv.pop(0)
            if argv and argv[0] in ('0', '1'):
                s.set_trainer_beaten(name, argv.pop(0) == '1')
                dirty = True
            print('%s beaten = %d' % (name, s.trainer_beaten(name)))
        elif cmd == 'var':
            name = argv.pop(0)
            if argv and argv[0] not in COMMANDS:
                s.set_var(name, argv.pop(0))
                dirty = True
            print('%s = %d' % (name, s.var(name)))
        elif cmd == 'warp':
            name = argv.pop(0)
            where = argv.pop(0)
            if where.startswith('@'):
                w = map_info(name)['json']['warp_events'][int(where[1:])]
                x, y = w['x'], w['y']
            else:
                x, y = int(where), int(argv.pop(0))
            s.warp(name, x, y)
            dirty = True
            print('warp %s (%d,%d)' % (map_info(name)['id'], x, y))
        elif cmd == 'strong':
            slot, level = int(argv.pop(0)), int(argv.pop(0))
            rom = rom or Rom()
            stats = s.party_mon(slot).make_strong(level, rom)
            dirty = True
            print('slot %d Lv%d stats %s' % (slot, level, stats))
        elif cmd == 'mon':
            slot, name, level = int(argv.pop(0)), argv.pop(0), int(argv.pop(0))
            rom = rom or Rom()
            m = s.party_mon(slot)
            m.set_species(_species(name), rom)
            m.make_strong(level, rom)
            dirty = True
            print('slot %d %s Lv%d' % (slot, name, level))
        elif cmd == 'tonext':
            slot, n = int(argv.pop(0)), int(argv.pop(0))
            rom = rom or Rom()
            s.party_mon(slot).set_exp_to_next(n, rom)
            dirty = True
            print('slot %d %d exp short of the next level' % (slot, n))
        elif cmd == 'held':
            slot, name = int(argv.pop(0)), argv.pop(0)
            s.party_mon(slot).set_held(const(item_name(name)))
            dirty = True
            print('slot %d holds %s' % (slot, name))
        elif cmd == 'friendship':
            slot, n = int(argv.pop(0)), int(argv.pop(0))
            s.party_mon(slot).set_friendship(n)
            dirty = True
            print('slot %d friendship %d' % (slot, n))
        elif cmd == 'starterbit':
            slot, on = int(argv.pop(0)), argv.pop(0) == '1'
            s.party_mon(slot).set_starter_bit(on)
            dirty = True
            print('slot %d isStarterPikachu %d' % (slot, on))
        elif cmd == 'otid':
            slot, n = int(argv.pop(0)), int(argv.pop(0), 0)
            s.party_mon(slot).set_otid(n)
            dirty = True
            print('slot %d OT ID %08x' % (slot, n))
        elif cmd == 'frombox':
            index, slot = int(argv.pop(0)), int(argv.pop(0))
            rom = rom or Rom()
            species, level = s.copy_box_mon_to_party(index, slot, rom)
            dirty = True
            print('slot %d is box mon %d (species %d Lv%d)' % (slot, index, species, level))
        elif cmd == 'lead':
            slot = int(argv.pop(0))
            s.set_lead(slot)
            dirty = True
            print('party slot %d leads' % slot)
        elif cmd == 'party':
            n = int(argv.pop(0))
            s.keep_party(n)
            dirty = True
            print('party of %d' % s.party_count())
        elif cmd == 'hp':
            slot, hp = int(argv.pop(0)), int(argv.pop(0))
            s.set_hp(slot, hp)
            dirty = True
            print('slot %d HP %d' % (slot, hp))
        elif cmd == 'day':
            n = int(argv.pop(0))
            s.add_days(n)
            dirty = True
            print('clock %+d days' % n)
        elif cmd == 'hour':
            h = int(argv.pop(0))
            t = s.set_hour(h)
            dirty = True
            print('clock day %d %02d:00' % (t // 1440, h))
        elif cmd == 'item':
            name, n = argv.pop(0), int(argv.pop(0))
            s.set_item(name, n)
            dirty = True
            print('%s x%d' % (name, s.item_count(name)))
        elif cmd == 'firstitem':
            name, n = argv.pop(0), int(argv.pop(0))
            s.put_item_first(name, n)
            dirty = True
            print('%s x%d, first in its pocket' % (name, s.item_count(name)))
        elif cmd == 'fillitems':
            leave = []
            while argv and argv[0].startswith('ITEM_'):
                leave.append(argv.pop(0))
            n = s.fill_items(leave)
            dirty = True
            print('filled %d item slots' % n)
        elif cmd == 'fastbattle':
            s.fast_battles()
            dirty = True
            print('battle style SET, animations off, fast text')
        elif cmd == 'noquestlog':
            size = off('questlogscene')
            for i in range(const('QUEST_LOG_SCENE_COUNT')):
                s.sb1[off('sb1.questLog') + i * size] = 0   # startType: no scene
            dirty = True
            print('quest log emptied')
        elif cmd == 'fillboxes':
            n = s.fill_boxes()
            dirty = True
            print('filled %d box slots' % n)
        elif cmd == 'dex':
            name = argv.pop(0)
            sp = _species(name)
            s.set_dex(_national(sp))
            dirty = True
            print('dex %s seen+owned' % name)
        elif cmd == 'money':
            s.set_money(int(argv.pop(0)))
            dirty = True
        elif cmd == 'coins':
            n = int(argv.pop(0))
            key = struct.unpack_from('<I', s.sb2, off('sb2.encryptionKey'))[0]
            struct.pack_into('<H', s.sb1, off('sb1.coins'), (n ^ key) & 0xFFFF)
            dirty = True
        else:
            print('unknown command %s' % cmd, file=sys.stderr)
            return 2
    if dirty or out != src:
        s.save(out)
    return 0


def _species(name):
    return const(name if name.startswith('SPECIES_') or name.isdigit() else 'SPECIES_' + name)


_NAT = None


def _national(species):
    """Internal species number -> national dex number (they differ past Celebi)."""
    global _NAT
    if _NAT is None:
        rom = Rom()
        addr = rom.syms.get('sSpeciesToNationalPokedexNum') or rom.syms.get('gSpeciesToNationalPokedexNum')
        if addr is None:
            raise KeyError('no species-to-national table in the .sym')
        n = const('NUM_SPECIES') - 1
        _NAT = struct.unpack('<%dH' % n, rom.at(addr, n * 2))
    return _NAT[species - 1]


if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
