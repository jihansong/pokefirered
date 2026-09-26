#!/usr/bin/env python3
"""Measure the boot -> copyright -> intro -> title timeline of a built ROM, frame by frame.

    python3 tools/qa/intro_timeline.py [rom] [--frames N] [--skip-at F]
                                       [--dump DIR --from F --to F --step K]

Boots the ROM with no save and no input (or presses A once at --skip-at) and prints
every frame where one of these changes:

- gMain.callback2 (the main callback: copyright, CB2_Intro, title screen ...)
- the intro sequence callback and its state (src/intro.c IntroSequenceData:
  callback +0, state +4, timer +18; for the new opening, state = scene number 1..7)
- the song playing on the BGM player (gMPlayInfo_BGM.songHeader)

F is the frame counted from power on (the loop count, starting at 1 after the first
emulated frame). With --dump it also saves the screen of frames F in [from, to] every
`step` frames as DIR/FFFF.png, for contact sheets (tools/make_contact_sheet.py).

The last lines are a summary: the frame the BGM song MUS_INTRO_FIGHT starts and
ends, the frame the intro callback becomes IntroCB_ExitToTitleScreen and the frame
the title screen (CB2_InitTitleScreen) is reached.
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu import Emu  # noqa: E402

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
TASK_SIZE, NUM_TASKS = 0x28, 16


def rev(syms):
    out = {}
    for k, v in syms.items():
        out.setdefault(v & ~1, k)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(FR, 'pokemonthyl.gba'))
    ap.add_argument('--frames', type=int, default=1700)
    ap.add_argument('--skip-at', type=int, default=None, help='press A (3 frames) at this frame')
    ap.add_argument('--dump', default=None)
    ap.add_argument('--from', dest='dfrom', type=int, default=0)
    ap.add_argument('--to', dest='dto', type=int, default=0)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--quiet', action='store_true', help='only print the summary')
    a = ap.parse_args()

    with Emu(a.rom, None) as e:
        s = e.syms
        names = rev(s)
        task_fn = s['Task_CallIntroCallback'] & ~1
        bgm = s['gMPlayInfo_BGM']
        songs = {}
        for k, v in s.items():
            if k.startswith('mus_') or k.startswith('se_'):
                songs[v] = k
        last = {}
        events = []
        summary = {}
        if a.dump:
            os.makedirs(a.dump, exist_ok=True)
        for f in range(1, a.frames + 1):
            if a.skip_at is not None and f == a.skip_at:
                e.hold('A')
            if a.skip_at is not None and f == a.skip_at + 3:
                e.hold()
            e.run(1)
            cur = {}
            cb2 = e.callback2() & ~1
            cur['cb2'] = names.get(cb2, hex(cb2))
            icb = None
            for t in range(NUM_TASKS):
                base = s['gTasks'] + t * TASK_SIZE
                fn, active = struct.unpack('<IB', e.read(base, 5))
                if active and (fn & ~1) == task_fn:
                    ptr = struct.unpack('<I', e.read(base + 8, 4))[0]
                    cb, st = struct.unpack('<IB', e.read(ptr, 5))
                    icb = (names.get(cb & ~1, hex(cb)), st)
                    break
            cur['intro'] = icb
            hdr, status = struct.unpack('<II', e.read(bgm, 8))
            playing = hdr and (status & 0xFFFF) and not (status & 0x80000000)
            cur['bgm'] = songs.get(hdr, hex(hdr)) if playing else None
            for k, v in cur.items():
                if last.get(k, 'x') != v:
                    events.append((f, k, v))
                    if not a.quiet:
                        print('%5d  %-5s %s' % (f, k, v))
                    if k == 'bgm' and v == 'mus_intro_fight' and 'fight_start' not in summary:
                        summary['fight_start'] = f
                    if k == 'bgm' and last.get(k) == 'mus_intro_fight' and 'fight_end' not in summary:
                        summary['fight_end'] = f
                    if k == 'intro' and v and v[0] == 'IntroCB_ExitToTitleScreen' and 'exit' not in summary:
                        summary['exit'] = f
                    if k == 'intro' and v and v[0] == 'IntroCB_Opening' and 'opening' not in summary:
                        summary['opening'] = f
                    if k == 'intro' and v and v[0] == 'IntroCB_Scene1' and 'opening' not in summary:
                        summary['opening'] = f
                    if k == 'cb2' and v == 'CB2_InitTitleScreen' and 'title' not in summary:
                        summary['title'] = f
            last = cur
            if a.dump and a.dfrom <= f <= a.dto and (f - a.dfrom) % a.step == 0:
                e.shot(os.path.join(a.dump, '%04d.png' % f))
        print('summary: ' + ' '.join('%s=%s' % (k, summary.get(k)) for k in
                                     ('opening', 'fight_start', 'fight_end', 'exit', 'title')))


if __name__ == '__main__':
    main()
