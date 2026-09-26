#!/usr/bin/env python3
"""Load official GBA graphics (4bpp tile sheets, tilemaps, JASC/GBA palettes) as PIL images,
for mock-ups built only from official art (animator direction change, 2026-09-26).

Nothing here draws: it only decodes tiles + tilemap + palette the way the hardware does.
"""
import os
import struct

from PIL import Image

EMERALD = '/root/src/pokeemerald'
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def path(p):
    if p.startswith('EM:'):
        return os.path.join(EMERALD, p[3:])
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def read_pal(p):
    """A palette as a list of RGB tuples (JASC .pal, .gbapal or the palette of a PNG)."""
    p = path(p)
    if p.endswith('.png'):
        flat = Image.open(p).getpalette()
        return [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
    if p.endswith('.gbapal'):
        raw = open(p, 'rb').read()
        out = []
        for (v,) in struct.iter_unpack('<H', raw):
            out.append(tuple(((v >> s) & 31) * 255 // 31 for s in (0, 5, 10)))
        return out
    lines = open(p).read().split()
    n = int(lines[2])
    return [tuple(int(v) for v in lines[3 + 3 * i:6 + 3 * i]) for i in range(n)]


def tiles(p):
    """The 8x8 tiles of a sheet, left to right, top to bottom, as index lists."""
    im = Image.open(path(p))
    w, h = im.size
    px = im.load()
    out = []
    for ty in range(h // 8):
        for tx in range(w // 8):
            out.append([[px[tx * 8 + x, ty * 8 + y] & 15 for x in range(8)] for y in range(8)])
    return out


def render_map(tile_png, map_bin, pal, width=32, transparent=True, palbanks=None, base=None):
    """Render a text-BG tilemap. pal: list of colours (16 per bank, bank 0 first) or a dict
    {bank: 16 colours}. Index 0 is transparent when transparent is set."""
    ts = tiles(tile_png)
    raw = open(path(map_bin), 'rb').read()
    ents = [v for (v,) in struct.iter_unpack('<H', raw)]
    rows = len(ents) // width
    img = Image.new('RGBA', (width * 8, rows * 8), (0, 0, 0, 0))
    # palettes are loaded at the map's lowest bank when the file has fewer banks than used
    used = sorted({e >> 12 for e in ents if 0 < (e & 0x3FF) < len(ts)})
    shift = used[0] if used and not isinstance(pal, dict) and len(pal) < (used[-1] + 1) * 16 else 0
    if base is not None:
        shift = base
    px = img.load()
    for i, e in enumerate(ents):
        t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        if t >= len(ts):
            continue
        if isinstance(pal, dict):
            cols = pal.get(bank, pal.get('default'))
        else:
            b = bank - shift
            cols = pal[b * 16:b * 16 + 16] if len(pal) > 16 and 0 <= b and len(pal) >= b * 16 + 16 else pal[:16]
        if palbanks is not None:
            cols = palbanks(bank)
        # 64-wide maps are stored as two 32x32 screens
        if width == 64:
            scr, k = divmod(i, 1024)
            ty, tx = divmod(k, 32)
            tx += 32 * scr
        else:
            ty, tx = divmod(i, width)
        tile = ts[t]
        for y in range(8):
            for x in range(8):
                c = tile[7 - y if vf else y][7 - x if hf else x]
                if c == 0 and transparent:
                    continue
                px[tx * 8 + x, ty * 8 + y] = cols[c] + (255,)
    return img


def sprite(p, frame=0, w=None, h=None, pal=None):
    """One frame (stacked vertically, or horizontally for field sprites) of a sprite
    sheet as RGBA with index 0 transparent."""
    im = Image.open(path(p))
    W, H = im.size
    w = w or W
    h = h or w
    if H >= W and h < H:
        box = (0, frame * h, w, frame * h + h)
    else:
        box = (frame * w, 0, frame * w + w, h)
    part = im.crop(box)
    cols = read_pal(pal) if pal else read_pal(p)
    out = Image.new('RGBA', part.size, (0, 0, 0, 0))
    src, dst = part.load(), out.load()
    for y in range(part.size[1]):
        for x in range(part.size[0]):
            c = src[x, y]
            if c & 15:
                dst[x, y] = tuple(cols[c]) + (255,) if c < len(cols) else (255, 0, 255, 255)
    return out


def render_layout(layout_dir, primary, secondary, width, pal_tint=None):
    """Render a map layout (data/layouts/X/map.bin) with its FR tilesets: 16x16 metatiles,
    primary tiles/metatiles/palettes 0-639 and banks 0-6, secondary from 640 and banks 7-12."""
    def tileset(d):
        ts = tiles(d + '/tiles.png')
        mt = [v for (v,) in struct.iter_unpack('<H', open(path(d + '/metatiles.bin'), 'rb').read())]
        return ts, [mt[i:i + 8] for i in range(0, len(mt), 8)]
    pt, pm = tileset(primary)
    st, sm = tileset(secondary)
    pals = []
    for i in range(16):
        f = primary if i < 7 else secondary
        pp = path('%s/palettes/%02d.pal' % (f, i))
        pals.append(read_pal(pp)[:16] if os.path.exists(pp) else [(0, 0, 0)] * 16)
    blocks = [v & 0x3FF for (v,) in struct.iter_unpack('<H', open(path(layout_dir + '/map.bin'), 'rb').read())]
    height = len(blocks) // width
    img = Image.new('RGB', (width * 16, height * 16))
    px = img.load()
    for bi, m in enumerate(blocks):
        meta = pm[m] if m < 640 else sm[m - 640]
        by, bx = divmod(bi, width)
        for layer in range(2):
            for q in range(4):
                e = meta[layer * 4 + q]
                t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
                tile = pt[t] if t < 640 else st[t - 640] if t - 640 < len(st) else None
                if tile is None:
                    continue
                ox, oy = bx * 16 + (q & 1) * 8, by * 16 + (q >> 1) * 8
                for y in range(8):
                    for x in range(8):
                        c = tile[7 - y if vf else y][7 - x if hf else x]
                        if c == 0 and layer:
                            continue
                        px[ox + x, oy + y] = pals[bank][c]
    return img
