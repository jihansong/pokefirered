#!/usr/bin/env python3
"""Model sheets of the opening's characters, for the illustrator and art direction.

    python3 tools/make_intro_opening_models.py [--out docs/anim/models]

Writes, from the rule-built models (tools/intro_opening_pikachu.py,
tools/intro_opening_red.py):

- pikachu/<view>.png: every view at 1x (64x64, the close-up 128x128), transparent;
- pikachu/sheet-4x.png: all of PIKACHU's views at 4x, beside FR/LG's front sprite;
- red/<view>.png and red/sheet-4x.png: the same for RED, beside his FR/LG trainer
  pictures and overworld sprite;
- compare.png: one page, 1x and 4x: the approved front poses and the close-up next
  to the new back, side, run and jump views, and RED at the same scale;
- run-cycles.png: both run cycles laid out as film strips at 1x and 4x.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import intro_opening_pikachu as pika  # noqa: E402
import intro_opening_red as red  # noqa: E402
from intro_opening_art import to_image  # noqa: E402

BG = (150, 190, 230)


def rgba(rows, pal):
    im = to_image(rows, pal)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    mask = Image.frombytes('L', im.size, bytes(255 if v else 0 for v in im.getdata()))
    out.paste(im.convert('RGB'), (0, 0), mask)
    return out


def on_bg(im, scale=1):
    im = im.convert('RGBA')
    im = im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)
    out = Image.new('RGB', im.size, BG)
    out.paste(im, (0, 0), im)
    return out


def sheet(items, cols, scale, title, pad=6, bar=14):
    ims = [on_bg(im, scale) for im, _ in items]
    w = max(i.size[0] for i in ims)
    h = max(i.size[1] for i in ims)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new('RGB', (cols * (w + pad) + pad, bar + pad + rows * (h + bar + pad) + pad), (40, 40, 40))
    d = ImageDraw.Draw(out)
    d.text((pad, pad // 2), title, fill=(255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = pad + c * (w + pad), bar + pad + r * (h + bar + pad)
        d.text((x, y + 1), items[i][1], fill=(255, 255, 255))
        out.paste(im, (x, y + bar + (h - im.size[1])))
    return out


def stack(*parts):
    w = max(p.size[0] for p in parts)
    out = Image.new('RGB', (w, sum(p.size[1] for p in parts)), (40, 40, 40))
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.size[1]
    return out


def slug(name):
    return name.replace(', ', '-').replace(': ', '-').replace(' ', '-').replace('(', '').replace(')', '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/models'))
    a = ap.parse_args()
    pdir, rdir = os.path.join(a.out, 'pikachu'), os.path.join(a.out, 'red')
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(rdir, exist_ok=True)

    pv = pika.model_views()
    scene2 = pika.frames()
    pv = dict([('front B (snap)', scene2['B'])] + list(pv.items()))
    cu = pika.closeup_frames()
    pims = [(rgba(v, pika.PAL), n) for n, v in pv.items()]
    cims = [(rgba(cu['CU'], pika.PAL), 'close-up (2x)'), (rgba(cu['CU_hmph'], pika.PAL), 'close-up "hmph"')]
    for im, n in pims + cims:
        im.save(os.path.join(pdir, slug(n).replace('"', '') + '.png'))
    ref = Image.open(os.path.join(ROOT, 'graphics/pokemon/pikachu/front.png')).convert('RGBA')
    ref_items = [(Image.frombytes('RGBA', ref.size, bytes(
        b for px, idx in zip(ref.getdata(), Image.open(os.path.join(ROOT, 'graphics/pokemon/pikachu/front.png')).getdata())
        for b in (px[:3] + ((0,) if idx == 0 else (255,))))), 'FR/LG front.png')]
    sheet(ref_items + pims, 8, 4, 'PIKACHU model, 4x (tools/intro_opening_pikachu.py)').save(
        os.path.join(pdir, 'sheet-4x.png'))

    rv = red.model_views()
    rims = [(rgba(v, red.PAL), n) for n, v in rv.items()]
    for im, n in rims:
        im.save(os.path.join(rdir, slug(n) + '.png'))
    refs = []
    for path, box, label in (('graphics/trainers/front_pics/red_front_pic.png', None, 'FR/LG front pic'),
                             ('graphics/trainers/back_pics/red_back_pic.png', (0, 0, 64, 64), 'FR/LG back pic'),
                             ('graphics/object_events/pics/people/red_normal.png', (0, 0, 144, 32), 'FR/LG overworld')):
        im = Image.open(os.path.join(ROOT, path))
        idx = im.crop(box) if box else im
        rgb = idx.convert('RGBA')
        refs.append((Image.frombytes('RGBA', rgb.size, bytes(
            b for px, i in zip(rgb.getdata(), idx.getdata()) for b in (px[:3] + ((0,) if i == 0 else (255,))))), label))
    sheet(refs[:2] + rims, 4, 4, 'RED model, 4x (tools/intro_opening_red.py), beside his FR/LG pictures').save(
        os.path.join(rdir, 'sheet-4x.png'))

    # one page: 1x rows, then 4x of the key views
    ones = sheet(pims + cims + rims, 12, 1, 'All views at 1x (as the game shows them)')
    fours = sheet([(im, n) for im, n in pims if n in ('front A', 'front C', 'back', 'side', 'run 0', 'jump: air')]
                  + [(im, n) for im, n in rims if n in ('run 0', 'back')], 8, 4,
                  'Key views at 4x: approved front poses, new back / side / run / jump, RED')
    close = sheet(cims, 2, 2, 'The approved 2x close-up at 2x')
    stack(ones, fours, close).save(os.path.join(a.out, 'compare.png'))

    runs = [(im, 'PIKACHU ' + n) for im, n in pims if n.startswith('run')] + \
           [(im, 'RED ' + n) for im, n in rims if n.startswith('run')]
    stack(sheet(runs, 8, 1, 'Run cycles at 1x (4 frames each, loop)'),
          sheet(runs, 4, 4, 'Run cycles at 4x')).save(os.path.join(a.out, 'run-cycles.png'))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
