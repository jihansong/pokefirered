#!/usr/bin/env python3
"""Emulator captures of the opening for review: the key moments, a side-by-side sheet
against the official FR/LG opening frames, and a GIF from power-on to the title screen.

    python3 tools/qa/opening_capture.py [rom] [--out docs/anim/drafts/storyboard-A/ingame]
        [--official docs/anim/drafts/storyboard-A/official]

The official frames are the vanilla FR/LG opening dumped from the qa-base ROM with
tools/qa/emu.py (never anything from reference/). Key moments are code frames t of the
opening (F = 706 + t); a picture set up at F is captured at F + 1.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from emu import Emu  # noqa: E402

START = 706
W, H = 240, 160
SHOTS = [  # shot, key code frames, official FR/LG frames of the beat it replaces
    ('S1 VERMILION GYM', (10, 60, 85, 122), (720, 746)),
    ('S2 the battle begins', (150, 190, 200, 205, 211), (790, 820)),
    ('S3 close-ups, face-off', (226, 244, 255, 275), (860, 920, 950)),
    ('S4 high-speed exchanges', (300, 309, 335, 344, 347, 384, 422), (1000, 1120, 1160)),
    ('S5 THUNDERBOLT', (455, 470, 481, 510), (1236, 1256)),
    ('S6 AGILITY', (519, 523, 528, 538, 543, 547, 560, 566, 585), (1280, 1300)),
    ('S7 the win, the song rings out', (600, 610, 620, 650, 684, 740), (1340, 1376, 1390, 1430)),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rom', nargs='?', default=os.path.join(FR, 'pokemonthyl.gba'))
    ap.add_argument('--out', default=os.path.join(FR, 'docs/anim/drafts/storyboard-A/ingame'))
    ap.add_argument('--official', default=os.path.join(FR, 'docs/anim/drafts/storyboard-A/official'))
    ap.add_argument('--gif-step', type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = {}
    title = None
    with Emu(a.rom) as e:
        names = {v & ~1: k for k, v in e.syms.items()}
        f = 0
        while f < 1600:
            e.run(1)
            f += 1
            frames[f] = Image.frombytes('RGB', (W, H), e.screen())
            if title is None and names.get(e.callback2() & ~1) == 'CB2_InitTitleScreen':
                title = f
            if title and f >= title + 40:
                break
    rows = []
    for shot, keys, orig in SHOTS:
        row = []
        for t in keys:
            F = START + t + 1
            im = frames[F]
            im.save(os.path.join(a.out, 'F%04d_t%03d.png' % (F, t)))
            row.append(('ROM F%d (t%d)' % (F, t), im))
        off = []
        for o in orig:
            p = os.path.join(a.official, '%04d.png' % o)
            if os.path.exists(p):
                off.append(('FR/LG F%d' % o, Image.open(p).convert('RGB')))
        rows.append((shot, off, row))
    for scale, fn in ((1, 'compare.png'), (2, 'compare_x2.png')):
        cw, ch = W * scale + 6, H * scale + 16
        cols = max(len(o) + len(r) for _, o, r in rows)
        sheet = Image.new('RGB', (cw * cols, (ch + 14) * len(rows) + 20), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        d.text((4, 4), 'Opening in the ROM (emulator captures) next to the FR/LG opening beat it replaces (vanilla ROM, emulator)', fill=(255, 255, 255))
        for r, (shot, off, row) in enumerate(rows):
            y = 20 + r * (ch + 14)
            d.text((4, y), shot, fill=(255, 220, 120))
            for c, (label, im) in enumerate(off + row):
                x = c * cw
                d.text((x + 2, y + 14), label, fill=(160, 200, 255) if c < len(off) else (255, 255, 255))
                sheet.paste(im.resize((W * scale, H * scale), Image.NEAREST), (x, y + 28))
        sheet.save(os.path.join(a.out, fn))
    # GIF: power-on to the title screen (and 40 frames of it)
    last = max(frames)
    seq = [frames[f].convert('P', palette=Image.ADAPTIVE, colors=255) for f in range(1, last + 1, a.gif_step)]
    dur = int(round(1000.0 * a.gif_step / 59.7275))
    seq[0].save(os.path.join(a.out, 'opening.gif'), save_all=True, append_images=seq[1:], duration=dur, loop=0, optimize=True)
    print('title screen F%s; %d key frames, compare.png, opening.gif (%d frames, %d ms each) in %s' % (
        title, sum(len(k) for _, k, _ in SHOTS), len(seq), dur, a.out))


if __name__ == '__main__':
    main()
