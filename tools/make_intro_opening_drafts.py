#!/usr/bin/env python3
"""Review material for scene 2 of the opening, from the built ROM.

    python3 tools/make_intro_opening_drafts.py [rom] [--out docs/anim/drafts/scene2]

Boots the ROM with no save and no input in the headless emulator (tools/qa/emu.py),
captures every frame of scene 2 plus the frames around its two cuts, and writes:

- keyN_FXXXX.png and keyN_FXXXX_x3.png: the key frames, 240x160 and 3x;
- emu-every3.png: every third frame of the scene (F843-918) as captured;
- cuts.png: the two frames either side of each cut (no blank or mixed frame);
- models.png: the PIKACHU poses, the forearm, ball, spark and bolt frames, 4x;
- contact-sheet.png: one page with all of the above for the user.

A capture named F shows the picture the game drew during frame F after power on,
the frame after the one on which the code set it up (so the cut set at F842 is
seen from F843).
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, 'qa'))
sys.path.insert(0, HERE)
from emu import Emu  # noqa: E402
import make_intro_opening_scene2 as s2  # noqa: E402
from intro_opening_art import to_image, enlarge  # noqa: E402

FIRST, LAST = 843, 918           # captures showing scene 2 (set up at F842-917)
KEYS = [(857, 'the hand holds the ball out'),
        (863, 'beat 2: the ball opens, PIKACHU snaps away'),
        (866, 'the zap'),
        (874, 'the ball flies, the hand springs open'),
        (881, 'beat 3: the ball hits the desk'),
        (901, 'beat 4: sulking, cheeks crackle')]
CUTS = [841, 842, 843, 844, 917, 918, 919, 920]


def capture(rom, frames):
    shots = {}
    with Emu(rom) as e:
        for f in range(1, max(frames) + 1):
            e.run(1)
            if f in frames:
                shots[f] = Image.frombytes('RGB', (240, 160), e.screen())
    return shots


def labelled(images, labels, cols, scale, title=None, pad=6, bar=14, bg=(40, 40, 40)):
    ims = [im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST) for im in images]
    w = max(i.size[0] for i in ims)
    h = max(i.size[1] for i in ims)
    rows = (len(ims) + cols - 1) // cols
    top = bar + pad if title else 0
    out = Image.new('RGB', (cols * (w + pad) + pad, top + rows * (h + bar + pad) + pad), bg)
    d = ImageDraw.Draw(out)
    if title:
        d.text((pad, pad // 2), title, fill=(255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = pad + c * (w + pad), top + pad + r * (h + bar + pad)
        d.text((x, y + 1), labels[i], fill=(255, 255, 255))
        out.paste(im, (x, y + bar))
    return out


def models():
    art = s2.art()
    pieces = [(to_image(p, s2.PIKA_PAL), 'PIKACHU ' + n) for p, n in zip(art['pikachu'][0], 'ABC')]
    pieces += [(to_image(s2.arm('hold'), s2.PROP_PAL), 'arm: hold'),
               (to_image(s2.arm('open'), s2.PROP_PAL), 'arm: open')]
    pieces += [(to_image(b, s2.PROP_PAL), 'ball %d' % i) for i, b in enumerate(s2.ball_frames())]
    pieces += [(to_image(b, s2.PROP_PAL), 'spark %d' % i) for i, b in enumerate(s2.spark_frames())]
    pieces += [(to_image(b, s2.PROP_PAL), 'bolt %d' % i) for i, b in enumerate(s2.bolt_frames())]
    shown = []
    for im, label in pieces:
        canvas = Image.new('RGB', im.size, (150, 190, 230))
        mask = Image.frombytes('L', im.size, bytes(255 if v else 0 for v in im.getdata()))
        canvas.paste(im.convert('RGB'), (0, 0), mask)
        shown.append((canvas, label))
    top = labelled([c for c, _ in shown[:5]], [l for _, l in shown[:5]], 5, 4)
    bottom = labelled([c for c, _ in shown[5:]], [l for _, l in shown[5:]], 9, 4)
    out = Image.new('RGB', (max(top.size[0], bottom.size[0]), top.size[1] + bottom.size[1]), (40, 40, 40))
    out.paste(top, (0, 0))
    out.paste(bottom, (0, top.size[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(ROOT, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/scene2'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = set(range(FIRST, LAST + 1)) | set(CUTS) | {f for f, _ in KEYS}
    shots = capture(a.rom, frames)
    for i, (f, _) in enumerate(KEYS, 1):
        shots[f].save(os.path.join(a.out, 'key%d_F%04d.png' % (i, f)))
        enlarge(shots[f], 3).save(os.path.join(a.out, 'key%d_F%04d_x3.png' % (i, f)))
    every = list(range(FIRST, LAST + 1, 3))
    labelled([shots[f] for f in every], ['F%d (t%d)' % (f, f - FIRST) for f in every], 6, 1,
             'scene 2 in the emulator, every 3rd frame (t = frames since the cut)').save(
        os.path.join(a.out, 'emu-every3.png'))
    labelled([shots[f] for f in CUTS], ['F%d' % f for f in CUTS], 4, 1,
             'cuts: scene 1 -> 2 (F842/843) and 2 -> 3 (F918/919)').save(os.path.join(a.out, 'cuts.png'))
    m = models()
    m.save(os.path.join(a.out, 'models.png'))
    keys = labelled([shots[f] for f, _ in KEYS], ['%d. F%d %s' % (i, f, t) for i, (f, t) in enumerate(KEYS, 1)],
                    3, 2, 'Thunder Yellow opening, scene 2 draft A: the PIKACHU that hates POKe BALLS '
                          '(F842-917, 76 frames, bar 2 of MUS_INTRO_FIGHT)')
    strip = labelled([shots[f] for f in range(FIRST, LAST + 1, 6)],
                     ['F%d' % f for f in range(FIRST, LAST + 1, 6)], 13, 1, 'every 6th frame')
    w = max(keys.size[0], strip.size[0], m.size[0])
    sheet = Image.new('RGB', (w, keys.size[1] + strip.size[1] + m.size[1]), (40, 40, 40))
    y = 0
    for part in (keys, strip, m):
        sheet.paste(part, (0, y))
        y += part.size[1]
    sheet.save(os.path.join(a.out, 'contact-sheet.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
