#!/usr/bin/env python3
"""The title screen must look the same however the opening ended.

    python3 tools/qa/opening_title_check.py [rom] --skips 870,1120,1280

For no skip and for A pressed at each frame given, captures the screen a fixed
number of frames after the title screen starts and compares the captures: they must
be identical (the opening must leave no layer, scroll, window or palette behind).
"""
import argparse
import os
import sys

from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu import Emu  # noqa: E402

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
AFTER = 240


def title_shot(rom, skip):
    with Emu(rom) as e:
        names = {v & ~1: k for k, v in e.syms.items()}
        start = None
        f = 0
        while True:
            f += 1
            if skip and f == skip:
                e.hold('A')
            if skip and f == skip + 3:
                e.hold()
            e.run(1)
            if start is None and names.get(e.callback2() & ~1) == 'CB2_InitTitleScreen':
                start = f
            if start is not None and f == start + AFTER:
                return Image.frombytes('RGB', (240, 160), e.screen())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(FR, 'pokemonthyl.gba'))
    ap.add_argument('--skips', default='870,1120,1280')
    a = ap.parse_args()
    base = title_shot(a.rom, None)
    for at in [int(x) for x in a.skips.split(',') if x]:
        box = ImageChops.difference(base, title_shot(a.rom, at)).getbbox()
        print('A at F%d: title screen %s' % (at, 'identical' if box is None else 'DIFFERS in %s' % (box,)))


if __name__ == '__main__':
    main()
