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
    day N                      move the game clock N days forward (or back)
    dex SPECIES                mark a species seen and owned (all 4 places)
    money N / coins N          money and coins (both kept XORed with the save key)

Without -o the input file is rewritten in place.
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gamedata import const, map_info, maps, off, Rom           # noqa: E402
from savefile import SaveFile                                   # noqa: E402


COMMANDS = {'info', 'flag', 'var', 'trainer', 'warp', 'strong', 'day', 'dex', 'money', 'coins'}


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
        elif cmd == 'day':
            n = int(argv.pop(0))
            s.add_days(n)
            dirty = True
            print('clock %+d days' % n)
        elif cmd == 'dex':
            name = argv.pop(0)
            sp = const(name if name.startswith('SPECIES_') or name.isdigit() else 'SPECIES_' + name)
            s.set_dex(_national(sp))
            dirty = True
            print('dex %s seen+owned' % name)
        elif cmd == 'money':
            n = int(argv.pop(0))
            key = struct.unpack_from('<I', s.sb2, off('sb2.encryptionKey'))[0]
            struct.pack_into('<I', s.sb1, off('sb1.money'), n ^ key)
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
