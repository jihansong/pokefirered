#!/usr/bin/env python3
"""Shade the title screen PIKACHU (graphics/title_screen/leafgreen/box_art_mon.*) in
FR/LG's style.

Yellow's title PIKACHU is flat: a thick black outline, yellow, red cheeks. Its palette
already has a lighter and a darker yellow, a darker red and white that were never
used. This puts the picture together from its tiles and tilemap (Yellow's, kept in
tools/data), shades it like FR/LG's box art mons, lit from the upper left:

- yellow next to the outline on the lower right gets a two pixel band of the darker
  yellow, yellow next to it on the upper left the lighter yellow;
- the cheeks get the darker red along their lower right edge and a white shine;

then cuts it back into tiles (reusing flipped copies) and writes the tile sheet, the
tilemap and the tile count for graphics_file_rules.mk.
"""
import os, re, struct
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC_TILES = FR + '/tools/data/title_pikachu_yellow_tiles.png'
SRC_MAP = FR + '/tools/data/title_pikachu_yellow_map.bin'
OUT_TILES = FR + '/graphics/title_screen/leafgreen/box_art_mon.png'
OUT_MAP = FR + '/graphics/title_screen/leafgreen/box_art_mon.bin'
RULES = FR + '/graphics_file_rules.mk'

SKY, OUTLINE, WHITE, LIGHT, YELLOW, SHADE, RED, DARK_RED = 0, 1, 2, 3, 4, 5, 6, 7
MAP_W, MAP_H = 32, 20
XFLIP, YFLIP = 1 << 10, 1 << 11


def tiles_of(sheet):
    per_row = sheet.size[0] // 8
    n = per_row * (sheet.size[1] // 8)
    return [tuple(sheet.getpixel((c * 8 + x, r * 8 + y)) for y in range(8) for x in range(8))
            for r, c in (divmod(i, per_row) for i in range(n))]


def flip(tile, h, v):
    return tuple(tile[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))


def assemble(tiles, entries):
    img = Image.new('P', (MAP_W * 8, MAP_H * 8), SKY)
    for i, e in enumerate(entries):
        t = flip(tiles[e & 0x3FF], e & XFLIP, e & YFLIP)
        mx, my = (i % MAP_W) * 8, (i // MAP_W) * 8
        for k, c in enumerate(t):
            img.putpixel((mx + k % 8, my + k // 8), c)
    return img


def shade(src):
    out = src.copy()
    w, h = src.size
    px = lambda x, y: src.getpixel((x, y)) if 0 <= x < w and 0 <= y < h else SKY
    for y in range(h):
        for x in range(w):
            c = src.getpixel((x, y))
            if c == YELLOW:
                near_lr = OUTLINE in (px(x + 1, y), px(x, y + 1), px(x + 1, y + 1),
                                      px(x + 2, y), px(x, y + 2), px(x + 2, y + 2), px(x + 2, y + 1), px(x + 1, y + 2))
                near_ul = OUTLINE in (px(x - 1, y), px(x, y - 1), px(x - 1, y - 1))
                if near_lr and not near_ul:
                    out.putpixel((x, y), SHADE)
                elif near_ul and not near_lr:
                    out.putpixel((x, y), LIGHT)
            elif c == RED:
                if px(x + 1, y) != RED or px(x, y + 1) != RED:
                    out.putpixel((x, y), DARK_RED)
    # a shine on each cheek, up and to the left of its middle
    seen = set()
    for y in range(h):
        for x in range(w):
            if src.getpixel((x, y)) != RED or (x, y) in seen:
                continue
            stack, comp = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if n not in seen and px(*n) == RED:
                        seen.add(n)
                        stack.append(n)
            if len(comp) >= 20:
                xs, ys = [p[0] for p in comp], [p[1] for p in comp]
                sx, sy = min(xs) + (max(xs) - min(xs)) // 3, min(ys) + (max(ys) - min(ys)) // 3
                for dx, dy in ((0, 0), (1, 0), (0, 1)):
                    if (sx + dx, sy + dy) in comp:
                        out.putpixel((sx + dx, sy + dy), WHITE)
    return out


def split(img, palette_bits):
    uniq, entries = [], []
    blank = tuple([SKY] * 64)
    uniq.append(blank)                     # tile 0 stays the empty sky tile
    for i in range(MAP_W * MAP_H):
        mx, my = (i % MAP_W) * 8, (i // MAP_W) * 8
        t = tuple(img.getpixel((mx + k % 8, my + k // 8)) for k in range(64))
        entry = None
        for idx, u in enumerate(uniq):
            for h, v, bits in ((0, 0, 0), (1, 0, XFLIP), (0, 1, YFLIP), (1, 1, XFLIP | YFLIP)):
                if flip(u, h, v) == t:
                    entry = idx | bits
                    break
            if entry is not None:
                break
        if entry is None:
            uniq.append(t)
            entry = len(uniq) - 1
        entries.append(entry | palette_bits[i])
    return uniq, entries


def main():
    sheet = Image.open(SRC_TILES)
    raw = open(SRC_MAP, 'rb').read()
    src_entries = list(struct.unpack('<%dH' % (len(raw) // 2), raw))
    picture = assemble(tiles_of(sheet), src_entries)
    shaded = shade(picture)
    uniq, entries = split(shaded, [e & 0xF000 for e in src_entries])
    per_row = 12
    rows = (len(uniq) + per_row - 1) // per_row
    out = Image.new('P', (per_row * 8, rows * 8), SKY)
    out.putpalette(sheet.getpalette())
    for i, t in enumerate(uniq):
        r, c = divmod(i, per_row)
        for k, v in enumerate(t):
            out.putpixel((c * 8 + k % 8, r * 8 + k // 8), v)
    out.save(OUT_TILES)
    open(OUT_MAP, 'wb').write(struct.pack('<%dH' % len(entries), *entries))
    rules = open(RULES).read()
    rules = re.sub(r'(\$\(TITLESCREENGFXDIR\)/leafgreen/box_art_mon\.4bpp: %\.4bpp: %\.png\n\t\$\(GFX\) \$< \$@ -num_tiles )\d+',
                   r'\g<1>%d' % len(uniq), rules)
    open(RULES, 'w').write(rules)
    print(f'{len(uniq)} tiles, colors {sorted(set(shaded.getdata()))}')


if __name__ == '__main__':
    main()
