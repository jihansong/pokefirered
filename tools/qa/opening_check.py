#!/usr/bin/env python3
"""Check the new opening in a built ROM against the tools' mock-ups and the timing.

    python3 tools/qa/opening_check.py [rom] --mock scene2=DIR [--mock scene4=DIR ...]
                                      [--skips 400,850,1000,1300]

- Boots the ROM with no save and no input, captures every frame of each named scene
  and compares it with the mock-up the scene's tool drew (DIR/tNN.png or tNNN.png, as
  `make_intro_opening_scene*.py --preview` writes them), in the GBA's 5-bit colour.
  A scene set up at code frame F is seen in the capture of F+1 (storyboard 3.7).
- Reports the frames the opening dropped (gOpeningDroppedFrames, must be 0) and
  where the title screen arrives (F1459 in the original).
- With --skips, presses A at each frame and reports when the title screen arrives
  (the original arrives the frame after the press).
"""
import argparse
import os
import sys

from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu import Emu  # noqa: E402

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SCENE_CODE_START = {'scene2': 842, 'scene4': 995, 'scene5': 1148}   # code frames
SCENE_FRAMES = {'scene2': 76, 'scene4': 153, 'scene5': 153}


def q(im):
    return im.convert('RGB').point(lambda v: (v >> 3) * 255 // 31)


def mock_path(d, t):
    for name in ('t%02d.png' % t, 't%03d.png' % t):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


def run(rom, mocks, frames=1470):
    want = {}
    for scene, d in mocks.items():
        f0 = SCENE_CODE_START[scene] + 1
        for t in range(SCENE_FRAMES[scene]):
            want[f0 + t] = (scene, t, d)
    shots = {}
    title = None
    with Emu(rom) as e:
        s = e.syms
        names = {v & ~1: k for k, v in s.items()}
        for f in range(1, frames + 1):
            e.run(1)
            if f in want:
                shots[f] = Image.frombytes('RGB', (240, 160), e.screen())
            if title is None and names.get(e.callback2() & ~1) == 'CB2_InitTitleScreen':
                title = f
            if f == 1456:
                dropped = e.u16(s['gOpeningDroppedFrames'])
    bad = {}
    for f, (scene, t, d) in sorted(want.items()):
        p = mock_path(d, t)
        if p is None:
            continue
        diff = ImageChops.difference(q(shots[f]), q(Image.open(p)))
        n = sum(1 for px in diff.getdata() if px != (0, 0, 0))
        if n:
            bad.setdefault(scene, []).append((t, n, diff.getbbox()))
    return bad, dropped, title


def skip_title(rom, at):
    with Emu(rom) as e:
        names = {v & ~1: k for k, v in e.syms.items()}
        for f in range(1, at + 200):
            if f == at:
                e.hold('A')
            if f == at + 3:
                e.hold()
            e.run(1)
            if names.get(e.callback2() & ~1) == 'CB2_InitTitleScreen':
                return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(FR, 'pokemonthyl.gba'))
    ap.add_argument('--mock', action='append', default=[], help='sceneN=DIR')
    ap.add_argument('--skips', default='')
    a = ap.parse_args()
    mocks = dict(m.split('=', 1) for m in a.mock)
    bad, dropped, title = run(a.rom, mocks)
    for scene in mocks:
        b = bad.get(scene, [])
        print('%s: %d of %d frames differ from the mock-ups %s' % (scene, len(b), SCENE_FRAMES[scene], b[:8]))
    print('dropped frames: %d' % dropped)
    print('title screen: F%s (original F1459)' % title)
    for at in [int(x) for x in a.skips.split(',') if x]:
        print('A at F%d -> title F%s (original F%d)' % (at, skip_title(a.rom, at), at + 1))


if __name__ == '__main__':
    main()
