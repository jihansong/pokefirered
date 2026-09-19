#!/usr/bin/env python3
"""Generates the airplane flight scene art (graphics/airplane): indexed PNGs,
JASC palettes and tilemaps. Pixel art in the style of the GBA games: limited
palettes, dark outlines, 2-3 shade shading."""
import math, struct, os
from PIL import Image
OUT = os.path.join(os.path.dirname(__file__), '../../graphics/airplane')

def save_pal(path, cols):
    cols = list(cols) + [(0, 0, 0)] * (16 - len(cols))
    with open(path, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g} {b}\n' for r, g, b in cols))

def save_png(path, px, pal):
    h, w = len(px), len(px[0])
    im = Image.new('P', (w, h)); im.putpalette([c for rgb in (list(pal) + [(0, 0, 0)] * (16 - len(pal))) for c in rgb])
    for y in range(h):
        for x in range(w): im.putpixel((x, y), px[y][x])
    im.save(path)

def tiles_from(px, dedupe=True):
    """Split a pixel grid into 8x8 tiles; returns (tile list, tilemap of indices)"""
    h, w = len(px), len(px[0]); tiles, index, tmap = [], {}, []
    for ty in range(h // 8):
        row = []
        for tx in range(w // 8):
            t = tuple(tuple(px[ty*8+y][tx*8+x] for x in range(8)) for y in range(8))
            if dedupe and t in index: row.append(index[t])
            else:
                index[t] = len(tiles); tiles.append(t); row.append(index[t])
        tmap.append(row)
    return tiles, tmap

def tiles_png(path, tiles, pal):
    n = len(tiles); cols = 16; rows = (n + cols - 1) // cols
    px = [[0] * (cols * 8) for _ in range(rows * 8)]
    for i, t in enumerate(tiles):
        for y in range(8):
            for x in range(8): px[(i // cols) * 8 + y][(i % cols) * 8 + x] = t[y][x]
    save_png(path, px, pal)

def save_tilemap(path, tmap, pal_num, w=32, h=32):
    data = []
    for y in range(h):
        for x in range(w):
            t = tmap[y][x] if y < len(tmap) and x < len(tmap[0]) else 0
            data.append(t | (pal_num << 12))
    open(path, 'wb').write(struct.pack(f'<{len(data)}H', *data))

# ---------------------------------------------------------------- sky (BG3)
SKY = [(0, 0, 0), (248, 248, 255), (232, 240, 255), (208, 228, 255), (184, 216, 255), (160, 200, 248), (136, 184, 240),
       (112, 168, 232), (96, 152, 224), (80, 136, 216), (255, 255, 255), (224, 232, 248), (192, 208, 240)]
def make_sky():
    W, H = 256, 256
    px = [[0] * W for _ in range(H)]
    for y in range(H):
        # gradient from deep blue at the top to pale near the horizon (y ~ 150), dithered between bands
        t = min(1.0, y / 150.0)
        band = 9 - t * 8
        for x in range(W):
            b = int(band); frac = band - b
            px[y][x] = max(1, min(9, b + (1 if ((x + y) % 2 == 0 and frac > 0.5) else 0)))
    # distant clouds: thin flat streaks
    for cx, cy, ln in ((30, 40, 50), (150, 25, 70), (90, 80, 40), (200, 95, 60), (20, 115, 45), (130, 130, 80)):
        for dy in range(3):
            for x in range(cx - ln // 2 + dy * 4, cx + ln // 2 - dy * 4):
                px[cy + dy][x % W] = 11 if dy else 10
    tiles, tmap = tiles_from(px)
    tiles_png(f'{OUT}/sky.png', tiles, SKY); save_pal(f'{OUT}/sky.pal', SKY); save_tilemap(f'{OUT}/sky_tilemap.bin', tmap, 0)
    return len(tiles)

# ------------------------------------------------------------ clouds (BG2)
CLOUD = [(0, 0, 0), (255, 255, 255), (240, 244, 255), (216, 224, 248), (184, 200, 232), (136, 152, 200)]
def blob(px, cx, cy, parts):
    W, H = len(px[0]), len(px)
    for (ox, oy, r) in parts:
        for y in range(int(cy + oy - r) - 1, int(cy + oy + r) + 2):
            for x in range(int(cx + ox - r) - 1, int(cx + ox + r) + 2):
                if 0 <= y < H and math.hypot(x - cx - ox, y - cy - oy) <= r:
                    px[y][x % W] = 1
def shade_clouds(px):
    W, H = len(px[0]), len(px)
    out = [row[:] for row in px]
    for y in range(H):
        for x in range(W):
            if px[y][x]:
                below = y + 2 < H and px[y + 2][x] == 0
                below1 = y + 1 < H and px[y + 1][x] == 0
                above = y - 1 >= 0 and px[y - 1][x] == 0
                if below1: out[y][x] = 5
                elif below: out[y][x] = 4
                elif y + 4 < H and px[y + 4][x] == 0: out[y][x] = 3
                elif above: out[y][x] = 1
                else: out[y][x] = 2
    return out
def make_clouds():
    W, H = 256, 256
    px = [[0] * W for _ in range(H)]
    for cx, cy, s in ((40, 30, 1.0), (170, 55, 1.3), (100, 100, 0.8), (230, 120, 1.1), (60, 150, 1.2), (160, 175, 0.9), (20, 210, 1.0), (200, 230, 1.2)):
        blob(px, cx, cy, [(-14 * s, 3, 7 * s), (-4 * s, -3, 10 * s), (8 * s, -1, 8 * s), (17 * s, 4, 6 * s), (2 * s, 5, 8 * s)])
        for x in range(int(cx - 20 * s), int(cx + 22 * s)):   # flat bottom
            for y in range(int(cy + 5), int(cy + 24)):
                if 0 <= y < H: px[y][x % W] = 0
    px = shade_clouds(px)
    tiles, tmap = tiles_from(px)
    tiles_png(f'{OUT}/clouds.png', tiles, CLOUD); save_pal(f'{OUT}/clouds.pal', CLOUD); save_tilemap(f'{OUT}/clouds_tilemap.bin', tmap, 1)
    return len(tiles)

# ------------------------------------------------------- runway ground (BG1)
GROUND = [(0, 0, 0), (112, 200, 96), (80, 168, 72), (56, 128, 56), (104, 104, 112), (88, 88, 96), (72, 72, 80),
          (248, 248, 248), (248, 208, 64), (40, 40, 48), (176, 176, 184), (144, 144, 152)]
def make_ground():
    W, H = 256, 256
    px = [[0] * W for _ in range(H)]
    top = 200   # ground starts here in the 256-high map; the BG is scrolled so it sits at the bottom of the screen
    for y in range(top, H):
        for x in range(W):
            d = y - top
            if d < 2: c = 3
            elif d < 10: c = 1 if (x // 2 + d) % 5 else 2
            elif d < 12: c = 10
            elif d < 36:
                c = 4 if ((x * 7 + y * 3) % 11) else 5
                if 22 <= d <= 23 and (x // 16) % 2 == 0: c = 7          # centre line dashes
                if d in (13, 34): c = 7                                    # edge lines
            elif d < 38: c = 10
            else: c = 1 if (x // 3 + d) % 6 else 2
            px[y][x] = c
    # the terminal and control tower behind the runway
    bx0, bx1, btop = 120, 216, top - 22
    for y in range(btop, top):
        for x in range(bx0, bx1):
            c = 10 if y < btop + 2 else 11
            if btop + 5 <= y <= btop + 9 and (x - bx0) % 8 < 5: c = 6
            if btop + 13 <= y <= btop + 17 and (x - bx0) % 8 < 5: c = 6
            if x in (bx0, bx1 - 1) or y == btop: c = 9
            px[y][x] = c
    for y in range(top - 46, btop):                    # tower shaft
        for x in range(96, 104): px[y][x] = 9 if x in (96, 103) else 11
    for y in range(top - 54, top - 44):                # tower cab
        for x in range(92, 108): px[y][x] = 9 if (x in (92, 107) or y in (top - 54, top - 45)) else (6 if y < top - 48 else 10)
    for y in range(btop - 1, top):
        for x in range(96, 104): px[y][x] = 9 if x in (96, 103) else 11
    # runway lights along the edges
    for x in range(4, W, 32):
        for (yy, col) in ((top + 12, 8), (top + 36, 8)):
            px[yy][x] = col; px[yy][x + 1] = col
    tiles, tmap = tiles_from(px)
    tiles_png(f'{OUT}/ground.png', tiles, GROUND); save_pal(f'{OUT}/ground.pal', GROUND); save_tilemap(f'{OUT}/ground_tilemap.bin', tmap, 2)
    return len(tiles)

# ------------------------------------------------------ airplane (sprite)
PLANE = [(0, 0, 0), (40, 40, 56), (248, 248, 248), (216, 224, 232), (176, 184, 200), (128, 136, 160),
         (56, 104, 200), (32, 72, 160), (232, 64, 56), (168, 32, 40), (152, 208, 248), (96, 152, 216), (248, 208, 64)]
def plane_frame(pitch):
    W, H = 64, 32
    px = [[0] * W for _ in range(H)]
    def put(x, y, c):
        x, y = int(round(x)), int(round(y + (32 - x) * pitch))
        if 0 <= x < W and 0 <= y < H: px[y][x] = c
    # fuselage: a long rounded capsule, nose on the right
    for x in range(4, 60):
        # half height along the body
        if x < 12: hh = 2 + (x - 4) * 0.45          # tail cone
        elif x > 52: hh = 5.5 - (x - 52) * 0.55      # nose
        else: hh = 5.5
        cy = 17
        for y in range(int(cy - hh), int(cy + hh) + 1):
            d = (y - (cy - hh)) / max(1, 2 * hh)
            c = 2 if d < 0.35 else (3 if d < 0.65 else 4)
            if 0.55 <= d < 0.72 and 12 <= x <= 56: c = 6       # blue stripe
            if 0.72 <= d < 0.8 and 12 <= x <= 54: c = 7
            put(x, y, c)
        put(x, cy - hh - 1, 1); put(x, cy + hh + 1, 1)
    # windows
    for x in range(16, 50, 3):
        put(x, 15, 10); put(x, 14, 11)
    # cockpit window
    for x, y in ((54, 14), (55, 14), (56, 15), (53, 14)): put(x, y, 11)
    # tail fin with a POKé BALL mark, swept back and joined to the body
    for x in range(3, 16):
        top = 3 + max(0, (x - 3)) * 0.9 if x > 9 else 3
        bottom = 17 - (2 + max(0, x - 4) * 0.45) if x < 12 else 12
        for y in range(int(top), int(bottom) + 1):
            put(x, y, 6 if x > 4 else 7)
        put(x, int(top) - 1, 1)
    for y in range(3, 14): put(2, y, 1)
    for x, y, c in ((7, 6, 8), (8, 6, 8), (9, 6, 8), (7, 7, 9), (8, 7, 1), (9, 7, 2), (7, 8, 2), (8, 8, 2), (9, 8, 3)): put(x, y, c)
    put(3, 11, 1)
    # wing (seen from the side: a swept shape under the body) and engine
    for x in range(22, 40):
        y0 = 20 + (x - 22) * 0.15
        for y in range(int(y0), int(y0) + 3):
            put(x, y, 4 if y == int(y0) else 5)
        put(x, int(y0) + 3, 1)
    for x in range(30, 40):
        for y in range(22, 26):
            put(x, y, 3 if y < 24 else 5)
        put(x, 26, 1)
    put(39, 23, 1); put(39, 24, 1); put(30, 23, 12)
    # horizontal stabiliser
    for x in range(4, 12): put(x, 16, 4); put(x, 17, 5)
    return px
def rotate(px, deg):
    W, H = len(px[0]), len(px); a = math.radians(deg); cx, cy = W / 2, H / 2 + 2
    out = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            sx = math.cos(a) * (x - cx) + math.sin(a) * (y - cy) + cx
            sy = -math.sin(a) * (x - cx) + math.cos(a) * (y - cy) + cy
            ix, iy = int(round(sx)), int(round(sy))
            if 0 <= ix < W and 0 <= iy < H: out[y][x] = px[iy][ix]
    return out
def make_plane():
    level = plane_frame(0.0)
    frames = [level, rotate(level, -8)]
    px = [row for f in frames for row in f]           # 64x64: frame 0 above frame 1
    # store as 1D sprite sheet order: each 64x32 frame is 8x4 tiles, row-major
    tiles = []
    for f in frames:
        t, _ = tiles_from(f, dedupe=False); tiles += t
    tiles_png(f'{OUT}/plane.png', tiles, PLANE); save_pal(f'{OUT}/plane.pal', PLANE)
    save_png(f'{OUT}/plane_preview.png', px, PLANE)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print('sky tiles', make_sky(), 'cloud tiles', make_clouds(), 'ground tiles', make_ground())
    make_plane()
