#!/usr/bin/env python3
"""Check the opening in a built ROM against the tool's frames and the timing.

    python3 tools/qa/opening_check.py [rom] [--preview DIR] [--skips 400,850,1000,1290]
                                      [--dump DIR --keys 716,...]

- Boots the ROM with no save and no input and captures every frame of the opening.
  With --preview (tools/make_intro_opening_a.py --preview DIR writes DIR/c1 .. DIR/c13),
  every frame is compared with the frame the tool drew, in the GBA's 5-bit colour. A
  cut set up at code frame F is seen in the capture of F+1.
- Checks the screen's edge columns inside the letterbox: a black column at x 0 or 239
  while the columns next to it are not black (a shake leaving the picture) fails (R2-4).
- Reports the frames the opening dropped (gOpeningDroppedFrames, must be 0) and where
  the title screen arrives (F1459 in the original).
- With --skips, presses A at each frame and reports when the title screen arrives.
- With --dump, saves the captures of the listed frames (and --gif, every frame).
"""
import argparse
import os
import sys

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(FR, 'tools'))
from emu import Emu  # noqa: E402
import make_intro_opening_a as A  # noqa: E402

START = 706                       # code frame 0 of the opening
TITLE_EXPECTED = 1459             # as FR/LG: exit at F1457, the title screen two frames later
LAST = 1470


def q(im):
    return im.convert('RGB').point(lambda v: (v >> 3) * 255 // 31)


def edge_black(im):
    px = im.load()
    rows = range(32, 128)
    out = []
    for x, nx in ((0, 1), (239, 238)):
        col = all(px[x, y] == (0, 0, 0) for y in rows)
        ncol = all(px[nx, y] == (0, 0, 0) for y in rows)
        if col and not ncol:
            out.append(x)
    return out


def run(rom, keep=None):
    shots = {}
    title = dropped = None
    with Emu(rom) as e:
        s = e.syms
        names = {v & ~1: k for k, v in s.items()}
        for f in range(1, LAST + 1):
            e.run(1)
            if f >= START and (keep is None or f in keep):
                shots[f] = Image.frombytes('RGB', (240, 160), e.screen())
            if title is None and names.get(e.callback2() & ~1) == 'CB2_InitTitleScreen':
                title = f
                dropped = e.u16(s['gOpeningDroppedFrames'])
    return shots, title, dropped


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
    ap.add_argument('--preview', default=None)
    ap.add_argument('--skips', default='')
    ap.add_argument('--dump', default=None)
    ap.add_argument('--keys', default='')
    a = ap.parse_args()
    shots, title, dropped = run(a.rom)
    bad_total = 0
    if a.preview:
        for name, start, frames, title_ in A.CUTS:
            bad = []
            for t in range(frames):
                p = os.path.join(a.preview, name, 't%03d.png' % t)
                f = START + start + t + 1
                if not os.path.exists(p) or f not in shots:
                    continue
                diff = ImageChops.difference(q(shots[f]), q(Image.open(p)))
                n = sum(1 for px in diff.getdata() if px != (0, 0, 0))
                if n:
                    bad.append((t, n, diff.getbbox()))
            bad_total += len(bad)
            print('%-4s %-22s %3d of %3d frames differ from the tool %s' % (name, title_, len(bad), frames, bad[:6]))
    edges = [(f, x) for f, im in sorted(shots.items()) if f <= START + A.END and edge_black(im) for x in edge_black(im)]
    print('black edge columns inside the letterbox: %d %s' % (len(edges), edges[:10]))
    print('frames captured: %d (F%d-F%d)' % (len(shots), min(shots), max(shots)))
    print('dropped frames: %s' % dropped)
    print('title screen: F%s (expected F%d; FR/LG original F1459)' % (title, TITLE_EXPECTED))
    for at in [int(x) for x in a.skips.split(',') if x]:
        print('A at F%d -> title F%s (original F%d)' % (at, skip_title(a.rom, at), at + 1))
    if a.dump:
        os.makedirs(a.dump, exist_ok=True)
        for f in [int(x) for x in a.keys.split(',') if x]:
            shots[f].save(os.path.join(a.dump, '%04d.png' % f))
    ok = (dropped == 0 and title == TITLE_EXPECTED and not edges and bad_total == 0)
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
