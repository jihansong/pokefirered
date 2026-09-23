#!/usr/bin/env python3
"""Save compatibility test: does the current ROM load old saves exactly the
way the release that wrote them does?

For each save in saves/ it boots the release ROM that saved it (qa-base/<tag>,
built by tools/qa/refroms.sh) and the current ROM, stops both at the main
menu (the save has just been read into RAM there), and compares SaveBlock1,
SaveBlock2 and the PC storage byte for byte: IDENTICAL or the differing
fields. Then it continues the save on the current ROM into the overworld and
checks the player stands where the save says, with the game still running.

    tools/qa/savetest.py                   # all saves in SAVES below
    tools/qa/savetest.py saves/hoenn.sav:v0.7.0 --shots /tmp/st
"""

import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emu import Emu                                  # noqa: E402
from gamedata import REPO, FIELDS, off, offsets      # noqa: E402

# save file -> the release that wrote it (from the save's date against the
# release dates; see docs/INSTALL.md "QA")
SAVES = [
    ('saves/v0.1.0.sav', 'v0.1.0'),
    ('saves/v0.2.1.sav', 'v0.2.1'),
    ('saves/pokemonthyl_v3.gba.sav', 'v0.3.0'),
    ('saves/v0.5.1.sav', 'v0.5.1'),
    ('saves/hoenn.sav', 'v0.7.0'),
]

BLOCKS = [('SaveBlock1', 'gSaveBlock1Ptr', 'sb1'), ('SaveBlock2', 'gSaveBlock2Ptr', 'sb2'),
          ('PokemonStorage', 'gPokemonStoragePtr', 'storage')]


def at_main_menu(rom, sav):
    """Boot to the main menu and return the three blocks as loaded."""
    e = Emu(rom, sav)
    target = e.syms['CB2_MainMenu']
    for _ in range(400):
        if (e.callback2() & ~1) == target:
            break
        e.press('A', hold=2, after=12)
    else:
        e.close()
        raise TimeoutError('%s never reached the main menu' % rom)
    e.run(20)
    status = e.u8(e.syms['gSaveFileStatus'])
    blocks = {key: e.read(e.ptr(ptr), off(key)) for _, ptr, key in BLOCKS}
    e.close()
    return status, blocks


def field_name(block, pos):
    best = None
    for key, (st, member) in FIELDS.items():
        if member is None or not key.startswith(block + '.'):
            continue
        o = offsets()[key]
        if o <= pos and (best is None or o > best[1]):
            best = (key, o)
    return '%s+%#x' % best if best else '%s+%#x' % (block, pos)


def diff_ranges(a, b):
    out, start = [], None
    for i in range(len(a)):
        if a[i] != b[i]:
            if start is None:
                start = i
        elif start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(a)))
    return out


def test(sav, tag, rom, base, shots):
    ref = os.path.join(base, tag, 'pokemonthyl.gba')
    if not os.path.exists(ref):
        return False, 'no reference ROM %s (run tools/qa/refroms.sh %s)' % (ref, tag)
    s_ref, b_ref = at_main_menu(ref, sav)
    s_cur, b_cur = at_main_menu(rom, sav)
    problems = []
    if s_ref != 1 or s_cur != 1:
        problems.append('save status ref=%d cur=%d (1 = OK)' % (s_ref, s_cur))
    for name, _, key in BLOCKS:
        for lo, hi in diff_ranges(b_ref[key], b_cur[key])[:8]:
            problems.append('%s differs at %s (%d bytes)' % (name, field_name(key, lo), hi - lo))
    verdict = 'IDENTICAL' if not problems else 'DIFFERENT'

    # Continue into the overworld on the current ROM.
    with Emu(rom, sav) as e:
        try:
            e.boot_continue()
        except TimeoutError as ex:
            problems.append('CONTINUE failed: %s' % ex)
        else:
            g, n, x, y = e.location()
            e.run(300)
            wg, wn = struct.unpack_from('<bb', b_cur['sb1'], off('sb1.location'))
            if (g, n) != (wg, wn):
                problems.append('continued on map %d.%d, save says %d.%d' % (g, n, wg, wn))
            if not (e.in_overworld() or e.in_battle()):
                problems.append('game left the overworld within 5 s of continuing')
        if shots:
            os.makedirs(shots, exist_ok=True)
            e.shot(os.path.join(shots, os.path.basename(sav) + '.png'))
    return not problems, '%s  (load %s)%s' % ('OK' if not problems else 'FAIL', verdict,
                                             ''.join('\n    ' + p for p in problems))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('pairs', nargs='*', help='SAVE:TAG (default: the table in this script)')
    ap.add_argument('--rom', default=os.path.join(REPO, 'pokemonthyl.gba'))
    ap.add_argument('--base', default=os.path.join(REPO, 'qa-base'))
    ap.add_argument('--shots', help='directory for a screenshot of each continued save')
    a = ap.parse_args()
    pairs = [tuple(p.rsplit(':', 1)) for p in a.pairs] or SAVES
    ok_all = True
    for sav, tag in pairs:
        path = sav if os.path.isabs(sav) else os.path.join(REPO, sav)
        if not os.path.exists(path):
            print('%-32s MISSING' % sav)
            ok_all = False
            continue
        ok, msg = test(path, tag, a.rom, a.base, a.shots)
        ok_all &= ok
        print('%-32s vs %-7s %s' % (os.path.basename(sav), tag, msg))
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
