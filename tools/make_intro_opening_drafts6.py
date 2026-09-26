#!/usr/bin/env python3
"""Review material for scene 6 of the opening (the rainbow), from the built ROM.

    python3 tools/make_intro_opening_drafts6.py [rom] [--out docs/anim/drafts/scene6-A]
        [--label A] [--wav-tool path/to/audiocap.py]

Captures F1280-1400 (the white-out of scene 5, scene 6, the start of scene 7) with no
save and no input and writes key frames (1x, 3x), emu-every3-scene6.png, cuts.png,
preview.gif (2x, 30 frames a second), preview.wav (with --wav-tool) and
contact-sheet.png. Scene 6 is seen at F1302-1378 (storyboard 3.7).
"""
import argparse
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from make_intro_opening_drafts45 import capture, labelled, stack  # noqa: E402

SPAN = (1280, 1400)
S6 = (1302, 1378)
KEYS = [(1306, '6a: out of the white: the rainbow over the hill'),
        (1316, '6a: RED and PIKACHU from behind, looking at it'),
        (1330, '6b: beat 2: the camera starts to tilt up'),
        (1345, '6b: the hill leaves the picture; HO-OH comes in high on the right'),
        (1352, '6c: HO-OH comes out, a golden silhouette, far off'),
        (1359, '6c: beat 4: over the top of the rainbow'),
        (1368, '6c: the sparkle trail'),
        (1378, '6c: last frame of scene 6')]
CUTS = [1300, 1301, 1302, 1303, 1377, 1378, 1379, 1380]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(ROOT, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/scene6-A'))
    ap.add_argument('--label', default='A')
    ap.add_argument('--wav-tool', default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    shots = capture(a.rom, set(range(SPAN[0], SPAN[1] + 1)))
    for i, (f, _) in enumerate(KEYS, 1):
        shots[f].save(os.path.join(a.out, 'key%02d_F%04d.png' % (i, f)))
        shots[f].resize((720, 480), Image.NEAREST).save(os.path.join(a.out, 'key%02d_F%04d_x3.png' % (i, f)))
    every = list(range(S6[0], S6[1] + 1, 3))
    labelled([shots[f] for f in every], ['F%d (t%d)' % (f, f - S6[0]) for f in every], 6, 1,
             'scene 6 draft %s in the emulator, every 3rd frame' % a.label).save(
        os.path.join(a.out, 'emu-every3-scene6.png'))
    labelled([shots[f] for f in CUTS], ['F%d' % f for f in CUTS], 2, 1,
             'cuts: into 6 (F1301|1302), into 7 (F1378|1379)').save(os.path.join(a.out, 'cuts.png'))
    frames = [shots[f].resize((480, 320), Image.NEAREST) for f in range(SPAN[0], SPAN[1] + 1, 2)]
    durations = [30 if i % 3 else 40 for i in range(len(frames))]
    frames[0].save(os.path.join(a.out, 'preview.gif'), save_all=True, append_images=frames[1:],
                   duration=durations, loop=0)
    if a.wav_tool:
        subprocess.check_call([sys.executable, a.wav_tool, a.rom, os.path.join(a.out, 'preview.wav'),
                               '--skip', str(SPAN[0] - 1), '--frames', str(SPAN[1] - SPAN[0] + 1), '--small'])
    keys = labelled([shots[f] for f, _ in KEYS], ['%d. F%d %s' % (i, f, t) for i, (f, t) in enumerate(KEYS, 1)],
                    4, 2, 'Thunder Yellow opening, scene 6 draft %s: the rainbow and HO-OH '
                          '(F1301-1377, bar 8 of MUS_INTRO_FIGHT)' % a.label)
    strip = labelled([shots[f] for f in range(S6[0], S6[1] + 1, 6)], ['F%d' % f for f in range(S6[0], S6[1] + 1, 6)],
                     7, 1, 'scene 6, every 6th frame')
    stack(keys, strip).save(os.path.join(a.out, 'contact-sheet.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
