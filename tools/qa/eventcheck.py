#!/usr/bin/env python3
"""Run scripted event checks: a save state, key presses, then screenshots and
memory checks, one case per line of a JSON-lines file.

    tools/qa/eventcheck.py tools/qa/cases/z2.jsonl [--shots DIR] [--only NAME]

A case:

    {"name": "wattson_rematch",
     "base": "saves/hoenn.sav",                      (default saves/hoenn.sav)
     "edit": ["warp MauvilleCity_Gym 5 3", "flag FLAG_HOENN_NEW_MAUVILLE_DONE 1"],
     "steps": ["UP", "A*3", "wait 60", "shot rematch", "expect var VAR_X = 2"]}

"edit" lines are savedit.py commands applied to a copy of the base save.
Steps, in order:
    A | B | START | SELECT | L | R      press once;  "A*5" presses five times
    UP | DOWN | LEFT | RIGHT [N]         face/walk N tiles (default 1)
    wait N                               run N frames
    mash [N]                             press A (at most N times, default 300)
                                         until the overworld is idle: no battle,
                                         no script running, the player free
    shot NAME                            save NAME.png (in --shots)
    expect flag NAME = 0|1               check a flag in the live game
    expect var NAME = N                  check a var in the live game
    expect trainer NAME = 0|1            check a trainer's beaten flag
    expect money = N                     check the player's money
    expect item ITEM = N                 check how many of ITEM the bag holds
    expect egg SPECIES = N               count EGGS of SPECIES in party and PC
    expect fateful SPECIES = N           count SPECIES (EGGS too) in party and PC
                                         with the fateful encounter bit (MEW's
                                         and DEOXYS's obedience)
    expect map MAP                       check the player's current map
    expect battle | expect overworld     check what the game is doing
The save is continued (title, CONTINUE, quest-log recap skipped) before the
first step. A case passes when every expect holds; screenshots are for eyes.
"xfail": true marks a negative control, which passes only if a check fails.
"""

import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emu import Emu, GameReset                    # noqa: E402
from gamedata import REPO, const, map_info, off   # noqa: E402
from savefile import Blocks, Mon                  # noqa: E402
import savedit                                    # noqa: E402

BUTTONS = {'A', 'B', 'START', 'SELECT', 'L', 'R'}
DIRS = {'UP', 'DOWN', 'LEFT', 'RIGHT'}


def live_blocks(e):
    return Blocks(e.read(e.ptr('gSaveBlock1Ptr'), off('sb1')), e.read(e.ptr('gSaveBlock2Ptr'), off('sb2')))


def live_mons(e):
    """The party (gPlayerParty, not the save's copy) and every PC box slot."""
    size = off('pokemon')
    party = bytearray(e.read(e.sym('gPlayerParty'), 6 * size))
    mons = [Mon(party, i * size) for i in range(e.u8(e.sym('gPlayerPartyCount')))]
    bsize = off('boxmon')
    n = const('TOTAL_BOXES_COUNT') * const('IN_BOX_COUNT')
    boxes = bytearray(e.read(e.ptr('gPokemonStoragePtr') + off('storage.boxes'), n * bsize))
    mons += [Mon(boxes, i * bsize) for i in range(n)]
    return [m for m in mons if m.has_species()]


def species_id(name):
    return const(name if name.startswith('SPECIES_') or name.isdigit() else 'SPECIES_' + name)


def run_case(case, rom, shots):
    name = case['name']
    base = case.get('base', 'saves/hoenn.sav')
    base = base if os.path.isabs(base) else os.path.join(REPO, base)
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        sav = os.path.join(tmp, 'case.sav')
        argv = [base, '-o', sav]
        for line in case.get('edit', []):
            argv += line.split()
        with open(os.devnull, 'w') as quiet:
            old, sys.stdout = sys.stdout, quiet
            try:
                rc = savedit.run(argv)
            finally:
                sys.stdout = old
        if rc:
            return False, ['savedit failed: %s' % ' '.join(argv[3:])]
        with Emu(rom, sav) as e:
            try:
                e.boot_continue()
            except (TimeoutError, GameReset) as ex:
                return False, ['could not continue: %s' % ex]
            for step in case.get('steps', []):
                p = step.split()
                head = p[0].upper()
                if head.split('*')[0] in BUTTONS:
                    key, _, times = head.partition('*')
                    for _ in range(int(times or 1)):
                        e.press(key, hold=3, after=20)
                elif head in DIRS:
                    e.walk(head, int(p[1]) if len(p) > 1 else 1)
                elif head == 'WAIT':
                    e.run(int(p[1]))
                elif head == 'MASH':
                    for _ in range(int(p[1]) if len(p) > 1 else 300):
                        if e.field_idle():
                            e.run(20)
                            if e.field_idle():
                                break
                        e.press('A', hold=3, after=20)
                    else:
                        fails.append('%s: the game never went idle' % step)
                elif head == 'SHOT':
                    if shots:
                        e.shot(os.path.join(shots, '%s_%s.png' % (name, p[1])))
                elif head == 'EXPECT':
                    what = p[1]
                    if what in ('flag', 'var', 'trainer'):
                        blocks = live_blocks(e)
                        want = int(p[4], 0)
                        got = {'flag': lambda n: int(blocks.flag(n)), 'var': blocks.var,
                               'trainer': lambda n: int(blocks.trainer_beaten(n))}[what](p[2])
                        if got != want:
                            fails.append('%s: %s %s is %d, expected %d' % (step, what, p[2], got, want))
                    elif what == 'money':
                        got, want = live_blocks(e).money(), int(p[3], 0)
                        if got != want:
                            fails.append('%s: money is %d' % (step, got))
                    elif what in ('item', 'egg', 'fateful'):
                        want = int(p[4], 0)
                        if what == 'item':
                            got = live_blocks(e).item_count(p[2])
                        else:
                            sp = species_id(p[2])
                            mons = [m for m in live_mons(e) if m.species() == sp]
                            got = sum(1 for m in mons if (m.is_egg() if what == 'egg' else m.fateful()))
                        if got != want:
                            fails.append('%s: %s %s is %d' % (step, what, p[2], got))
                    elif what == 'map':
                        m = map_info(p[2])
                        g, n, _, _ = e.location()
                        if (g, n) != (m['group'], m['num']):
                            fails.append('%s: on map %d.%d' % (step, g, n))
                    elif what == 'battle' and not e.in_battle():
                        fails.append('%s: not in a battle' % step)
                    elif what == 'overworld' and not e.in_overworld():
                        fails.append('%s: not in the overworld' % step)
                else:
                    fails.append('unknown step %r' % step)
                if e.reset_seen():
                    fails.append('game reset during %r' % step)
                    break
    return not fails, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cases', help='JSON-lines file of cases')
    ap.add_argument('--rom', default=os.path.join(REPO, 'pokemonthyl.gba'))
    ap.add_argument('--shots', help='directory for the cases\' screenshots')
    ap.add_argument('--only', help='run only the case with this name')
    a = ap.parse_args()
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
    total = passed = 0
    with open(a.cases) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            case = json.loads(line)
            if a.only and case['name'] != a.only:
                continue
            total += 1
            ok, fails = run_case(case, a.rom, a.shots)
            if case.get('xfail'):
                # a negative control: it must fail, or the checks prove nothing
                ok, fails = (not ok), (['expected to fail but passed'] if ok else [])
            passed += ok
            print('%-4s %s%s' % ('ok' if ok else 'FAIL', case['name'], ''.join('\n     ' + x for x in fails)),
                  flush=True)
    print('%d/%d cases passed' % (passed, total))
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
