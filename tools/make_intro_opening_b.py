#!/usr/bin/env python3
"""The Thunder Yellow opening, plan B (docs/anim/opening-storyboard-B.md): five cuts made
only of official graphics already in this repository. This tool does the direction:
it takes the official tiles, maps, sprites and palettes, places them, times them and
writes the tables the opening's player (src/intro_opening.c) runs.

    python3 tools/make_intro_opening_b.py [--preview DIR]

Writes graphics/intro/opening_b/* (the pieces each cut uses: BG tiles, maps and
palettes re-packed per cut, sprite strips; every pixel copied from an official file,
the only change a palette recolour of HO-OH) and src/data/intro_opening_b.h. With
--preview, DIR/cN/tNNN.png: every frame drawn the way the GBA draws it (tiles, maps,
palettes in 5-bit colour, the palette blends of the events, sprite order, the
letterbox), which tools/qa/opening_check.py compares with the emulator.

Sprites are "sheets" (a strip of frames from one official file, one palette) played by
"tracks". A sheet can later be swapped for another source (e.g. a 2-frame front
sprite) by changing its SHEETS entry; the tracks and the player stay the same.
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from official_gfx import ROOT, path, tiles as load_tiles  # noqa: E402

OUT = 'graphics/intro/opening_b'
HEADER = 'src/data/intro_opening_b.h'
W, H, VIEW_Y, VIEW_H = 240, 160, 32, 96          # FR/LG's letterbox: rows 32-127
BG_BANK0 = 1                                     # BG palettes from bank 1 (bank 0: backdrop)
MAP_W, MAP_H = 64, 32                            # every map 64x32 tiles (512x256)
MAX_BG_TILES = 512

HIDE, FRONT, HFLIP, VFLIP = 1, 2, 4, 8
EV_BLEND, EV_CRY, EV_OBJ_BLEND = 0, 1, 2
T_BG, T_OBJ, T_ALL = 0, 1, 2

# cut starts (code frames from F706) on the bars of MUS_INTRO_FIGHT; the title at 595
CUTS = [('c1', 0, 136), ('c2', 136, 76), ('c3', 212, 153), ('c4', 365, 154), ('c5', 519, 76)]
END = 595


# ---------------------------------------------------------------- colours
def c5(rgb8):
    return tuple(v >> 3 for v in rgb8[:3])


def pal_file(p):
    """An official palette in 5-bit colours: JASC .pal, or the palette of the .png the
    build turns into the .gbapal (gbagfx divides by 8 as well)."""
    full = path(p)
    if full.endswith('.pal'):
        words = open(full).read().split()
        n = int(words[2])
        return [c5([int(v) for v in words[3 + 3 * i:6 + 3 * i]]) for i in range(n)]
    flat = Image.open(full).getpalette()
    return [c5(flat[i:i + 3]) for i in range(0, len(flat), 3)]


def pal16(colours):
    out = list(colours[:16]) + [(0, 0, 0)] * (16 - len(colours[:16]))
    out[0] = (0, 0, 0)
    return tuple(out)


def blend5(c, coeff, col):
    """BlendPalette (src/blend_palette.c) on one 5-bit colour."""
    return tuple(a + (((b - a) * coeff) >> 4) for a, b in zip(c, col))


def rgb5(r, g, b):
    return (r >> 3, g >> 3, b >> 3)


WHITE, BLACK = (31, 31, 31), (0, 0, 0)


# ---------------------------------------------------------------- BG cells
def flip_tile(t, h, v):
    return tuple(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))


class Layer:
    """A 64x32 grid of cells; a cell is (64 pixel indices, 16-colour palette) or None."""

    def __init__(self):
        self.cells = {}

    def put(self, tx, ty, tile, pal):
        if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
            self.cells[(tx, ty)] = (tuple(tile), pal)


def map_cells(tile_png, map_bin, pals, width, base_bank):
    """The cells of an official tilemap: pals is the palette file's list of colours as
    the game loads it at base_bank (16-colour banks); tiles keep their flips."""
    ts = load_tiles(tile_png)
    ents = [v for (v,) in struct.iter_unpack('<H', open(path(map_bin), 'rb').read())]
    out = {}
    for i, e in enumerate(ents):
        if width == 64:
            scr, k = divmod(i, 1024)
            ty, tx = divmod(k, 32)
            tx += 32 * scr
        else:
            ty, tx = divmod(i, width)
        t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        if t >= len(ts):
            continue
        b = bank - base_bank
        if len(pals) <= 16 or not 0 <= b < len(pals) // 16:
            b = 0
        tile = [px for row in ts[t] for px in row]
        out[(tx, ty)] = (flip_tile(tile, hf, vf), pal16(pals[b * 16:b * 16 + 16]))
    return out


def layout_cells(layout_dir, primary, secondary, width):
    """A field map drawn the way field_camera.c does: per metatile, by its layer type,
    the bottom and top tiles go to BG3/BG2/BG1 (FR/LG: primary tiles and metatiles
    below 640, palettes 0-6 primary, 7-12 secondary). Returns three dicts of cells
    keyed by (x, y) in 8-px tiles of the whole map."""
    def tileset(d):
        ts = load_tiles(d + '/tiles.png')
        mt = [v for (v,) in struct.iter_unpack('<H', open(path(d + '/metatiles.bin'), 'rb').read())]
        at = [v for (v,) in struct.iter_unpack('<I', open(path(d + '/metatile_attributes.bin'), 'rb').read())]
        return ts, [mt[i:i + 8] for i in range(0, len(mt), 8)], at
    pt, pm, pa = tileset(primary)
    st, sm, sa = tileset(secondary)
    pals = []
    for i in range(16):
        d = primary if i < 7 else secondary
        f = '%s/palettes/%02d.pal' % (d, i)
        pals.append(pal16(pal_file(f)) if os.path.exists(path(f)) else pal16([]))
    blocks = [v & 0x3FF for (v,) in struct.iter_unpack('<H', open(path(layout_dir + '/map.bin'), 'rb').read())]
    layers = ({}, {}, {})                        # BG3 bottom, BG2 middle, BG1 top

    def cell(e):
        t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        tile = pt[t] if t < 640 else st[t - 640] if t - 640 < len(st) else None
        if tile is None:
            return None
        return flip_tile([px for row in tile for px in row], hf, vf), pals[bank]
    for bi, m in enumerate(blocks):
        meta, attr = (pm[m], pa[m]) if m < 640 else (sm[m - 640], sa[m - 640])
        kind = (attr & 0x60000000) >> 29
        by, bx = divmod(bi, width)
        for q in range(4):
            x, y = bx * 2 + (q & 1), by * 2 + (q >> 1)
            bottom, top = cell(meta[q]), cell(meta[4 + q])
            if kind == 0:                        # NORMAL: garbage tile 0x3014 on BG3
                layers[0][(x, y)] = cell(0x3014)
                layers[1][(x, y)] = bottom
                layers[2][(x, y)] = top
            elif kind == 1:                      # COVERED
                layers[0][(x, y)] = bottom
                layers[1][(x, y)] = top
            else:                                # SPLIT
                layers[0][(x, y)] = bottom
                layers[2][(x, y)] = top
    return layers


def pack_bg(layers):
    """Tiles (deduplicated with flips), palettes (deduplicated, from BG_BANK0) and the
    three 64x32 maps of a cut."""
    tiles = [tuple([0] * 64)]
    index = {tiles[0]: 0}
    pals = []
    maps = []
    for layer in layers:
        entries = [0] * (MAP_W * MAP_H)
        for (tx, ty), c in (layer.cells.items() if layer else []):
            if c is None:
                continue
            tile, pal = c
            if not any(tile):
                continue
            if pal not in pals:
                pals.append(pal)
            bank = BG_BANK0 + pals.index(pal)
            entry = None
            for h, v, bits in ((0, 0, 0), (1, 0, 0x400), (0, 1, 0x800), (1, 1, 0xC00)):
                f = flip_tile(tile, h, v)
                if f in index:
                    entry = index[f] | bits
                    break
            if entry is None:
                index[tile] = len(tiles)
                tiles.append(tile)
                entry = index[tile]
            scr, lx = divmod(tx, 32)
            entries[scr * 1024 + ty * 32 + lx] = entry | (bank << 12)
        maps.append(entries if layer else None)
    assert len(tiles) <= MAX_BG_TILES, len(tiles)
    assert BG_BANK0 + len(pals) <= 16, len(pals)
    return tiles, pals, maps


# ---------------------------------------------------------------- sprites
class Sheet:
    """Frames of one official sprite file, one palette. frames: list of (x, y) corners
    of w x h frames in the file."""

    def __init__(self, name, src, w, h, pal, frames=None, recolour=None):
        self.name, self.src, self.w, self.h = name, src, w, h
        im = Image.open(path(src))
        iw, ih = im.size
        if frames is None:
            frames = [(0, y) for y in range(0, ih, h)] if iw == w else [(x, 0) for x in range(0, iw, w)]
        px = im.load()
        self.frames = [[[px[fx + x, fy + y] & 15 for x in range(w)] for y in range(h)] for fx, fy in frames]
        self.pal = pal16(pal_file(pal))
        if recolour:
            self.pal = recolour(self.pal)
        stem = os.path.splitext(pal)[0].split('/')[-2:]
        self.tag = 'PALTAG_B_' + ('_'.join(stem) + ('_' + recolour.__name__ if recolour else '')).upper()


def gold(pal):
    """HO-OH's field palette recoloured to a gold ramp, in the original order (each
    colour takes the gold of its brightness)."""
    ramp = [(15, 9, 2), (24, 16, 5), (30, 24, 9), (31, 29, 19), (31, 31, 27)]
    out = [pal[0]]
    for r, g, b in pal[1:]:
        lum = (r * 3 + g * 6 + b) / 310.0
        out.append(ramp[min(4, int(lum * 5))])
    return tuple(out)


SPR = 'graphics/battle_anims/sprites/'
SHEETS = {s.name: s for s in [
    Sheet('red_field', 'graphics/object_events/pics/people/red_normal.png', 16, 32,
          'graphics/object_events/palettes/player.pal'),
    Sheet('pika_field', 'graphics/object_events/pics/pokemon/pikachu.png', 16, 16,
          'graphics/object_events/palettes/npc_blue.pal'),
    Sheet('red_back', 'graphics/trainers/back_pics/red_back_pic.png', 64, 64,
          'graphics/trainers/palettes/red_back_pic.pal'),
    Sheet('pika_front', 'graphics/pokemon/pikachu/front.png', 64, 64, 'graphics/pokemon/pikachu/normal.pal'),
    Sheet('pika_back', 'graphics/pokemon/pikachu/back.png', 64, 64, 'graphics/pokemon/pikachu/normal.pal'),
    Sheet('ball', 'graphics/interface/ball/poke.png', 16, 16, 'graphics/interface/ball/poke.png'),
    Sheet('electricity', SPR + 'electricity.png', 32, 32, SPR + 'electric_orbs.png'),
    Sheet('lightning', SPR + 'lightning.png', 32, 32, SPR + 'lightning_2.png'),
    Sheet('run', 'graphics/credits/player_male.png', 64, 64, 'graphics/credits/player_male.png'),
    Sheet('spearow_field', 'graphics/object_events/pics/pokemon/spearow.png', 16, 16,
          'graphics/object_events/palettes/npc_white.pal'),
    Sheet('spearow_front', 'graphics/pokemon/spearow/front.png', 64, 64, 'graphics/pokemon/spearow/normal.pal'),
    Sheet('rain', 'graphics/weather/rain.png', 16, 32, 'graphics/weather/default.pal'),
    Sheet('cloud', 'graphics/weather/cloud.png', 64, 64, 'graphics/weather/cloud.png'),
    Sheet('hooh_field', 'graphics/object_events/pics/pokemon/ho_oh.png', 32, 32,
          'graphics/object_events/palettes/npc_blue.pal', recolour=gold),
    # the small and the tiny star of the battle's gold stars (8x8 each)
    Sheet('star', SPR + 'gold_stars.png', 8, 8, SPR + 'gold_stars.png', frames=[(0, 16), (8, 16)]),
]}
OAM = {(64, 64): 'sOam_64x64', (32, 32): 'sOam_32x32', (16, 32): 'sOam_16x32',
       (16, 16): 'sOam_16x16', (8, 8): 'sOam_8x8'}


class Cut:
    def __init__(self, name, start, frames):
        self.name, self.start, self.frames = name, start, frames
        self.tracks = []                           # (track name, sheet name)
        self.keys = [dict() for _ in range(frames)]
        self.scroll = [(0, 0, 0, 0, 0, 0)] * frames
        self.events = []
        self.layers = [None, None, None]           # BG3, BG2, BG1

    def track(self, name, sheet):
        self.tracks.append((name, sheet))

    def key(self, t, name, x, y, frame=0, flags=0):
        """Sprite corner (x, y) on the screen (the view starts at row 32)."""
        s = SHEETS[dict(self.tracks)[name]]
        x, y = int(math.floor(x)), int(math.floor(y))
        # fully outside the letterbox: hide (no wrap-round at the screen's edges)
        if y >= VIEW_Y + VIEW_H or y + s.h <= VIEW_Y or x >= W or x + s.w <= 0:
            return
        self.keys[t][name] = (x, y, frame, flags)

    def ev(self, t, typ, target=0, coeff=0, color=BLACK):
        self.events.append((t, typ, target, coeff, color))


# ---------------------------------------------------------------- the cuts
def s_ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


ROUTE_H = 40 * 16
C1_PATH = [(96, ROUTE_H + 120), (96, ROUTE_H + 136), (200, ROUTE_H + 136), (200, ROUTE_H - 64)]


def c1_red(t):
    seg = [math.dist(C1_PATH[i], C1_PATH[i + 1]) for i in range(3)]
    d = max(0.0, t - 8) * 2.0
    for i in range(3):
        if d <= seg[i]:
            f = d / seg[i]
            return (C1_PATH[i][0] + (C1_PATH[i + 1][0] - C1_PATH[i][0]) * f,
                    C1_PATH[i][1] + (C1_PATH[i + 1][1] - C1_PATH[i][1]) * f, i)
        d -= seg[i]
    return C1_PATH[-1][0], C1_PATH[-1][1], 2


def c1_camera(t):
    fx, fy, _ = c1_red(min(t, 100))
    cx = max(0, min(24 * 16 - W, fx - W // 2 + 8))
    cy = fy - VIEW_H // 2 - 8
    if t < 24:
        cy -= round(72 * (1 - s_ease(t / 24.0)))
    return int(cx), int(round(cy))


def cut1(c):
    """Pallet Town at dawn: tilt down onto RED's door, follow him north; the camera
    stops at t100 and PIKACHU, trailing, sits down and looks back at t110."""
    ts = ('data/tilesets/primary/general', 'data/tilesets/secondary/pallet_town')
    route = layout_cells('data/layouts/Route1', *ts, 24)
    town = layout_cells('data/layouts/PalletTown', *ts, 24)
    cams = [c1_camera(t) for t in range(c.frames)]
    top = min(cy for _, cy in cams)
    y0 = (top // 8) * 8                          # map row 0 = world row y0
    assert max(cy for _, cy in cams) + VIEW_H <= y0 + 256
    for li in range(3):
        L = Layer()
        for part, oy in ((route, 0), (town, ROUTE_H // 8)):
            for (x, y), cell in part[li].items():
                if cell is not None:
                    L.put(x, y + oy - y0 // 8, *cell)
        c.layers[li] = L
    c.track('red', 'red_field')
    c.track('pika', 'pika_field')
    for t in range(c.frames):
        cx, cy = cams[t]
        vofs = cy - y0 - VIEW_Y
        c.scroll[t] = (cx, vofs, cx, vofs, cx, vofs)
        rx, ry, leg = c1_red(t)
        step = (t // 8) % 2
        walking = t >= 8
        frame = {0: 3 + step, 1: 7 + step, 2: 5 + step}[leg] if walking else 0
        c.key(t, 'red', rx - cx, ry - cy - 16 + VIEW_Y, frame, HFLIP if (leg == 1 and walking) else 0)
        if t >= 11:
            pt = min(t, 110) - 11
            px_, py_, pleg = c1_red(pt)
            if t >= 110:
                pf, fl = 0, 0
            else:
                pf = {0: 3 + step, 1: 7 + step, 2: 5 + step}[pleg] if pt >= 8 else 0
                fl = HFLIP if (pleg == 1 and pt >= 8) else 0
            c.key(t, 'pika', px_ - cx, py_ - cy + VIEW_Y, pf, fl)
    # out of the GAME FREAK scene's white into a dawn tint, then day
    dawn = rgb5(255, 156, 82)
    for t in range(0, 17):
        f = t / 16.0
        col = tuple(round(WHITE[i] + (dawn[i] - WHITE[i]) * f) for i in range(3))
        c.ev(t, EV_BLEND, T_ALL, 16 - round(12 * f), col)
    for t in range(17, 41):
        c.ev(t, EV_BLEND, T_ALL, max(0, 4 - (t - 16) // 6), dawn)


RED_THROW = [(4, 0), (24, 1), (30, 2), (36, 3), (60, 4), (999, 0)]   # sAnimCmd_Red_1
BALL_OUT, BALL_HIT = 32, 48


def cut2(c):
    """The ball it hates: RED (back) throws, the ball arcs over, PIKACHU hops and zaps
    it back over RED."""
    L = Layer()
    for k, cell in map_cells('graphics/battle_terrain/grass/terrain.png', 'graphics/battle_terrain/grass/terrain.bin',
                             pal_file('graphics/battle_terrain/grass/terrain.pal'), 64, 2).items():
        L.put(k[0], k[1], *cell)
    c.layers[0] = L
    for name, sheet in (('ball', 'ball'), ('e0', 'electricity'), ('e1', 'electricity'), ('e2', 'electricity'),
                        ('e3', 'electricity'), ('pika', 'pika_front'), ('red', 'red_back')):
        c.track(name, sheet)
    for t in range(c.frames):
        c.scroll[t] = (0, 16 - VIEW_Y, 0, 0, 0, 0)
        hop = -round(8 * math.sin(math.pi * (t - 44) / 14.0)) if 44 <= t < 58 else 0
        c.key(t, 'pika', 144, -6 + hop + VIEW_Y)
        f = next(fr for until, fr in RED_THROW if t < until)
        c.key(t, 'red', 24, 32 + VIEW_Y, f)
        if BALL_OUT <= t < BALL_HIT:
            p = (t - BALL_OUT) / float(BALL_HIT - BALL_OUT)
            c.key(t, 'ball', 72 + 96 * p, 40 - 24 * math.sin(math.pi * p) - 16 * p + VIEW_Y, (t // 2) % 2)
        elif BALL_HIT <= t < 70:
            p = (t - BALL_HIT) / 22.0
            c.key(t, 'ball', 168 - 190 * p, 20 - 40 * math.sin(math.pi * p * 0.8) + 40 * p * p + VIEW_Y, (t // 2) % 2)
        if BALL_HIT <= t < 56:
            for k in range(4):
                a = t / 3.0 + k * math.pi / 2
                c.key(t, 'e%d' % k, 160 + 26 * math.cos(a), 20 + 20 * math.sin(a) + VIEW_Y, (t + k) % 4)
    c.ev(BALL_HIT, EV_BLEND, T_ALL, 10, WHITE)
    c.ev(BALL_HIT, EV_CRY)
    c.ev(BALL_HIT + 2, EV_BLEND, T_ALL, 0, WHITE)


def swoop(f, left_to_right):
    x0, x1 = (-70, 250) if left_to_right else (250, -70)
    return x0 + (x1 - x0) * f, 60 * (f - 0.5) ** 2 * 4 - 46


STORM = rgb5(16, 24, 56)


def cut3(c):
    """Rain and SPEAROW: the opening's forest darkened and scrolling fast, RED running
    (the credits' run cycle), the far flock, three SPEAROW swooping over his head."""
    L = Layer()
    for k, cell in map_cells('graphics/intro/scene_3/bg.png', 'graphics/intro/scene_3/bg.bin',
                             pal_file('graphics/intro/scene_3/bg.pal'), 32, 1).items():
        for dx in (0, 32):
            L.put(k[0] + dx, k[1], *cell)
    c.layers[0] = L
    c.track('bolt', 'lightning')
    for k in range(14):
        c.track('rain%d' % k, 'rain')
    c.track('swoop', 'spearow_front')
    c.track('run', 'run')
    for k in range(9):
        c.track('flock%d' % k, 'spearow_field')
    for t in range(c.frames):
        c.scroll[t] = ((t * 4) % 512, 40 - VIEW_Y, 0, 0, 0, 0)
        for k in range(9):
            fx = (300 - t * 3 + k * 23) % 320 - 40
            c.key(t, 'flock%d' % k, fx, 4 + (k * 7) % 20 + VIEW_Y, (t // 4 + k) % 3)
        c.key(t, 'run', 88, 30 + VIEW_Y, (t // 5) % 6)
        for t0, ltr in ((20, False), (60, True), (110, False)):
            if t0 <= t < t0 + 26:
                x, y = swoop((t - t0) / 26.0, ltr)
                c.key(t, 'swoop', x, y + 40 + VIEW_Y, 0, HFLIP if ltr else 0)
        for k in range(14):
            c.key(t, 'rain%d' % k, (k * 37 + t * 5) % 256 - 16, (k * 29 + t * 9) % 128 - 32 + VIEW_Y, (t // 2 + k) % 4)
        if t % 60 in (40, 41):
            c.key(t, 'bolt', 180, VIEW_Y, 2)
    c.ev(0, EV_BLEND, T_BG, 9, STORM)
    for t in range(c.frames):
        if t % 60 == 40:                            # lightning: a grey wash of 2 frames
            c.ev(t, EV_BLEND, T_ALL, 8, WHITE)
            c.ev(t + 2, EV_BLEND, T_ALL, 0, WHITE)
            c.ev(t + 2, EV_BLEND, T_BG, 9, STORM)


def thunder_layer():
    """The Thunder background's cloud rows only: rows 0-6 and their mirror (13-19, as
    the original map mirrors them), repeated down the map, so there is no flat band and
    the joins are mirror lines through cloud."""
    cells = map_cells('graphics/battle_anims/backgrounds/thunder.png', 'graphics/battle_anims/backgrounds/thunder.bin',
                      pal_file('graphics/battle_anims/backgrounds/thunder.png'), 32, 0)
    rows = list(range(0, 7)) + list(range(13, 20))
    L = Layer()
    for ty in range(MAP_H):
        src = rows[ty % len(rows)]
        for tx in range(MAP_W):
            cell = cells.get((tx % 32, src))
            if cell:
                L.put(tx, ty, *cell)
    return L


def cut4(c):
    """THUNDERBOLT: the Thunder clouds flow down, darkened as in battle; PIKACHU (1x)
    comes up into the middle; bolts hit the two SPEAROW, which blink white three times
    and drop straight down; into white."""
    c.layers[0] = thunder_layer()
    for k in range(2):
        c.track('bolt%d' % k, 'lightning')
    for k in range(4):
        c.track('e%d' % k, 'electricity')
    c.track('pika', 'pika_front')
    c.track('sp0', 'spearow_front')
    c.track('sp1', 'spearow_front')
    for t in range(c.frames):
        c.scroll[t] = (0, (c.frames - 1 - t) - VIEW_Y, 0, 0, 0, 0)
        shake = (1 if t % 2 else -1) if 50 <= t < 62 else 0
        rise = round(24 * (1 - s_ease(t / 30.0)))
        c.key(t, 'pika', W // 2 - 32 + shake, 16 + rise + VIEW_Y)
        for k in range(4):
            a = t / 4.0 + k * math.pi / 2
            c.key(t, 'e%d' % k, 104 + 50 * math.cos(a), 30 + 30 * math.sin(a) + VIEW_Y, (t + k) % 4)
        for k, x in enumerate((8, 168)):
            y = 4 + round(3 * math.sin(t / 5.0 + k))
            if t >= 62:
                y += (t - 62) * (t - 62) // 4
            c.key(t, 'sp%d' % k, x, y + VIEW_Y, 0, HFLIP if k == 0 else 0)
            if 48 <= t < 56:
                c.key(t, 'bolt%d' % k, x + 16, VIEW_Y - 8, 0 if (t // 2) % 2 else 2)
    c.ev(0, EV_BLEND, T_BG, 9, BLACK)
    c.ev(50, EV_BLEND, T_ALL, 10, WHITE)
    for t in (50, 54, 58):
        c.ev(t, EV_OBJ_BLEND, 'spearow_front', 16, WHITE)
    c.ev(52, EV_BLEND, T_ALL, 0, WHITE)
    c.ev(52, EV_BLEND, T_BG, 9, BLACK)
    for t in (56, 60):
        c.ev(t, EV_OBJ_BLEND, 'spearow_front', 0, WHITE)
    for t in range(c.frames - 16, c.frames):
        c.ev(t, EV_BLEND, T_ALL, t - (c.frames - 17), WHITE)


SKY_TOP, SKY_BOTTOM = rgb5(99, 156, 222), rgb5(206, 234, 255)


def sky_layer():
    """12 flat bands of sky colour, 8 lines each, over the letterbox (the backdrop
    stepped per band); colours 1-12 of one palette, one solid tile per colour."""
    cols = [(0, 0, 0)] + [tuple(round(SKY_TOP[i] + (SKY_BOTTOM[i] - SKY_TOP[i]) * k / 11.0) for i in range(3))
                          for k in range(12)]
    pal = pal16(cols)
    L = Layer()
    for ty in range(MAP_H):
        k = min(11, max(0, ty - VIEW_Y // 8))
        for tx in range(MAP_W):
            L.put(tx, ty, [k + 1] * 64, pal)
    return L


def cut5(c):
    """After the storm: the sky in 12 steps, two layers of the weather's clouds, HO-OH
    (gold field sprite) beating its wings in the upper third, then rising out of the
    picture; gold sparkles falling below it; RED and PIKACHU from behind, low."""
    c.layers[0] = sky_layer()
    for k in range(3):
        c.track('star%d' % k, 'star')
    c.track('hooh', 'hooh_field')
    c.track('red', 'red_back')
    c.track('pika', 'pika_back')
    for k in range(3):
        c.track('cloud%d' % k, 'cloud')
    HX = 140
    for t in range(c.frames):
        c.scroll[t] = (0, 0, 0, 0, 0, 0)
        # far layer: 1 cloud, slow; near layer: 2, faster, one half off the left edge
        for k, (x0, y, speed, fl) in enumerate(((150, 18, 0.25, 0), (-32, 44, 0.75, HFLIP), (176, 50, 0.75, 0))):
            c.key(t, 'cloud%d' % k, x0 - t * speed, y + VIEW_Y, 0, fl)
        hy = 6 if t < 36 else 6 - (t - 36) * (t - 36) / 32.0
        c.key(t, 'hooh', HX, hy + VIEW_Y, (t // 9) % 2)
        for k, born in enumerate((8, 26, 44)):
            age = t - born
            if 0 <= age < 36:
                bx, by = HX + 8 + (k - 1) * 10, (6 if born < 36 else 6 - (born - 36) ** 2 / 32.0) + 24
                c.key(t, 'star%d' % k, bx, by + age * 0.5 + VIEW_Y, (age // 6) % 2)
        c.key(t, 'red', 40, 48 + VIEW_Y)
        c.key(t, 'pika', 120, 50 + VIEW_Y)
    for t in range(0, 16):
        c.ev(t, EV_BLEND, T_ALL, 16 - t, WHITE)
    for t in range(c.frames - 16, c.frames):
        c.ev(t, EV_BLEND, T_ALL, t - (c.frames - 17), BLACK)


BUILD = {'c1': cut1, 'c2': cut2, 'c3': cut3, 'c4': cut4, 'c5': cut5}


# ---------------------------------------------------------------- the GBA, drawn
class Gba:
    """Draws a cut's frames as the hardware shows them: BG3, BG2, sprites (priority 1,
    by subpriority), BG1, inside the letterbox; palettes in 5-bit with the events'
    BlendPalette applied the way Table_Update applies them."""

    def __init__(self, cut, packed):
        self.c = cut
        self.tiles, self.bgpals, self.maps = packed
        self.sheets = sorted({s for _, s in cut.tracks})
        self.unfaded = {('bg', i): list(p) for i, p in enumerate(self.bgpals)}
        for s in self.sheets:
            self.unfaded[('obj', SHEETS[s].tag)] = list(SHEETS[s].pal)
        self.faded = {k: list(v) for k, v in self.unfaded.items()}

    def blend(self, keys, coeff, col):
        for k in keys:
            self.faded[k] = [blend5(c, coeff, col) for c in self.unfaded[k]]

    def apply(self, t):
        for (et, typ, target, coeff, col) in self.c.events:
            if et != t:
                continue
            if typ == EV_BLEND:
                keys = [k for k in self.unfaded if target == T_ALL or (k[0] == 'bg') == (target == T_BG)]
                self.blend(keys, coeff, col)
            elif typ == EV_OBJ_BLEND:
                self.blend([('obj', SHEETS[target].tag)], coeff, col)

    def frame(self, t):
        self.apply(t)
        img = Image.new('RGB', (W, H))
        px = img.load()
        buf = [[None] * W for _ in range(VIEW_H)]
        sc = self.c.scroll[t]

        def bg(li, hofs, vofs):
            m = self.maps[li]
            if m is None:
                return
            for y in range(VIEW_H):
                my = (y + VIEW_Y + vofs) % 256
                ty, py = divmod(my, 8)
                for x in range(W):
                    mx = (x + hofs) % 512
                    tx, pxx = divmod(mx, 8)
                    e = m[(tx // 32) * 1024 + ty * 32 + tx % 32]
                    t_, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
                    v = self.tiles[t_][(7 - py if vf else py) * 8 + (7 - pxx if hf else pxx)]
                    if v:
                        buf[y][x] = self.faded[('bg', bank - BG_BANK0)][v]
        bg(0, sc[0], sc[1])
        bg(1, sc[2], sc[3])
        keys = self.c.keys[t]
        # draw order: tracks later in the list are behind (higher subpriority)
        for i in range(len(self.c.tracks) - 1, -1, -1):
            name, sheet = self.c.tracks[i]
            if name not in keys:
                continue
            x, y, f, fl = keys[name]
            s = SHEETS[sheet]
            pal = self.faded[('obj', s.tag)]
            fr = s.frames[f]
            for yy in range(s.h):
                Y = y + yy - VIEW_Y
                if not 0 <= Y < VIEW_H:
                    continue
                row = fr[s.h - 1 - yy if fl & VFLIP else yy]
                for xx in range(s.w):
                    X = x + xx
                    if not 0 <= X < W:
                        continue
                    v = row[s.w - 1 - xx if fl & HFLIP else xx]
                    if v:
                        buf[Y][X] = pal[v]
        bg(2, sc[4], sc[5])
        for y in range(VIEW_H):
            for x in range(W):
                c = buf[y][x] or (0, 0, 0)
                px[x, y + VIEW_Y] = (c[0] << 3, c[1] << 3, c[2] << 3)
        return img


# ---------------------------------------------------------------- output
def write_png_indexed(fn, rows, pal):
    h, w = len(rows), len(rows[0])
    im = Image.new('P', (w, h))
    flat = []
    for c in list(pal)[:16] + [(0, 0, 0)] * (16 - len(pal[:16])):
        flat += [c[0] << 3, c[1] << 3, c[2] << 3]
    im.putpalette(flat)
    im.putdata([v for r in rows for v in r])
    im.save(path(fn))


def write_pal(fn, pals):
    cols = [c for p in pals for c in p]
    with open(path(fn), 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n%d\n' % len(cols))
        for c in cols:
            f.write('%d %d %d\n' % (c[0] << 3, c[1] << 3, c[2] << 3))


def scene_tags(c):
    return sorted({SHEETS[s].tag for _, s in c.tracks})


def ident(s):
    return ''.join(w.capitalize() for w in s.split('_'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None)
    a = ap.parse_args()
    os.makedirs(path(OUT), exist_ok=True)
    cuts = []
    for name, start, frames in CUTS:
        c = Cut(name, start, frames)
        BUILD[name](c)
        packed = pack_bg(c.layers)
        cuts.append((c, packed))
        tiles, pals, maps = packed
        print('%s: %d BG tiles, %d BG palettes, %d tracks' % (name, len(tiles), len(pals), len(c.tracks)))
        sheet_rows = []
        for i in range(0, len(tiles), 16):
            row_tiles = list(tiles[i:i + 16]) + [tuple([0] * 64)] * (16 - len(tiles[i:i + 16]))
            for y in range(8):
                sheet_rows.append([row_tiles[k][y * 8 + x] for k in range(16) for x in range(8)])
        write_png_indexed('%s/%s_bg.png' % (OUT, name), sheet_rows, pals[0])
        write_pal('%s/%s_bg.pal' % (OUT, name), pals)
        for li, m in enumerate(maps):
            if m is not None:
                with open(path('%s/%s_map%d.bin' % (OUT, name, li)), 'wb') as f:
                    f.write(struct.pack('<%dH' % len(m), *m))
    used = sorted({s for c, _ in cuts for _, s in c.tracks})
    for s in used:
        sh = SHEETS[s]
        write_png_indexed('%s/%s.png' % (OUT, s), [r for fr in sh.frames for r in fr], sh.pal)
        write_pal('%s/%s.pal' % (OUT, s), [sh.pal])
    write_header(cuts, used)
    if a.preview:
        for c, packed in cuts:
            d = os.path.join(a.preview, c.name)
            os.makedirs(d, exist_ok=True)
            g = Gba(c, packed)
            for t in range(c.frames):
                g.frame(t).save('%s/t%03d.png' % (d, t))
        print('mock-ups in', a.preview)


def write_header(cuts, used):
    L = ['// Generated by tools/make_intro_opening_b.py. Do not edit: change the direction',
         '// there and run it again. Plan B of the opening: official graphics only.', '']
    tags = []
    for s in used:
        if SHEETS[s].tag not in tags:
            tags.append(SHEETS[s].tag)
    L.append('enum {')
    L.append('    %s = 0x1400,' % tags[0])
    L += ['    %s,' % t for t in tags[1:]]
    L += ['};', '']
    for s in used:
        sh = SHEETS[s]
        L.append('static const u32 sB_%s_Gfx[] = INCBIN_U32("%s/%s.4bpp");' % (ident(s), OUT, s))
        L.append('static const u16 sB_%s_Pal[] = INCBIN_U16("%s/%s.gbapal");' % (ident(s), OUT, s))
    L.append('')
    for c, (tiles, pals, maps) in cuts:
        n, N = c.name, c.name.upper()
        L.append('// ---- %s: code frames %d-%d' % (n, c.start, c.start + c.frames - 1))
        L.append('static const u32 sB_%s_BgGfx[] = INCBIN_U32("%s/%s_bg.4bpp");' % (N, OUT, n))
        L.append('static const u16 sB_%s_BgPal[] = INCBIN_U16("%s/%s_bg.gbapal");' % (N, OUT, n))
        for li, m in enumerate(maps):
            if m is not None:
                L.append('static const u16 sB_%s_Map%d[] = INCBIN_U16("%s/%s_map%d.bin");' % (N, li, OUT, n, li))
        L.append('#define %s_FRAMES %d' % (N, c.frames))
        L.append('#define %s_TRACKS %d' % (N, len(c.tracks)))
        L.append('static const struct OpeningTrack sB_%s_Tracks[] = {' % N)
        for i, (name, s) in enumerate(c.tracks):
            sh = SHEETS[s]
            L.append('    {sB_%s_Gfx, &%s, %s, %d, %d, %d, %d}, // %s' % (
                ident(s), OAM[(sh.w, sh.h)], sh.tag, sh.w, sh.h, 20 + i, 20 + i, name))
        L.append('};')
        L.append('static const struct OpeningKey sB_%s_Keys[%s_FRAMES][%s_TRACKS] = {' % (N, N, N))
        for t in range(c.frames):
            ks = []
            for name, _ in c.tracks:
                k = c.keys[t].get(name)
                ks.append('{%d, %d, %d, %d}' % k if k else '{0, 0, 0, KEY_HIDE}')
            L.append('    {%s},' % ', '.join(ks))
        L.append('};')
        L.append('static const struct OpeningScroll sB_%s_Scroll[%s_FRAMES] = {' % (N, N))
        for s in c.scroll:
            L.append('    {%d, %d, %d, %d, %d, %d},' % tuple(s))
        L.append('};')
        L.append('static const struct OpeningEvent sB_%s_Events[] = {' % N)
        for (t, typ, target, coeff, col) in sorted(c.events, key=lambda e: e[0]):
            if typ == EV_OBJ_BLEND:
                target = scene_tags(c).index(SHEETS[target].tag)
            L.append('    {%d, %d, %d, %d, RGB(%d, %d, %d)},' % ((t, typ, target, coeff) + tuple(col)))
        L.append('    {0xFFFF},')
        L.append('};')
        tg = scene_tags(c)
        first = {}
        for s in sorted({s for _, s in c.tracks}):
            first.setdefault(SHEETS[s].tag, s)
        L.append('static const u16 *const sB_%s_ObjPals[] = {%s};' % (N, ', '.join('sB_%s_Pal' % ident(first[t]) for t in tg)))
        L.append('static const u16 sB_%s_ObjPalTags[] = {%s};' % (N, ', '.join(tg)))
        L.append('')
    L.append('static const struct OpeningTableScene sTableScenes[NUM_SCENES] = {')
    for c, (tiles, pals, maps) in cuts:
        N = c.name.upper()
        mp = ', '.join('sB_%s_Map%d' % (N, li) if m is not None else 'NULL' for li, m in enumerate(maps))
        L.append('    {')
        L.append('        sB_%s_Tracks, %s_TRACKS, %s_FRAMES, sB_%s_Keys[0], sB_%s_Scroll, sB_%s_Events,' % (N, N, N, N, N, N))
        L.append('        sB_%s_BgGfx, sizeof(sB_%s_BgGfx), {%s}, sB_%s_BgPal, %d,' % (N, N, mp, N, len(pals)))
        L.append('        sB_%s_ObjPals, sB_%s_ObjPalTags, ARRAY_COUNT(sB_%s_ObjPalTags),' % (N, N, N))
        L.append('    },')
    L.append('};')
    L.append('')
    L.append('static const u16 sSceneStarts[NUM_SCENES] = {%s};' % ', '.join(str(c.start) for c, _ in cuts))
    L.append('#define OPENING_END %d' % END)
    L.append('')
    open(path(HEADER), 'w').write('\n'.join(L))


if __name__ == '__main__':
    main()
