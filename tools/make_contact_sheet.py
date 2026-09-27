#!/usr/bin/env python3
"""Put screenshots side by side with a caption over each, for reviewing animation.

    python3 tools/make_contact_sheet.py OUT.png IMG... [--cols N] [--scale K]
                                        [--labels "a,b,..."] [--title TEXT]

Captions default to the file names without extension. Images are enlarged by
--scale with nearest-neighbour so pixels stay sharp.
"""
import argparse
import os

from PIL import Image, ImageDraw


def sheet(paths, cols=4, scale=1, labels=None, title=None, pad=6, bar=12):
    ims = [Image.open(p).convert('RGB') for p in paths]
    ims = [im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST) for im in ims]
    w = max(im.size[0] for im in ims)
    h = max(im.size[1] for im in ims)
    rows = (len(ims) + cols - 1) // cols
    top = bar + pad if title else 0
    out = Image.new('RGB', (cols * (w + pad) + pad, top + rows * (h + bar + pad) + pad), (40, 40, 40))
    d = ImageDraw.Draw(out)
    if title:
        d.text((pad, pad // 2), title, fill=(255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = pad + c * (w + pad), top + pad + r * (h + bar + pad)
        label = labels[i] if labels else os.path.splitext(os.path.basename(paths[i]))[0]
        d.text((x, y), label, fill=(255, 255, 255))
        out.paste(im, (x, y + bar))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('images', nargs='+')
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--scale', type=int, default=1)
    ap.add_argument('--labels', default=None)
    ap.add_argument('--title', default=None)
    a = ap.parse_args()
    labels = a.labels.split(',') if a.labels else None
    sheet(a.images, a.cols, a.scale, labels, a.title).save(a.out)


if __name__ == '__main__':
    main()
