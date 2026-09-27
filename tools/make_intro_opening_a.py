#!/usr/bin/env python3
"""The Thunder Yellow opening, direction (a): PIKACHU vs RAICHU in VERMILION GYM
(docs/anim/opening-storyboard-A.md, approved by the user 2026-09-27, with the art
director's revision-2 changes R2-1..R2-5). This tool does the direction only: it takes
official in-game graphics (FR/LG files of this repository; Emerald's RAICHU anim_front
and PIKACHU's anim_front frame 1 from /root/src/pokeemerald), places, scrolls, flips,
scales and times them, and writes the tables src/intro_opening.c plays.

    python3 tools/make_intro_opening_a.py [--preview DIR] [--only c9,c10]

Writes graphics/intro/opening_a/* (per cut: BG tiles, maps and palettes re-packed from
the official files; sprite strips, every pixel copied from an official file) and
src/data/intro_opening_a.h. With --preview, DIR/<cut>/tNNN.png: every frame drawn the
way the GBA draws it (tiles, maps, palettes in 5-bit colour with the events' blends,
sprites by subpriority, the OBJ affine unit, semi-transparent sprites through BLDALPHA,
window 0 over the letterbox), which tools/qa/opening_check.py compares with the ROM.

Nothing is read from reference/.
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_intro_opening_b as B  # noqa: E402  plan B's verified helpers (packing, sheets)
from official_gfx import path, tiles as load_tiles  # noqa: E402

OUT = 'graphics/intro/opening_a'
HEADER = 'src/data/intro_opening_a.h'
W, H, VIEW_Y, VIEW_H = B.W, B.H, B.VIEW_Y, B.VIEW_H
HIDE, FRONT, HFLIP, VFLIP, BLEND = 1, 2, 4, 8, 16
EV_BLEND, EV_CRY, EV_OBJ_BLEND = B.EV_BLEND, B.EV_CRY, B.EV_OBJ_BLEND
T_BG, T_OBJ, T_ALL = B.T_BG, B.T_OBJ, B.T_ALL
WHITE, BLACK, STORM = B.WHITE, B.BLACK, B.STORM
CRY_PIKACHU, CRY_RAICHU = 0, 1
EVA = EVB = 8                                   # afterimages: 8/16 sprite + 8/16 below
BLDALPHA = EVA | (EVB << 8)

# the bars of MUS_INTRO_FIGHT (song from frame 20), code frames from F706
BARS = [0, 59, 136, 212, 289, 365, 442, 519, 595, 672]
END = 751                                       # F1457: IntroCB_ExitToTitleScreen, as FR/LG

CUTS = [  # name, first frame, frames, shot
    ('c1', 0, 136, 'S1 VERMILION GYM'),
    ('c2', 136, 76, 'S2 the battle begins'),
    ('c3', 212, 38, 'S3a close-ups'),
    ('c4', 250, 39, 'S3b face-off'),
    ('c5', 289, 38, 'S4a clash'),
    ('c6', 327, 38, 'S4b race'),
    ('c7', 365, 39, 'S4c Quick Attack'),
    ('c8', 404, 38, 'S4d counter'),
    ('c9', 442, 77, 'S5 THUNDERBOLT'),
    ('c10', 519, 38, 'S6 AGILITY'),
    ('c11', 557, 9, 'S6 the last hit'),
    ('c12', 566, 29, 'S6 the faint'),
    ('c13', 595, 156, 'S7 the win'),
]


def s_ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


# ---------------------------------------------------------------- sprite sheets
SPR = 'graphics/battle_anims/sprites/'
EMP = 'EM:graphics/pokemon/'


def ghost(pal):
    return pal


def hit(pal):
    return pal


def sheet(name, src, w, h, pal, frames=None, recolour=None):
    s = B.Sheet(name, src, w, h, pal, frames, recolour)
    s.tag = s.tag.replace('PALTAG_B_', 'PALTAG_A_')
    return s


def emote_sheet():
    """trainer_see.c's emoticons: 2x2-tile frames packed 4 tiles each in tile order."""
    s = sheet('emote', 'graphics/misc/emoticons.png', 16, 16, 'graphics/misc/emoticons.png', frames=[(0, 0)])
    ts = load_tiles('graphics/misc/emoticons.png')
    s.frames = []
    for n in range(3):
        fr = [[0] * 16 for _ in range(16)]
        for q in range(4):
            tile = ts[n * 4 + q]
            for y in range(8):
                for x in range(8):
                    fr[(q >> 1) * 8 + y][(q & 1) * 8 + x] = tile[y][x]
        s.frames.append(fr)
    return s


PK = 'graphics/pokemon/pikachu/'
SHEETS = {s.name: s for s in [
    sheet('red_field', 'graphics/object_events/pics/people/red_normal.png', 16, 32, 'graphics/object_events/palettes/player.pal'),
    sheet('red_run', 'graphics/object_events/pics/people/red_surf_run.png', 16, 32, 'graphics/object_events/palettes/player.pal'),
    sheet('pika_field', 'graphics/object_events/pics/pokemon/pikachu.png', 16, 16, 'graphics/object_events/palettes/npc_blue.pal'),
    sheet('surge_field', 'graphics/object_events/pics/people/lt_surge.png', 16, 32, 'graphics/object_events/palettes/npc_green.pal'),
    sheet('sailor', 'graphics/object_events/pics/people/sailor.png', 16, 32, 'graphics/object_events/palettes/npc_pink.pal'),
    sheet('gentleman', 'graphics/object_events/pics/people/gentleman.png', 16, 32, 'graphics/object_events/palettes/npc_white.pal'),
    sheet('balding', 'graphics/object_events/pics/people/balding_man.png', 16, 32, 'graphics/object_events/palettes/npc_white.pal'),
    emote_sheet(),
    sheet('surge_pic', 'graphics/trainers/front_pics/leader_lt_surge_front_pic.png', 64, 64, 'graphics/trainers/palettes/leader_lt_surge.pal'),
    sheet('red_back', 'graphics/trainers/back_pics/red_back_pic.png', 64, 64, 'graphics/trainers/palettes/red_back_pic.pal'),
    sheet('ball', 'graphics/interface/ball/poke.png', 16, 16, 'graphics/interface/ball/poke.png'),
    sheet('raichu', EMP + 'raichu/anim_front.png', 64, 64, EMP + 'raichu/normal.pal'),
    sheet('pika_front', PK + 'front.png', 64, 64, PK + 'normal.pal'),
    sheet('pika_happy', EMP + 'pikachu/anim_front.png', 64, 64, PK + 'normal.pal', frames=[(0, 64)]),
    sheet('pika_back', PK + 'back.png', 64, 64, PK + 'normal.pal'),
    sheet('pika_ghost', PK + 'back.png', 64, 64, PK + 'normal.pal', recolour=ghost),
    sheet('pika_hit', PK + 'back.png', 64, 64, PK + 'normal.pal', recolour=hit),
    sheet('impact', SPR + 'impact.png', 32, 32, SPR + 'impact.png'),
    sheet('dust', SPR + 'speed_dust.png', 16, 16, SPR + 'speed_dust.png'),
    sheet('spark1', SPR + 'spark_1.png', 16, 16, SPR + 'spark.pal'),
    sheet('spark2', SPR + 'spark_2.png', 16, 16, SPR + 'spark_2.png'),
    sheet('spark2_eo', SPR + 'spark_2.png', 16, 16, SPR + 'electric_orbs.png'),
    sheet('shock', SPR + 'shock_3.png', 32, 32, SPR + 'shock_3.png', frames=[(0, 64)]),
    sheet('electricity', SPR + 'electricity.png', 32, 32, SPR + 'electric_orbs.png'),
    sheet('lightning', SPR + 'lightning.png', 32, 32, SPR + 'lightning_2.png', frames=[(0, 0), (0, 64)]),
]}
OAM = {(64, 64, False): 'sOam_64x64', (32, 32, False): 'sOam_32x32', (16, 32, False): 'sOam_16x32',
       (16, 16, False): 'sOam_16x16', (64, 64, True): 'sOam_64x64_Affine', (16, 16, True): 'sOam_16x16_Affine'}


def content_box(sh, frame=0, flip=False):
    """Opaque pixels' bounding box (x0, y0, x1, y1) of a sheet frame."""
    fr = sh.frames[frame]
    xs = [x for y in range(sh.h) for x in range(sh.w) if fr[y][x]]
    ys = [y for y in range(sh.h) for x in range(sh.w) if fr[y][x]]
    x0, x1 = min(xs), max(xs)
    if flip:
        x0, x1 = sh.w - 1 - x1, sh.w - 1 - x0
    return x0, min(ys), x1, max(ys)


def mask(sh, frame, x, y, flip=False):
    fr = sh.frames[frame]
    return {(x + (sh.w - 1 - xx if flip else xx), y + yy) for yy in range(sh.h) for xx in range(sh.w) if fr[yy][xx]}


# ---------------------------------------------------------------- cuts
class Cut:
    def __init__(self, name, start, frames, title):
        self.name, self.start, self.frames, self.title = name, start, frames, title
        self.tracks = []                    # (track, sheet, affine)
        self.keys = [dict() for _ in range(frames)]
        self.scroll = [(0, 0, 0, 0, 0, 0)] * frames
        self.events = []
        self.layers = [None, None, None]    # BG3, BG2, BG1
        self.variants = {}                  # map variants: key -> [3 layers]
        self.patch_seq = []                 # (t, variant key)
        self.bld_alpha = 0
        self.split_row = 0

    def track(self, name, sheet_name, affine=False):
        self.tracks.append((name, sheet_name, affine))

    def key(self, t, name, x, y, frame=0, flags=0, affine=0):
        """Sprite corner (x, y) in the view (0-239, 0-95), unscaled for affine tracks."""
        tr = {n: (s, a) for n, s, a in self.tracks}[name]
        s = SHEETS[tr[0]]
        x, y = int(math.floor(x)), int(math.floor(y + VIEW_Y))
        if tr[1]:
            if not affine:
                affine = 0x100
            half = s.w * 256 // abs(affine) // 2 + 1
            cx, cy = x + s.w // 2, y + s.h // 2
            if cy - half >= VIEW_Y + VIEW_H or cy + half <= VIEW_Y or cx - half >= W or cx + half <= 0:
                return
        else:
            affine = 0
            if y >= VIEW_Y + VIEW_H or y + s.h <= VIEW_Y or x >= W or x + s.w <= 0:
                return
        if frame >= len(s.frames):
            raise ValueError('%s frame %d' % (name, frame))
        self.keys[t][name] = (x, y, frame, flags, affine)

    def ev(self, t, typ, target=0, coeff=0, color=BLACK):
        self.events.append((t, typ, target, coeff, color))

    def set_scroll(self, t, bx, by, fx=0, fy=0, tx=0, ty=0):
        self.scroll[t] = tuple(int(v) for v in (bx, by, fx, fy, tx, ty))


def layer_from_cells(cells, dx=0, dy=0, repeat_x=None):
    L = B.Layer()
    for (x, y), c in cells.items():
        if c is None:
            continue
        L.put(x + dx, y + dy, *c)
        if repeat_x:
            L.put(x + dx + repeat_x, y + dy, *c)
    return L


def solid_layer(color):
    L = B.Layer()
    tile = tuple([1] * 64)
    pal = B.pal16([(0, 0, 0), color])
    for y in range(B.MAP_H):
        for x in range(B.MAP_W):
            L.put(x, y, tile, pal)
    return L


def official_cells(png, binf, pal, width=32, base=0, rows=None):
    cells = B.map_cells(png, binf, B.pal_file(pal), width, base)
    if rows is not None:
        cells = {k: v for k, v in cells.items() if k[1] < rows}
    return cells


def stage_layer():
    """BATTLE_TERRAIN_LEADER (src/battle_bg.c): building terrain, leader palette (bank 2
    as the battle loads it), 32 tiles wide, repeated to 64."""
    return layer_from_cells(official_cells('graphics/battle_terrain/building/terrain.png',
                                           'graphics/battle_terrain/building/terrain.bin',
                                           'graphics/battle_terrain/indoor/leader.pal', 32, 2, rows=32), repeat_x=32)


def highspeed_layer(side):
    return layer_from_cells(official_cells('graphics/battle_anims/backgrounds/highspeed.png',
                                           'graphics/battle_anims/backgrounds/highspeed_%s.bin' % side,
                                           'graphics/battle_anims/backgrounds/highspeed.png'), repeat_x=32)


def impact_layer():
    return layer_from_cells(official_cells('graphics/battle_anims/backgrounds/impact.png',
                                           'graphics/battle_anims/backgrounds/impact_opponent.bin',
                                           'graphics/battle_anims/backgrounds/impact.png', rows=20), repeat_x=32)


def thunder_layers():
    """R2-1 / must-fix 1: the Thunder background's cloud rows 0-7 upright (BG3) and the
    same rows with the tile V-flip bit, in reverse order (BG2), as thunder.bin itself
    repeats them in rows 12-19. They meet on screen row 80 (window 0 hides BG2 above),
    band line 58 against its mirror."""
    cells = official_cells('graphics/battle_anims/backgrounds/thunder.png', 'graphics/battle_anims/backgrounds/thunder.bin',
                           'graphics/battle_anims/backgrounds/thunder.png', rows=8)
    up, down = B.Layer(), B.Layer()
    for (x, y), (tile, pal) in cells.items():
        for dx in (0, 32):
            up.put(x + dx, y, tile, pal)
            down.put(x + dx, 7 - y, B.flip_tile(tile, 0, 1), pal)
    return up, down


SPLIT_ROW = 80
THUNDER_VOFS_UP = 11 - VIEW_Y       # screen row 32 shows band line 11
THUNDER_VOFS_DOWN = 5 - SPLIT_ROW   # screen row 80 shows flipped line 5 = band line 58


def thunder_phase(t):
    """R2-1: the lower layer starts half a period (128 px) off the upper one and drifts
    by less than 64 px over S5 and S6 (t442-594), so the two never line up."""
    if t < BARS[7]:
        xu = (t - BARS[6]) * 2
    else:
        xu = (BARS[7] - BARS[6]) * 2 + (t - BARS[7]) * 4
    drift = (t - BARS[6]) * 3 // 10
    return xu, xu + 128 + drift


# ---------------------------------------------------------------- VERMILION GYM (S1)
BEAM = {  # data/maps/VermilionCity_Gym/scripts.inc: On (the map) -> HalfOn -> Off
    'on': {},
    'half': {(3, 6): 0x2BB, (4, 6): 0x2BC, (5, 6): 0x2BD, (6, 6): 0x2BE, (7, 6): 0x2BF,
             (3, 7): 0x2C3, (4, 7): 0x2C4, (5, 7): 0x2C5, (6, 7): 0x2C6, (7, 7): 0x2C7},
    'off': {(3, 6): 0x293, (4, 6): 0x294, (5, 6): 0x281, (6, 6): 0x295, (7, 6): 0x296,
            (3, 7): 0x29B, (4, 7): 0x29C, (5, 7): 0x281, (6, 7): 0x29D, (7, 7): 0x29E},
}
GYM_W = 11
GYM_TX, GYM_TY = 4, 4               # the map's corner in 8-px tiles of the world (2 blocks each)


def gym_cells(state, anim):
    """The gym as field_camera.c draws it: per metatile, by its layer type, into BG3/BG2/
    BG1; the beam state's metatiles (the gym script's setmetatile) and the motorized
    door's tile animation frame (src/tileset_anims.c: 7 tiles at 880). No border: the
    screen outside the map shows the black backdrop (as the border block does)."""
    prim, sec = 'data/tilesets/primary/building', 'data/tilesets/secondary/vermilion_gym'

    def tileset(d):
        ts = load_tiles(d + '/tiles.png')
        mt = [v for (v,) in struct.iter_unpack('<H', open(path(d + '/metatiles.bin'), 'rb').read())]
        at = [v for (v,) in struct.iter_unpack('<I', open(path(d + '/metatile_attributes.bin'), 'rb').read())]
        return ts, [mt[i:i + 8] for i in range(0, len(mt), 8)], at
    pt, pm, pa = tileset(prim)
    st, sm, sa = tileset(sec)
    st = list(st)
    frames = load_tiles(sec + '/anim/motorizeddoor/%d.png' % anim)
    for k in range(7):
        st[240 + k] = frames[k]
    pals = []
    for i in range(16):
        d = prim if i < 7 else sec
        f = '%s/palettes/%02d.pal' % (d, i)
        pals.append(B.pal16(B.pal_file(f)) if os.path.exists(path(f)) else B.pal16([]))
    blocks = [v & 0x3FF for (v,) in struct.iter_unpack('<H', open(path('data/layouts/VermilionCity_Gym/map.bin'), 'rb').read())]
    layers = ({}, {}, {})

    def cell(e):
        t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        tile = pt[t] if t < 640 else st[t - 640] if t - 640 < len(st) else None
        if tile is None:
            return None
        return B.flip_tile([px for row in tile for px in row], hf, vf), pals[bank]
    for bi, m in enumerate(blocks):
        by, bx = divmod(bi, GYM_W)
        m = BEAM[state].get((bx, by), m)
        meta, attr = (pm[m], pa[m]) if m < 640 else (sm[m - 640], sa[m - 640])
        kind = (attr & 0x60000000) >> 29
        for q in range(4):
            x, y = GYM_TX + bx * 2 + (q & 1), GYM_TY + by * 2 + (q >> 1)
            bottom, top = cell(meta[q]), cell(meta[4 + q])
            if kind == 0:
                layers[0][(x, y)] = cell(0x3014)
                layers[1][(x, y)] = bottom
                layers[2][(x, y)] = top
            elif kind == 1:
                layers[0][(x, y)] = bottom
                layers[1][(x, y)] = top
            else:
                layers[0][(x, y)] = bottom
                layers[2][(x, y)] = top
    return layers


def gym_state(t):
    return 'on' if t < BARS[1] else ('half' if t < round(BARS[1] + 19.15) else 'off')


RED_START, RED_STOP, RED_GO = 240, 112, 40     # feet lines (world px), run from frame 40
RUN_NORTH = [(6, 5), (7, 3), (6, 5), (8, 3)]   # sAnim_RunNorth: surf_run pics 6,7,6,8


def c1_red_feet(t):
    return max(RED_STOP, RED_START - 2 * max(0, t - RED_GO))


def c1_cam(t):
    return min(max(c1_red_feet(t) - 88, 24), RED_START - 88)


def cut1(c):
    y0 = 24                                        # world row of map row 0 (min camera)
    base = None
    for st in ('on', 'half', 'off'):
        for an in (0, 1):
            cells = gym_cells(st, an)
            ls = [layer_from_cells(cells[i], 0, -y0 // 8) for i in range(3)]
            c.variants[(st, an)] = ls
            if base is None:
                base = ls
    c.layers = list(c.variants[('on', 0)])
    prev = ('on', 0)
    for t in range(c.frames):
        v = (gym_state(t), (t // 2) % 2)
        if v != prev:
            c.patch_seq.append((t, v))
            prev = v
    names = [('emote', 'emote'), ('red', 'red_field'), ('red_run', 'red_run'), ('pika', 'pika_field'), ('surge', 'surge_field'),
             ('gentleman', 'gentleman'), ('balding', 'balding'), ('sailor', 'sailor')]
    for n, s in names:
        c.track(n, s)
    gx = GYM_TX * 8
    arrive = RED_GO + (RED_START - RED_STOP) // 2
    for t in range(c.frames):
        cam = c1_cam(t)
        vofs = cam - y0 - VIEW_Y
        c.set_scroll(t, 0, vofs, 0, vofs, 0, vofs)
        wy = lambda feet, h: feet - h - cam       # noqa: E731  sprite top in the view
        for n, bx, by, fr, fl in (('gentleman', 7, 8, 2, 0), ('balding', 2, 11, 0, 0), ('sailor', 8, 13, 2, 0)):
            c.key(t, n, gx + bx * 16, wy((by + 2) * 16 + 16, 32), fr, fl)
        c.key(t, 'surge', gx + 5 * 16, wy(4 * 16 + 16, 32), 0)
        feet = c1_red_feet(t)
        running = RED_GO <= t < arrive
        if running:
            k, acc = (t - RED_GO) % 16, 0
            for fr, d in RUN_NORTH:
                if k < acc + d:
                    break
                acc += d
            c.key(t, 'red_run', gx + 5 * 16, wy(feet, 32), fr)
        else:
            c.key(t, 'red', gx + 5 * 16, wy(feet, 32), 1)
        # PIKACHU one tile behind; at the stop it steps east, then north beside RED
        side, pfeet, pfl = 0, feet + 16, 0
        if t >= arrive:
            k = t - arrive
            side = min(16, 2 * k)
            pfeet = RED_STOP + 16 - max(0, min(16, 2 * (k - 8)))
            if k < 8:
                pf, pfl = 7 + (k // 4) % 2, HFLIP
            elif k < 16:
                pf = 5 + (k // 4) % 2
            else:
                pf = 1
        else:
            pf = (5 + (t // 4) % 2) if running else 1
        c.key(t, 'pika', gx + 5 * 16 + side, wy(pfeet, 16), pf, pfl)
        e0 = round(BARS[1] + 3 * 19.15)
        if t >= e0:
            n = 0 if t < e0 + 2 else 1 if t < e0 + 4 else 2
            c.key(t, 'emote', gx + 5 * 16, wy(4 * 16 + 16, 32) - 16 - (2 if t < e0 + 6 else 0), n)
    # from white (maps and sprites only: the backdrop, outside the map, stays black)
    for t in range(20):
        c.ev(t, EV_BLEND, T_ALL, 16 - (t * 16) // 20, WHITE)
    c.ev(20, EV_BLEND, T_ALL, 0, WHITE)
    for t0 in (124, 130):                          # the battle's two flashes
        c.ev(t0, EV_BLEND, T_ALL, 12, WHITE)
        c.ev(t0 + 3, EV_BLEND, T_ALL, 0, WHITE)
    c.ev(133, EV_BLEND, T_ALL, 16, WHITE)


# ---------------------------------------------------------------- battle layout
P_HOME, R_HOME = (24, 32), (148, 1)
STAGE_VOFS = 16 - VIEW_Y


def stage_track_hofs(t):
    """S3b and S4a: the stage drifts 1 px/frame (camera pan), continuous over both."""
    return t - BARS[3] - 38


RED_OUT, PIKA_IN = 57, 66


def cut2(c):
    c.layers[0] = stage_layer()
    c.bld_alpha = BLDALPHA
    for n, s, a in (('ball', 'ball', False), ('pika', 'pika_back', False), ('pg1', 'pika_back', False),
                    ('pg2', 'pika_back', False), ('raichu', 'raichu', True), ('surge', 'surge_pic', False),
                    ('red', 'red_back', False)):
        c.track(n, s, a)
    for u in range(c.frames):
        c.set_scroll(u, 0, STAGE_VOFS)
        ein = s_ease(u / 24.0)
        sx = -64 + (R_HOME[0] - 4 + 64) * ein if u < 38 else R_HOME[0] - 4 + (u - 38) * 8
        c.key(u, 'surge', sx, -6)
        rx = W - (W - P_HOME[0]) * ein if u < RED_OUT else P_HOME[0] - (u - RED_OUT) * 12
        c.key(u, 'red', rx, 32, 1 if 52 <= u < RED_OUT + 4 else 0)
        if 38 <= u < 50:
            f = (u - 38) / 12.0
            c.key(u, 'ball', 156 + 20 * f, 6 + 30 * f - 28 * math.sin(math.pi * f), (u // 2) % 2)
        if u >= 50:
            s = 1.0 if u >= 58 else 0.25 + 0.75 * (u - 50) / 8.0
            pose = 1 if 60 <= u < 68 else 0
            cx, bottom = R_HOME[0] + 32, R_HOME[1] + 64    # the send-out grows from the feet
            c.key(u, 'raichu', cx - 32, bottom - 32 * s - 32, pose, 0, round(256 / s))
        if u >= PIKA_IN:
            f = s_ease((u - PIKA_IN) / 8.0)
            px = -64 + (P_HOME[0] + 64) * f
            py = P_HOME[1] - (2 if u >= PIKA_IN + 8 else 0)
            if u < PIKA_IN + 8:
                c.key(u, 'pg2', px - 28, py, 0, BLEND)
                c.key(u, 'pg1', px - 14, py, 0, BLEND)
            c.key(u, 'pika', px, py)
    for u in range(8):
        c.ev(u, EV_BLEND, T_ALL, 16 - u * 2, WHITE)
    c.ev(8, EV_BLEND, T_ALL, 0, WHITE)
    for u in range(50, 63):                        # the send-out's white
        c.ev(u, EV_OBJ_BLEND, 'raichu', max(0, 16 - (u - 50) * 16 // 12), WHITE)


CHEEKS_FLIPPED = [(64 - 1 - 33, 26), (64 - 1 - 17, 27)]    # red pixels of pikachu/front.png
ORANGE = (31, 18, 0)                                        # graphics/intro/scene_2/bg.gbapal


def cut3(c):
    c.layers[0] = solid_layer(ORANGE)
    for n, s, a in (('sp0', 'spark2_eo', True), ('sp1', 'spark2_eo', True),
                    ('pika', 'pika_front', True), ('raichu', 'raichu', True)):
        c.track(n, s, a)
    for u in range(c.frames):
        f = s_ease(u / 12.0)
        px, py = -128 + 104 * f, -22               # the 2x picture's corner, as drawn
        c.key(u, 'pika', px + 32, py + 32, 0, 0, -0x80)
        if u >= 19:
            g = s_ease((u - 19) / 12.0)
            c.key(u, 'raichu', 240 - 124 * g + 32, -14 + 32, 1 if u >= 30 else 0, 0, 0x80)
        if u >= 28:
            for k, (cx, cy) in enumerate(CHEEKS_FLIPPED):
                if (u + k * 2) % 6 < 4:
                    bx, by = px + cx * 2 - 16 + (8 if k else -8), py + cy * 2 - 16
                    c.key(u, 'sp%d' % k, bx + 8, by + 8, (u // 3 + k) % 3, 0, 0x80)
        c.set_scroll(u, 0, 0)


def cut4(c):
    """S3b: the stage drifting 1 px/frame (R2-5: no entry streaks)."""
    c.layers[0] = stage_layer()
    for n, s in (('s0', 'spark2'), ('s1', 'spark2'), ('s2', 'spark2'), ('pika', 'pika_back'), ('raichu', 'raichu')):
        c.track(n, s)
    for v in range(c.frames):
        c.set_scroll(v, v, STAGE_VOFS)
        c.key(v, 'raichu', R_HOME[0], R_HOME[1], 1 if v < 12 else 0)
        c.key(v, 'pika', P_HOME[0], P_HOME[1] + (2 if v >= 19 else 0))
        if v >= 19:
            for k in range(3):
                a = v / 3.0 + k * 2.1
                c.key(v, 's%d' % k, P_HOME[0] + 24 + 26 * math.cos(a), P_HOME[1] + 12 + 12 * math.sin(a), (v // 3 + k) % 3)
    c.ev(0, EV_CRY, 0, CRY_RAICHU)


def dash(u, a, b, dur):
    f = min(1.0, u / float(dur))
    f = f * f
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def trail_keys(c, t, name, ghosts, pos_fn, u, frame=0, flags=0, step=3):
    for k in range(len(ghosts), 0, -1):
        if u - k * step >= 0:
            c.key(t, ghosts[k - 1], *pos_fn(u - k * step), frame, flags | BLEND)
    c.key(t, name, *pos_fn(u), frame, flags)


def cut5(c):
    """S4a: clash in the middle, on the drifting stage."""
    c.layers[0] = stage_layer()
    c.bld_alpha = BLDALPHA
    for n, s in (('impact', 'impact'), ('pika', 'pika_back'), ('raichu', 'raichu'),
                 ('pg1', 'pika_back'), ('pg2', 'pika_back'), ('rg1', 'raichu'), ('rg2', 'raichu')):
        c.track(n, s)
    mid = ((P_HOME[0] + R_HOME[0]) / 2, (P_HOME[1] + R_HOME[1]) / 2)
    hit = 19
    for u in range(c.frames):
        sh = (2 if u % 2 else -2) if hit <= u < hit + 6 else 0
        c.set_scroll(u, 39 + u - sh, STAGE_VOFS)
        if u < hit:
            trail_keys(c, u, 'pika', ['pg1', 'pg2'], lambda x: dash(x, P_HOME, (mid[0] - 24, mid[1] + 8), hit), u, step=4)
            trail_keys(c, u, 'raichu', ['rg1', 'rg2'], lambda x: dash(x, R_HOME, (mid[0] + 24, mid[1] - 8), hit), u, step=4)
        else:
            f = s_ease((u - hit) / 18.0)
            c.key(u, 'pika', mid[0] - 24 + (P_HOME[0] - mid[0] + 24) * f + sh, mid[1] + 8 + (P_HOME[1] - mid[1] - 8) * f)
            c.key(u, 'raichu', mid[0] + 24 + (R_HOME[0] - mid[0] - 24) * f + sh, mid[1] - 8 + (R_HOME[1] - mid[1] + 8) * f)
            if u < hit + 6:
                c.key(u, 'impact', mid[0] + 16 + sh, mid[1] + 16)


def cut6(c):
    """S4b: racing side by side over the Extreme Speed background (rec. 7)."""
    c.layers[0] = highspeed_layer('opponent')
    c.bld_alpha = BLDALPHA
    for n, s in (('impact', 'impact'), ('pika', 'pika_front'), ('raichu', 'raichu'), ('dust', 'dust'),
                 ('pg1', 'pika_front'), ('rg1', 'raichu'), ('pg2', 'pika_front'), ('rg2', 'raichu')):
        c.track(n, s)
    for v in range(c.frames):
        c.set_scroll(v, v * 8, -VIEW_Y)
        jit = lambda k: round(2 * math.sin(v * 1.3 + k))    # noqa: E731
        rx = 150 - max(0, v - 8) * 2.2 if v < 19 else 126
        ry = -12 + (max(0, v - 13) * 2.5 if v < 19 else 15)
        turn = 15 <= v < 19
        rfl, rpose = (0, 1) if turn else (HFLIP, 0)
        px, py = 20, 34
        if v >= 19:
            py += min(10, (v - 19) * 2)
            px -= min(12, (v - 19) * 2)
        for k in (2, 1):
            if not turn:
                c.key(v, 'rg%d' % k, rx - 20 * k, ry + jit(1), rpose, rfl | BLEND)
            c.key(v, 'pg%d' % k, px - 20 * k, py + jit(0), 0, HFLIP | BLEND)
        c.key(v, 'raichu', rx, ry + jit(1), rpose, rfl)
        c.key(v, 'pika', px, py + jit(0), 0, HFLIP)
        c.key(v, 'dust', px - 8, py + 48, (v // 2) % 3)
        if 19 <= v < 25:
            c.key(v, 'impact', px + 44, py + 8)


def cut7(c):
    """S4c: PIKACHU's Quick Attack, highspeed_opponent (the scroll follows the attacker)."""
    c.layers[0] = highspeed_layer('opponent')
    c.bld_alpha = BLDALPHA
    for n, s in (('impact', 'impact'), ('pika', 'pika_back'), ('raichu', 'raichu'),
                 ('pg1', 'pika_back'), ('pg2', 'pika_back'), ('pg3', 'pika_back')):
        c.track(n, s)
    hit = 19
    target = (R_HOME[0] - 36, R_HOME[1] + 20)
    for v in range(c.frames):
        c.set_scroll(v, (38 + v) * 8, -VIEW_Y)
        rec = min(10, max(0, v - hit) * 2)
        shake = (3 if v % 2 else -3) if hit <= v < hit + 12 else 0
        c.key(v, 'raichu', R_HOME[0] + rec + shake, R_HOME[1] - rec // 2)
        if v < hit:
            trail_keys(c, v, 'pika', ['pg1', 'pg2', 'pg3'], lambda x: dash(x, P_HOME, target, hit), v)
        else:
            f = s_ease((v - hit) / 18.0)
            c.key(v, 'pika', target[0] + (P_HOME[0] - target[0]) * f, target[1] + (P_HOME[1] - target[1]) * f)
        if hit <= v < hit + 6:
            c.key(v, 'impact', R_HOME[0] + 16, R_HOME[1] + 20)


def cut8(c):
    """S4d: RAICHU's counter, highspeed_player, scrolling the other way."""
    c.layers[0] = highspeed_layer('player')
    c.bld_alpha = BLDALPHA
    for n, s in (('impact', 'impact'), ('dust', 'dust'), ('pika', 'pika_back'), ('raichu', 'raichu'),
                 ('rg1', 'raichu'), ('rg2', 'raichu'), ('rg3', 'raichu')):
        c.track(n, s)
    hit = 18
    target = (P_HOME[0] + 40, P_HOME[1] - 16)
    for v in range(c.frames):
        c.set_scroll(v, -v * 8, -VIEW_Y)
        knock = min(16, max(0, v - hit) * 3)
        shake = (3 if v % 2 else -3) if hit <= v < hit + 12 else 0
        c.key(v, 'pika', P_HOME[0] - knock + shake, P_HOME[1])
        if v >= hit:
            c.key(v, 'dust', P_HOME[0] + 20 - knock, P_HOME[1] + 50, (v // 2) % 3)
        if v < hit:
            trail_keys(c, v, 'raichu', ['rg1', 'rg2', 'rg3'], lambda x: dash(x, R_HOME, target, hit), v, 1)
        else:
            f = s_ease((v - hit) / 18.0)
            c.key(v, 'raichu', target[0] + (R_HOME[0] - target[0]) * f, target[1] + (R_HOME[1] - target[1]) * f)
        if hit <= v < hit + 6:
            c.key(v, 'impact', P_HOME[0] + 20, P_HOME[1] + 12)


def storm(c, t, shake=0):
    xu, xl = thunder_phase(t)
    c.set_scroll(t - c.start, xu + shake, THUNDER_VOFS_UP, xl + shake, THUNDER_VOFS_DOWN)


def storm_setup(c):
    up, down = thunder_layers()
    c.layers[0], c.layers[1] = up, down
    c.split_row = SPLIT_ROW
    c.ev(0, EV_BLEND, T_BG, 9, STORM)


N_BOLT = 10


def cut9(c):
    """S5: THUNDERBOLT clash over the storm."""
    storm_setup(c)
    names = [('pika', 'pika_front'), ('raichu', 'raichu'), ('shock', 'shock')]
    names += [('l%d' % k, 'lightning') for k in range(3)]
    names += [('e%d' % k, 'electricity') for k in range(6)]
    names += [('b%d' % k, 'spark1') for k in range(2 * N_BOLT)]
    for n, s in names:
        c.track(n, s)
    for u in range(c.frames):
        sh = (1 if u % 2 else -1) if 38 <= u < 50 else 0
        storm(c, c.start + u, sh)
        pk_x = 8 + (8 if u >= 57 else 0)
        c.key(u, 'pika', pk_x + sh, 26, 0, HFLIP)
        c.key(u, 'raichu', 168 + sh, 22, 1 if u >= 10 else 0)
        if u < 19:
            for who, cx in ((0, pk_x + 32), (1, 200)):
                for k in range(3):
                    a = u / 3.0 + k * 2.1 + who
                    c.key(u, 'e%d' % (who * 3 + k), cx - 16 + 26 * math.cos(a) + sh, 40 - 16 + 18 * math.sin(a), (u + k) % 4)
        knot = 120
        if u >= 38:
            knot = 120 - 20 * s_ease((u - 38) / 19.0) if u < 57 else 100 + 50 * s_ease((u - 57) / 19.0)
        if u >= 19:
            reach = min(1.0, (u - 19) / 19.0)
            for side, (x0, y0, x1, y1, ph) in enumerate(((pk_x + 44, 48, pk_x + 44 + (knot - pk_x - 44) * reach, 44, u),
                                                          (196, 44, 196 + (knot - 196) * reach, 44, u + 1))):
                n = min(N_BOLT - 1, int(math.dist((x0, y0), (x1, y1)) // 12))
                for k in range(n + 1):
                    f = k / float(max(1, n))
                    wob = 5 * math.sin(k * 2.3 + ph)
                    c.key(u, 'b%d' % (side * N_BOLT + k), x0 + (x1 - x0) * f - 8 + sh, y0 + (y1 - y0) * f - 8 + wob, (k + ph // 2) % 4)
        if u >= 38:
            c.key(u, 'shock', knot - 16 + sh, 28)
            for k in range(2):
                c.key(u, 'e%d' % k, knot - 16 + (k * 2 - 1) * 12 + sh, 28 + (k * 2 - 1) * 6, (u + k) % 4)
            if u < 46:
                for k, y in enumerate((-36, -20, 12)):
                    c.key(u, 'l%d' % k, knot - 16 + sh, 44 + y - 16, (k + u // 2) % 2)
    c.ev(38, EV_BLEND, T_ALL, 10, WHITE)
    c.ev(40, EV_BLEND, T_ALL, 0, WHITE)
    c.ev(40, EV_BLEND, T_BG, 9, STORM)


# S6: PIKACHU hops between stops; each THUNDER lands on the oldest afterimage only
P_STOP1 = (88, -4)
P_MID1 = (56, 14)
P_STOP2 = (104, 40)                 # R2-2: moved from (108,36); checked in check_contact()
P_MID2 = ((P_STOP1[0] + P_STOP2[0]) / 2, (P_STOP1[1] + P_STOP2[1]) / 2)
P_HIT = (R_HOME[0] - 30, R_HOME[1] + 14)
STRIKES = ((0, P_HOME), (19, P_STOP1))


def lerp(a, b, f):
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def s6_pika(u):
    wob = (round(2 * math.sin(u / 2.0)), round(math.cos(u / 2.0)))
    if u < 15:
        ghosts = []
        if u < 1:
            ghosts.append((P_HOME, True))
        if u < 6:
            ghosts.append((P_MID1, False))
        return (P_STOP1[0] + wob[0], P_STOP1[1] + wob[1]), ghosts
    if u < 34:
        body = lerp(P_STOP1, P_STOP2, min(1.0, (u - 15) / 4.0))
        if u >= 19:
            body = (P_STOP2[0] + wob[0], P_STOP2[1] + wob[1])
        ghosts = []
        if u <= 19:
            ghosts.append((P_STOP1, u == 19))
        if 15 <= u < 24:
            ghosts.append((P_MID2, False))
        return body, ghosts
    if u < 38:
        f = (u - 34) / 4.0
        return lerp(P_STOP2, P_HIT, f * f), [(P_STOP2, False)]
    if u < 44:
        return P_HIT, []
    return lerp(P_HIT, P_HOME, s_ease(min(1.0, (u - 44) / 12.0))), []


def cut_s6(c):
    """S6 (three cuts: the storm, the impact burst, the storm): AGILITY."""
    u0 = c.start - BARS[7]
    burst = c.name == 'c11'
    if burst:
        c.layers[0] = impact_layer()
    else:
        storm_setup(c)
    c.bld_alpha = BLDALPHA
    names = [('impact', 'impact'), ('pika', 'pika_back'), ('raichu', 'raichu'), ('hitg', 'pika_hit'),
             ('g1', 'pika_ghost'), ('g2', 'pika_ghost'), ('s0', 'spark2'), ('s1', 'spark2'), ('s2', 'spark2')]
    names += [('l%d' % k, 'lightning') for k in range(3)]
    for n, s in names:
        c.track(n, s)
    c.ev(0, EV_OBJ_BLEND, 'pika_hit', 16, WHITE)     # the struck afterimage: white (sprite only)
    for i in range(c.frames):
        u = u0 + i
        sh = (3 if u % 2 else -3) if 38 <= u < 50 else 0
        if burst:
            c.set_scroll(i, sh, 24 - VIEW_Y)
        else:
            storm(c, BARS[7] + u, sh)
        ry = R_HOME[1] + (0 if u < 57 else (u - 57) * 5)
        c.key(i, 'raichu', R_HOME[0] + sh, ry, 1 if u < 30 else 0)
        body, ghosts = s6_pika(u)
        gi = 1
        for pos, struck in ghosts:
            if struck:
                c.key(i, 'hitg', *pos)
            else:
                c.key(i, 'g%d' % gi, *pos, 0, BLEND)
                gi += 1
        c.key(i, 'pika', *body)
        for s0, spot in STRIKES:
            if s0 <= u < s0 + 8:
                for k, y in enumerate((-40, -8, 24)):
                    c.key(i, 'l%d' % k, spot[0] + 16, spot[1] + y, (k + u) % 2)
        if 38 <= u < 44:
            c.key(i, 'impact', R_HOME[0] + 16 + sh, R_HOME[1] + 20)
        if u >= 57:
            for k in range(3):
                a = u / 3.0 + k * 2.1
                c.key(i, 's%d' % k, body[0] + 24 + 24 * math.cos(a), body[1] + 10 + 10 * math.sin(a), (u // 3 + k) % 3)
        if 47 <= u < 57:
            c.ev(i, EV_OBJ_BLEND, 'raichu', 16 if (u - 47) % 4 < 2 else 0, WHITE)
        if u >= 70:
            c.ev(i, EV_BLEND, T_ALL, min(16, (u - 69) * 3), WHITE)


S7_ONE_X = 21                                    # R2-3: the 1x pair for 21 frames (t595-615)
FADE_BLACK = 676                                 # F1382 as FR/LG, 14 frames to black


def s7_layout():
    """R2-3: RED's back pic high enough that cap and shoulders are inside the letterbox;
    PIKACHU up and to the right of him, 20 px between the two pictures' opaque pixels."""
    rb = content_box(SHEETS['red_back'], 1)      # with the arm up (frame 1)
    pf = content_box(SHEETS['pika_front'])
    red = (4, 26)
    px = red[0] + rb[2] + 1 + 20 - pf[0]
    py = red[1] + rb[1] - 14 - pf[1]            # its feet at RED's cheek line, hopping
    return red, (px, py)


def cut13(c):
    """S7: the win on FR/LG's own white; RED and PIKACHU as a pair (1x, 21 frames), one
    integer cut to 2x (PIKACHU's happy frame), black as the song rings out (as F1382)."""
    c.layers[0] = solid_layer(WHITE)
    for n, s, a in (('s0', 'spark2', False), ('s1', 'spark2', False), ('pika', 'pika_front', False),
                    ('red', 'red_back', False), ('happy', 'pika_happy', True)):
        c.track(n, s, a)
    red, pk = s7_layout()
    pc = content_box(SHEETS['pika_front'])
    for u in range(c.frames):
        c.set_scroll(u, 0, 0)
        if u < S7_ONE_X:
            hop = round(6 * math.sin(math.pi * min(1.0, u / 14.0)))
            c.key(u, 'red', *red, 1 if u >= 6 else 0)
            c.key(u, 'pika', pk[0], pk[1] - hop)
            if 8 <= u < 18:
                for k, (cx, cy) in enumerate([(33, 25), (17, 26)]):
                    c.key(u, 's%d' % k, pk[0] + cx - 8 + (6 if k == 0 else -6), pk[1] - hop + cy - 8, (u // 3 + k) % 3)
        else:
            c.key(u, 'happy', 88, 12, 0, 0, 0x80)
    for u in range(8):
        c.ev(u, EV_BLEND, T_OBJ, 16 - u * 2, WHITE)
    c.ev(8, EV_BLEND, T_OBJ, 0, WHITE)
    for t in range(FADE_BLACK, FADE_BLACK + 15):
        c.ev(t - c.start, EV_BLEND, T_ALL, min(16, (t - FADE_BLACK) * 16 // 14), BLACK)
    del pc


BUILD = {'c1': cut1, 'c2': cut2, 'c3': cut3, 'c4': cut4, 'c5': cut5, 'c6': cut6, 'c7': cut7, 'c8': cut8,
         'c9': cut9, 'c10': cut_s6, 'c11': cut_s6, 'c12': cut_s6, 'c13': cut13}


# ---------------------------------------------------------------- checks (R2-2, R2-3)
def check_contact():
    """R2-2: at S6's second stop PIKACHU (in front) and RAICHU either overlap by 8+ px or
    stay 4+ px apart. R2-3: the S7 pair's gap."""
    out = []
    rs, ps = SHEETS['raichu'], SHEETS['pika_back']
    for u in (19, 25, 30):
        body, _ = s6_pika(u)
        pm = mask(ps, 0, int(body[0]), int(body[1]))
        rm = mask(rs, 1 if u < 30 else 0, R_HOME[0], R_HOME[1])
        inter = pm & rm
        if inter:
            # depth: how far PIKACHU must move down-left before they no longer touch
            d = 0
            while pm & rm:
                d += 1
                pm = {(x - 1, y + 1) for x, y in pm}
            out.append('S6 u%d: overlap, %d px deep' % (u, d))
        else:
            dist = min(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in pm for b in rm)
            out.append('S6 u%d: gap %d px' % (u, dist))
    rel = [(thunder_phase(t)[1] - thunder_phase(t)[0]) % 256 for t in range(BARS[6], BARS[8])]
    out.append('R2-1 cloud layers: lower minus upper phase %d..%d px (period 256; 0 would line up)' % (min(rel), max(rel)))
    red, pk = s7_layout()
    rb, pf = content_box(SHEETS['red_back'], 1), content_box(SHEETS['pika_front'])
    out.append('S7 gap %d px, RED y %d..%d in the view' % (pk[0] + pf[0] - (red[0] + rb[2]) - 1, red[1] + rb[1], red[1] + rb[3]))
    return out


# ---------------------------------------------------------------- packing and output
def pack_cut(c):
    layers = list(c.layers)
    extra = []
    keys = list(c.variants)
    for k in keys:
        extra += c.variants[k]
    tiles, pals, maps = B.pack_bg(layers + extra)
    base = maps[:3]
    patches = []
    if keys:
        vm = {k: maps[3 + 3 * i:6 + 3 * i] for i, k in enumerate(keys)}
        boxes = []
        for li in range(3):
            if base[li] is None:
                boxes.append(None)
                continue
            diff = [i for k in keys for i in range(len(base[li])) if vm[k][li][i] != base[li][i]]
            if not diff:
                boxes.append(None)
                continue
            xs = [(i // 1024) * 32 + i % 32 for i in diff]
            ys = [(i % 1024) // 32 for i in diff]
            boxes.append((min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
        last = None
        for t, k in c.patch_seq:
            if last is not None and all(vm[k][li] == vm[last][li] for li in range(3) if boxes[li]):
                continue
            last = k
            for li, box in enumerate(boxes):
                if box is None:
                    continue
                x0, y0, w, h = box
                ents = [vm[k][li][((x0 + x) // 32) * 1024 + (y0 + y) * 32 + (x0 + x) % 32] for y in range(h) for x in range(w)]
                patches.append((t, li, x0, y0, w, h, ents))
    return tiles, pals, base, patches


class Gba:
    """A cut's frames as the hardware shows them (see the module docstring)."""

    def __init__(self, c, packed):
        self.c = c
        self.tiles, self.bgpals, maps, self.patches = packed
        self.maps = [list(m) if m is not None else None for m in maps]
        self.unfaded = {('bg', i): list(p) for i, p in enumerate(self.bgpals)}
        for _, s, _ in c.tracks:
            self.unfaded[('obj', SHEETS[s].tag)] = list(SHEETS[s].pal)
        self.faded = {k: list(v) for k, v in self.unfaded.items()}

    def blend(self, keys, coeff, col):
        for k in keys:
            self.faded[k] = [B.blend5(cc, coeff, col) for cc in self.unfaded[k]]

    def apply(self, t):
        for (et, typ, target, coeff, col) in self.c.events:
            if et != t:
                continue
            if typ == EV_BLEND:
                keys = [k for k in self.unfaded if target == T_ALL or (k[0] == 'bg') == (target == T_BG)]
                self.blend(keys, coeff, col)
            elif typ == EV_OBJ_BLEND:
                self.blend([('obj', SHEETS[target].tag)], coeff, col)
        for (pt, li, x0, y0, w, h, ents) in self.patches:
            if pt == t:
                for y in range(h):
                    for x in range(w):
                        self.maps[li][((x0 + x) // 32) * 1024 + (y0 + y) * 32 + (x0 + x) % 32] = ents[y * w + x]

    def bg_pixel(self, li, sx, sy):
        m = self.maps[li]
        if m is None:
            return None
        sc = self.c.scroll[self.t]
        hofs, vofs = sc[li * 2], sc[li * 2 + 1]
        mx, my = (sx + hofs) % 512, (sy + vofs) % 256
        tx, px = divmod(mx, 8)
        ty, py = divmod(my, 8)
        e = m[(tx // 32) * 1024 + ty * 32 + tx % 32]
        t_, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        v = self.tiles[t_][(7 - py if vf else py) * 8 + (7 - px if hf else px)]
        return self.faded[('bg', bank - B.BG_BANK0)][v] if v else None

    def obj_layer(self):
        """The front-most opaque sprite pixel per screen pixel, and whether it is
        semi-transparent. Earlier tracks are in front (lower subpriority)."""
        buf = {}
        keys = self.c.keys[self.t]
        for name, sname, aff in reversed(self.c.tracks):
            k = keys.get(name)
            if not k:
                continue
            x, y, f, fl, a = k
            s = SHEETS[sname]
            pal = self.faded[('obj', s.tag)]
            fr = s.frames[f]
            semi = bool(fl & BLEND)
            if aff:
                cx, cy = x + s.w // 2, y + s.h // 2
                bw, bh = 2 * s.w, 2 * s.h
                ox, oy = cx - s.w, cy - s.h
                d = abs(a)
                for by in range(bh):
                    Y = oy + by
                    if not VIEW_Y <= Y < VIEW_Y + VIEW_H:
                        continue
                    ty = ((d * (by - bh // 2)) >> 8) + s.h // 2
                    if not 0 <= ty < s.h:
                        continue
                    for bx in range(bw):
                        X = ox + bx
                        if not 0 <= X < W:
                            continue
                        tx = ((a * (bx - bw // 2)) >> 8) + s.w // 2
                        if 0 <= tx < s.w:
                            v = fr[ty][tx]
                            if v:
                                buf[(X, Y)] = (pal[v], semi)
            else:
                for yy in range(s.h):
                    Y = y + yy
                    if not VIEW_Y <= Y < VIEW_Y + VIEW_H:
                        continue
                    row = fr[s.h - 1 - yy if fl & VFLIP else yy]
                    for xx in range(s.w):
                        X = x + xx
                        if not 0 <= X < W:
                            continue
                        v = row[s.w - 1 - xx if fl & HFLIP else xx]
                        if v:
                            buf[(X, Y)] = (pal[v], semi)
        return buf

    def frame(self, t):
        self.t = t
        self.apply(t)
        img = Image.new('RGB', (W, H))
        px = img.load()
        obj = self.obj_layer()
        for Y in range(VIEW_Y, VIEW_Y + VIEW_H):
            bg2_on = not (self.c.split_row and Y < self.c.split_row)
            for X in range(W):
                top = self.bg_pixel(2, X, Y)
                if top is None:
                    under = (self.bg_pixel(1, X, Y) if bg2_on else None)
                    if under is None:
                        under = self.bg_pixel(0, X, Y)
                    if under is None:
                        under = (0, 0, 0)
                    o = obj.get((X, Y))
                    if o:
                        col, semi = o
                        if semi and self.c.bld_alpha:
                            # as mGBA mixes (8-bit channels, c << 3 | c >> 2), so the
                            # frames match the emulator's captures exactly
                            col = tuple(min(255, (((a << 3) | (a >> 2)) * EVA + ((b << 3) | (b >> 2)) * EVB) >> 4) >> 3
                                        for a, b in zip(col, under))
                        top = col
                    else:
                        top = under
                px[X, Y] = (top[0] << 3, top[1] << 3, top[2] << 3)
        return img


def ident(s):
    return ''.join(w.capitalize() for w in s.split('_'))


def scene_tags(c):
    return sorted({SHEETS[s].tag for _, s, _ in c.tracks})


def write_header(cuts, used):
    L = ['// Generated by tools/make_intro_opening_a.py. Do not edit: change the direction',
         '// there and run it again. Opening direction (a): official in-game graphics only.', '']
    L.append('#define NUM_SCENES %d' % len(cuts))
    tags = []
    for s in used:
        if SHEETS[s].tag not in tags:
            tags.append(SHEETS[s].tag)
    L.append('enum {')
    L.append('    %s = 0x1400,' % tags[0])
    L += ['    %s,' % t for t in tags[1:]]
    L += ['};', '']
    for s in used:
        L.append('static const u32 sA_%s_Gfx[] = INCBIN_U32("%s/%s.4bpp");' % (ident(s), OUT, s))
        L.append('static const u16 sA_%s_Pal[] = INCBIN_U16("%s/%s.gbapal");' % (ident(s), OUT, s))
    L.append('')
    for c, (tiles, pals, maps, patches) in cuts:
        n, N = c.name, c.name.upper()
        L.append('// ---- %s %s: code frames %d-%d' % (n, c.title, c.start, c.start + c.frames - 1))
        L.append('static const u32 sA_%s_BgGfx[] = INCBIN_U32("%s/%s_bg.4bpp");' % (N, OUT, n))
        L.append('static const u16 sA_%s_BgPal[] = INCBIN_U16("%s/%s_bg.gbapal");' % (N, OUT, n))
        for li, m in enumerate(maps):
            if m is not None:
                L.append('static const u16 sA_%s_Map%d[] = INCBIN_U16("%s/%s_map%d.bin");' % (N, li, OUT, n, li))
        L.append('#define %s_FRAMES %d' % (N, c.frames))
        L.append('#define %s_TRACKS %d' % (N, len(c.tracks)))
        L.append('static const struct OpeningTrack sA_%s_Tracks[] = {' % N)
        for i, (name, s, aff) in enumerate(c.tracks):
            sh = SHEETS[s]
            L.append('    {sA_%s_Gfx, &%s, %s, %d, %d, %d, %d}, // %s' % (
                ident(s), OAM[(sh.w, sh.h, aff)], sh.tag, sh.w, sh.h, 20 + i, 20 + i, name))
        L.append('};')
        L.append('static const struct OpeningKey sA_%s_Keys[%s_FRAMES][%s_TRACKS] = {' % (N, N, N))
        for t in range(c.frames):
            ks = []
            for name, _, _ in c.tracks:
                k = c.keys[t].get(name)
                ks.append('{%d, %d, %d, %d, %d}' % k if k else '{0, 0, 0, KEY_HIDE, 0}')
            L.append('    {%s},' % ', '.join(ks))
        L.append('};')
        L.append('static const struct OpeningScroll sA_%s_Scroll[%s_FRAMES] = {' % (N, N))
        for s in c.scroll:
            L.append('    {%d, %d, %d, %d, %d, %d},' % tuple(s))
        L.append('};')
        L.append('static const struct OpeningEvent sA_%s_Events[] = {' % N)
        for (t, typ, target, coeff, col) in sorted(c.events, key=lambda e: e[0]):
            if typ == EV_OBJ_BLEND:
                target = scene_tags(c).index(SHEETS[target].tag)
            L.append('    {%d, %d, %d, %d, RGB(%d, %d, %d)},' % ((t, typ, target, coeff) + tuple(col)))
        L.append('    {0xFFFF},')
        L.append('};')
        if patches:
            for i, (t, li, x, y, w, h, ents) in enumerate(patches):
                L.append('static const u16 sA_%s_Patch%d[] = {%s};' % (N, i, ', '.join('0x%04X' % e for e in ents)))
            L.append('static const struct OpeningPatch sA_%s_Patches[] = {' % N)
            for i, (t, li, x, y, w, h, ents) in enumerate(patches):
                L.append('    {%d, %d, %d, %d, %d, %d, sA_%s_Patch%d},' % (t, li, x, y, w, h, N, i))
            L.append('    {0xFFFF},')
            L.append('};')
        tg = scene_tags(c)
        first = {}
        for s in sorted({s for _, s, _ in c.tracks}):
            first.setdefault(SHEETS[s].tag, s)
        L.append('static const u16 *const sA_%s_ObjPals[] = {%s};' % (N, ', '.join('sA_%s_Pal' % ident(first[t]) for t in tg)))
        L.append('static const u16 sA_%s_ObjPalTags[] = {%s};' % (N, ', '.join(tg)))
        L.append('')
    L.append('static const struct OpeningTableScene sTableScenes[NUM_SCENES] = {')
    for c, (tiles, pals, maps, patches) in cuts:
        N = c.name.upper()
        mp = ', '.join('sA_%s_Map%d' % (N, li) if m is not None else 'NULL' for li, m in enumerate(maps))
        L.append('    { // %s' % c.title)
        L.append('        sA_%s_Tracks, %s_TRACKS, %s_FRAMES, sA_%s_Keys[0], sA_%s_Scroll, sA_%s_Events,' % (N, N, N, N, N, N))
        L.append('        sA_%s_BgGfx, sizeof(sA_%s_BgGfx), {%s}, sA_%s_BgPal, %d,' % (N, N, mp, N, len(pals)))
        L.append('        sA_%s_ObjPals, sA_%s_ObjPalTags, ARRAY_COUNT(sA_%s_ObjPalTags),' % (N, N, N))
        L.append('        0x%04X, %d, %s,' % (c.bld_alpha, c.split_row, 'sA_%s_Patches' % N if patches else 'NULL'))
        L.append('    },')
    L.append('};')
    L.append('')
    L.append('static const u16 sSceneStarts[NUM_SCENES] = {%s};' % ', '.join(str(c.start) for c, _ in cuts))
    L.append('#define OPENING_END %d' % END)
    L.append('')
    open(path(HEADER), 'w').write('\n'.join(L))


def build_cuts(only=None):
    cuts = []
    for name, start, frames, title in CUTS:
        c = Cut(name, start, frames, title)
        BUILD[name](c)
        if only and name not in only:
            cuts.append((c, None))
            continue
        cuts.append((c, pack_cut(c)))
    return cuts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    only = [x for x in a.only.split(',') if x]
    os.makedirs(path(OUT), exist_ok=True)
    cuts = build_cuts()
    for c, packed in cuts:
        tiles, pals, maps, patches = packed
        obj_tiles = sum(SHEETS[sn].w * SHEETS[sn].h // 64 for _, sn, _ in c.tracks)
        assert obj_tiles <= 511, (c.name, obj_tiles)
        assert len(c.tracks) <= 32, (c.name, len(c.tracks))
        print('%s: %d OBJ tiles' % (c.name, obj_tiles))
        print('%s %-22s %3d BG tiles, %2d BG pals, %2d tracks, %3d patches' % (
            c.name, c.title, len(tiles), len(pals), len(c.tracks), len(patches)))
        rows = []
        for i in range(0, len(tiles), 16):
            rt = list(tiles[i:i + 16]) + [tuple([0] * 64)] * (16 - len(tiles[i:i + 16]))
            for y in range(8):
                rows.append([rt[k][y * 8 + x] for k in range(16) for x in range(8)])
        B.write_png_indexed('%s/%s_bg.png' % (OUT, c.name), rows, pals[0])
        B.write_pal('%s/%s_bg.pal' % (OUT, c.name), pals)
        for li, m in enumerate(maps):
            if m is not None:
                with open(path('%s/%s_map%d.bin' % (OUT, c.name, li)), 'wb') as f:
                    f.write(struct.pack('<%dH' % len(m), *m))
    used = sorted({s for c, _ in cuts for _, s, _ in c.tracks})
    for s in used:
        sh = SHEETS[s]
        B.write_png_indexed('%s/%s.png' % (OUT, s), [r for fr in sh.frames for r in fr], sh.pal)
        B.write_pal('%s/%s.pal' % (OUT, s), [sh.pal])
    write_header(cuts, used)
    for line in check_contact():
        print(line)
    if a.preview:
        for c, packed in cuts:
            if only and c.name not in only:
                continue
            d = os.path.join(a.preview, c.name)
            os.makedirs(d, exist_ok=True)
            g = Gba(c, packed)
            for t in range(c.frames):
                g.frame(t).save('%s/t%03d.png' % (d, t))
        print('previews in', a.preview)


if __name__ == '__main__':
    main()
