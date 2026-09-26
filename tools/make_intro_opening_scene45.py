#!/usr/bin/env python3
"""Draw and time scenes 4 and 5 of the new opening: the storm, and THUNDERBOLT.

docs/anim/opening-storyboard.md 3.3 (revised 2026-09-26). Scene 4: F995-1147 (153
frames, bars 4-5 of MUS_INTRO_FIGHT, the sparse bars); scene 5: F1148-1300 (153
frames, bars 6-7). Code frames; a capture shows each one a frame later.

  4a  t0-76   Route 1 under a storm, wide. The sky darkens, the rain starts, the camera
              pans with RED running in (side run); he stops and turns (back view). A
              SPEAROW flock sweeps across from the upper right.
  4b  t77-152 Closer: RED crouched over the small PIKACHU, the flock circling him in
              front and behind; he spreads his arms as they dive (the screen shakes), one
              distant lightning flash.
  5a  t0-18   The small PIKACHU springs off his shoulder and out of the top of the frame.
  5b  t19-76  The camera tilts up into the clouds (RED and the field drop out of frame);
              only then does the big PIKACHU rise into the sky; on beat 3 (F1187)
              lightning strikes it and it cries; it hangs there, cheeks crackling.
  5c  t77-152 THUNDERBOLT: the burst around it, the flock caught and scattered, tumbling;
              the picture whitens into scene 6.

Size rule (art direction, models review): the 64 px PIKACHU and the 64 px RED never
share the screen; with RED, PIKACHU is drawn at his scale (the small PIKACHU).

Flash safety: whole-screen brightness changes are two single flashes (4b t130 and 5b
t38, 208 frames apart) and one slow white-out; the THUNDERBOLT burst is sprites that
do not blink (its rays change by mirroring, the bright area stays the same).

All palette changes are per-frame blends in the event table (BlendPalettes), so the
mock-ups drawn here and the game agree to the pixel.

Writes graphics/intro/opening/scene45/*.png|.bin and src/data/intro_opening_scene45.h;
with --preview DIR the mock-ups DIR/mock4/tNNN.png and DIR/mock5/tNNN.png.
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_opening_art import Figure, stamp, to_image  # noqa: E402
import intro_opening_pikachu as pika  # noqa: E402
import intro_opening_red as red  # noqa: E402
import make_intro_opening_scene2 as s2  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = ROOT + '/graphics/intro/opening/scene45'
HEADER = ROOT + '/src/data/intro_opening_scene45.h'
VIEW_W, VIEW_H, VIEW_Y, MAP = 240, 96, 32, 256
FRAMES = 153
BG_PAL_BANK = 3

# ---------------------------------------------------------------- storm palette
BG_PAL = [(0, 0, 0), (38, 42, 62), (52, 57, 82), (70, 76, 105), (92, 99, 128), (118, 126, 156),
          (150, 158, 188), (30, 38, 36), (34, 66, 46), (48, 88, 58), (66, 112, 72), (90, 136, 88),
          (150, 172, 204), (112, 132, 168), (200, 208, 228), (26, 28, 42)]
C1, C2, C3, C4, C5, C6 = 1, 2, 3, 4, 5, 6          # clouds, dark to light
TREES, G1, G2, G3, G4 = 7, 8, 9, 10, 11            # the field, dark to light
RAIN, RAIN_D, GLOW, DEEP = 12, 13, 14, 15


def _noise(x, y, seed):
    """Smooth, wrapping pseudo-noise on the 256x256 map (sums of sines with whole
    periods, so the sky wraps without a seam)."""
    v = 0.0
    for k, (fx, fy, ph) in enumerate(((1, 0, 0.3), (2, 1, 1.1), (3, 2, 2.3), (5, 3, 0.7), (1, 3, 4.1))):
        v += math.sin(2 * math.pi * (fx * x + fy * y) / MAP + ph + seed * (k + 1)) / (k + 1)
    return v


# The storm sky (art review of 4-5 draft A, change 6): banks of cumulus, one in front
# of the other, each with a scalloped top of round puffs of different sizes that
# repeats every 128 pixels (so its tiles repeat), puffs lying over puffs; the top of
# every puff lit one step lighter for 2 pixels (1 on the steep sides; the light is
# above and behind the clouds), the belly two steps darker under a 1 pixel dither row.
# The banks darken downward: the lightest high up round the break the lightning comes
# from, the darkest low over the field, with a pale band of horizon under the last
# bank's flat bottom, behind the trees. Up top, a low overcast hangs down with a lit
# bottom edge and opens over the break. World rows: wy 0 is the top of the picture at
# rest; the camera tilts up to wy -112.
# (top wy, [(puff centre x in the 128 repeat, half width, height)], body, rim, belly,
#  rows from the top to the belly)
SKY_BANKS = (
    (-84, [(4, 14, 10), (24, 18, 17), (47, 12, 9), (66, 16, 13), (88, 22, 19), (112, 12, 8)],
     C5, C6, C3, 10),
    (-42, [(10, 20, 16), (33, 12, 9), (52, 17, 14), (78, 13, 10), (96, 19, 17), (118, 10, 6)],
     C4, C5, C2, 11),
    (4, [(0, 16, 12), (20, 13, 16), (41, 20, 15), (66, 12, 8), (84, 18, 18), (108, 14, 10)],
     C3, C4, C1, 11),
    (38, [(12, 18, 12), (36, 12, 8), (55, 20, 15), (82, 14, 10), (104, 17, 13), (124, 9, 5)],
     C2, C3, DEEP, 6),
)
SKY_PERIOD = 128
SKY_BOTTOM = 50                     # the last bank's flat bottom; the horizon band below
BREAK = (215,)                      # the break in the clouds: its centre x (off to the
                                    # right of PIKACHU, not a moon behind its head)
BREAK_GLOW = -98                    # above this row the light behind it is brightest
BREAK_DIP = (215, 56, 22)            # the top bank sinks round the break: x, half width, depth
OVERCAST = -104                     # the hanging overcast's bottom edge, away from the break
OVERCAST_PUFFS = [(6, 12, 7), (26, 14, 11), (48, 10, 6), (66, 15, 12), (88, 11, 8), (108, 16, 10)]


def _dither(x, y):
    return (x + y) % 2 == 0


def _wrap_dx(x, c):
    d = (x - c) % MAP
    return d - MAP if d > MAP // 2 else d


def _puff_tops(x, puffs, period):
    """(height, index) of every puff over column x, in a repeat of `period`."""
    out = []
    for i, (pc, hw, h) in enumerate(puffs):
        for rep in (-period, 0, period):
            dx = (x % period) - (pc + rep)
            if abs(dx) < hw:
                out.append((round(h * math.sqrt(1 - (dx / hw) ** 2)), i + 1))
    return out


def sky_layer():
    """The storm sky over the whole 256x256 map (see SKY_BANKS)."""
    img = [[0] * MAP for _ in range(MAP)]
    for r in range(MAP):
        wy = ((r - VIEW_Y + 128) % MAP) - 128
        for x in range(MAP):
            if wy < 0:                               # the light behind the clouds, in bands
                k = BREAK_GLOW - wy                  # a 3-row dithered step, 3/4, 1/2, 1/4
                if k > 1:
                    c = GLOW
                elif k < -1:
                    c = C6
                else:
                    c = GLOW if (x + 2 * (wy % 2)) % 4 < 2 + k else C6
            else:                                    # the horizon band under the storm
                c = C4 if wy > SKY_BOTTOM else C3
                if wy == SKY_BOTTOM + 1 and _dither(x, wy):
                    c = C3
            img[r][x] = c
    # the overcast hanging down from the top, its bottom edge lit, open over the break
    for x in range(MAP):
        dx = _wrap_dx(x, BREAK[0])
        half = 40.0 if dx < 0 else 52.0                                 # a lopsided hole
        lift = round(30 * math.sqrt(max(0.0, 1 - (dx / half) ** 2)))
        hang = max([h for h, _ in _puff_tops(x, OVERCAST_PUFFS, SKY_PERIOD)], default=0)
        edge = OVERCAST + hang - lift
        for wy in range(-128, edge + 1):
            r = (wy + VIEW_Y) % MAP
            if wy == edge:                           # the underside lit by the break
                c = C5
            elif wy == edge - 1:
                c = C4 if _dither(x, wy) else C3
            else:
                c = C3
            img[r][x] = c
    for n, (top, puffs, body, rim, belly, deep) in enumerate(SKY_BANKS):
        last = n == len(SKY_BANKS) - 1

        def base(x):
            b = top + round(2 * math.sin(2 * math.pi * x / MAP * 2 + n))
            if n == 0:
                dx = abs(_wrap_dx(x, BREAK_DIP[0]))
                b += round(BREAK_DIP[2] * max(0.0, 1 - (dx / BREAK_DIP[1]) ** 2))
            return b
        cols = []
        for x in range(MAP):
            b = base(x)
            cols.append([(b, 0)] + [(b - h, i) for h, i in _puff_tops(x, puffs, SKY_PERIOD)])
        belly_wave = [round(3 * math.sin(2 * math.pi * x / 128 + n) + 2 * math.sin(2 * math.pi * x / 64 + 2 * n))
                      for x in range(MAP)]
        for x in range(MAP):
            layers = cols[x]
            y_top = min(t for t, _ in layers)
            nxt = min(t for t, _ in cols[(x + 1) % MAP])
            prv = min(t for t, _ in cols[x - 1])
            rim_rows = 1 if max(abs(nxt - y_top), abs(prv - y_top)) >= 3 else 2
            for wy in range(y_top, SKY_BOTTOM + 1 if last else 128):
                r = (wy + VIEW_Y) % MAP
                # the puff in front here (the last drawn that reaches this row); its lit top
                front = max(i for t, i in layers if t <= wy)
                t_front = min(t for t, i in layers if i == front)
                # the belly line rolls gently, not a ruled line
                b = layers[0][0] + deep + belly_wave[x]
                if wy - t_front < rim_rows:
                    c = rim
                elif wy > b:
                    c = belly
                elif wy == b:
                    c = belly if _dither(x, wy) else body
                else:
                    c = body
                img[r][x] = c
    return img


def field_layer():
    """Route 1 at dusk in the storm: a dark treeline on the horizon, the grass in
    bands, tall grass in front. Clear above the horizon."""
    img = [[0] * MAP for _ in range(MAP)]
    for x in range(MAP):
        tree = 58 + int(3 * math.sin(2 * math.pi * x / 64) + 2 * math.sin(2 * math.pi * x / 23 + 1))
        for wy in range(tree, VIEW_H + 16):         # past the bottom: the layer scrolls up a little
            r = wy + VIEW_Y
            if wy < 64:
                c = TREES
            elif wy < 70:
                c = G1
            elif wy < 80:
                c = G2
            elif wy < 88:
                c = G3
            else:
                c = G4
            img[r][x] = c
        # grass tufts across the bands
        for band, c, dark in ((70, G2, G1), (80, G3, G2), (88, G4, G3)):
            h = 2 + (x * 7 + band) % 5 // 2
            if (x * 13 + band * 3) % 9 < 4:
                for k in range(h):
                    img[band - k + VIEW_Y][x] = c if k else dark
    return img


def rain_layer():
    """Rain over the whole map: short streaks, falling down and to the left, in a 64
    pixel repeat (few tiles); it scrolls every frame."""
    img = [[0] * MAP for _ in range(MAP)]
    for r in range(MAP):
        for x in range(MAP):
            u, v = x % 64, r % 64
            h = (u * 37 + (v // 6) * 11) % 64
            if h in (0, 17, 41) and (v % 6) < 4:
                img[r][(x - (v % 6) // 2) % MAP] = RAIN if (v % 6) < 2 else RAIN_D
    return img


# ---------------------------------------------------------------- sprites
SPEAROW_PAL = [(0, 0, 0), (255, 222, 74), (255, 150, 110), (222, 148, 115), (123, 65, 65),
               (205, 172, 98), (123, 115, 65), (57, 57, 24), (230, 106, 74), (148, 57, 41),
               (82, 16, 0), (197, 197, 213), (139, 139, 148), (74, 74, 90), (255, 255, 255), (16, 16, 16)]
SP_BEAK, SP_CREST = 1, 2                  # a bright beak and a light crest, so the bird reads
SP_COLORS = {                             # on the dark sky at 1x (art review 4-5 A, change 8)
    'B': dict(base=6, rim=7, rim_dark=15, line=7, mid=7, shade=(2, 2)),      # brown body
    'W': dict(base=8, rim=9, rim_dark=15, line=9, mid=9, shade=(2, 2)),      # red-brown wings
    'F': dict(base=5, rim=6, rim_dark=15, mid=6, shade=(1, 1)),              # beige face
    'K': dict(base=SP_BEAK, rim=15, rim_dark=15),                             # beak
    'C': dict(base=8, rim=9, rim_dark=15),                                    # head crest
}


def spearow_frames():
    """SPEAROW far off, 16x16, flying left. Frames: 0 wings up, 1 wings down, 2 wings
    level (the cycle is 0, 2, 1, 2); 3 and 4: frames 0 and 1 as a white silhouette,
    the moment THUNDERBOLT hits it."""
    out = []
    for wing in ('up', 'down', 'level'):
        f = Figure(16, 16)
        if wing == 'up':
            f.poly('wingFar', [(8, 8), (12, 1), (14, 2), (11, 9)], kind='W')
        elif wing == 'level':
            f.poly('wingFar', [(8, 7.5), (13, 5), (15, 6), (11, 9)], kind='W')
        f.poly('tail', [(11, 8), (15, 6), (15, 10), (11, 10)], kind='B')
        f.poly('crest', [(4, 5.5), (7.5, 3), (8, 4.5), (6.5, 6.5)], kind='C')
        f.ellipse('body', 8.5, 9, 4.2, 2.8, kind='B')
        f.ellipse('head', 4.5, 7.5, 2.6, 2.4, kind='F')
        f.poly('beak', [(2.5, 7), (0, 8), (2.5, 9)], kind='K')
        if wing == 'up':
            f.poly('wing', [(6, 8), (9, 1), (11.5, 2), (10, 9)], kind='W')
        elif wing == 'down':
            f.poly('wing', [(6, 9), (9, 15), (11.5, 14), (10, 8.5)], kind='W')
        else:
            f.poly('wing', [(6, 8.5), (12, 6), (14.5, 7.5), (10, 10)], kind='W')
        img = f.render(SP_COLORS)
        stamp(img, 4, 7, ['K'], {'K': 15})
        stamp(img, 1, 7, ['b'], {'b': SP_BEAK})          # the beak's lit top
        for y in range(16):                               # the crest's tip lit
            for x in range(16):
                if f.owner[y][x] == 'crest' and img[y][x] != 15 and f.owner[y - 1][x] != 'crest':
                    img[y][x] = SP_CREST
        out.append(img)
    for src in out[:2]:
        out.append([[0 if v == 0 else 11 if v == 15 else 14 for v in row] for row in src])
    return out


def _zig(img, path, core, halo, rim_col, pale=None):
    """A jagged stroke: 1 pixel core, a halo round it, the rim outside."""
    pts = set()
    for p, q in zip(path, path[1:]):
        pts |= s2._line(p, q)
    h = len(img)
    w = len(img[0])
    for x, y in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < w and 0 <= y + dy < h and img[y + dy][x + dx] == 0:
                    img[y + dy][x + dx] = halo
    for x, y in path[1:-1]:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            if pale and 0 <= x + dx < w and 0 <= y + dy < h:
                img[y + dy][x + dx] = pale
    for x, y in pts:
        if 0 <= x < w and 0 <= y < h:
            img[y][x] = core
    return img


def bolt_down_frames():
    """The strike from the clouds: 32x64, two frames, a jagged vertical bolt with forks
    (two are stacked to reach from the top of the picture down to PIKACHU)."""
    paths = ([(16, 0), (11, 10), (19, 20), (12, 31), (20, 42), (13, 53), (16, 63)],
             [(15, 0), (21, 11), (13, 22), (20, 32), (12, 43), (19, 54), (16, 63)])
    forks = ([((11, 10), (4, 17)), ((20, 42), (27, 49))], [((21, 11), (28, 18)), ((12, 43), (5, 49))])
    out = []
    for path, fk in zip(paths, forks):
        img = [[0] * 32 for _ in range(64)]
        for p, q in fk:
            _zig(img, [p, q], pika.WHITE, pika.SPARK, pika.SPARK_RIM)
        _zig(img, path, pika.WHITE, pika.SPARK_PALE, pika.SPARK_RIM, pale=pika.SPARK)
        s2._rim(img, pika.SPARK_RIM)
        out.append(img)
    return out


# THUNDERBOLT (art review of 4-5 draft A, change 4): three different drawings of the
# burst, each 128x128 round PIKACHU's middle (the 'zap' pose's sprite sits at
# (32, 28) in it), cut into four 64x64 quarters for the four burst tracks. The strip
# is drawing-major: frame 4 * d + q, q = 0 upper left, 1 upper right, 2 lower left,
# 3 lower right; no flips. Each drawing: 4-5 thick trunks that leave the cheeks,
# different on the left and the right, forking on the way and splitting into twigs
# at the ends; nothing within 4 pixels of PIKACHU's outline (it stays clear and in
# front, in both discharge poses); every lit pixel inside local rows BURST_ROWS, so with the sprite at
# (PIKA_X, PIKA_Y) (+/- 1 for the bob and the shake) the burst stays inside the
# letterbox.
BURST = 128
BURST_ROWS = (8, 99)
BURST_POSES = ('zap', 'zap2')
BURST_AT = (32, 28)                       # where the pose's 64x64 sits in the drawing
CHEEKS = ((52, 54), (75, 54))             # the cheeks, in the drawing
BURST_KEEPOUT = 4
# (cheek 0 left / 1 right, end, segments, zigzag amplitude, forks as (where along,
# turn in degrees, length))
BURSTS = (
    ((0, (8, 12), 7, 4, ((0.55, -38, 14), (0.8, 30, 8))),
     (0, (5, 78), 6, 3, ((0.6, 32, 10),)),
     (1, (118, 24), 6, 4, ((0.5, -40, 12),)),
     (1, (110, 96), 5, 3, ((0.65, -30, 9),))),
    ((0, (22, 8), 6, 4, ((0.6, -35, 13),)),
     (0, (2, 46), 7, 4, ((0.5, 38, 12), (0.82, -30, 8))),
     (0, (32, 98), 4, 3, ()),
     (1, (124, 62), 7, 4, ((0.55, -36, 14),)),
     (1, (104, 9), 5, 3, ((0.7, 34, 8),))),
    ((0, (3, 28), 7, 4, ((0.45, 36, 11), (0.75, -34, 9))),
     (0, (16, 97), 5, 3, ((0.6, -30, 8),)),
     (1, (110, 9), 6, 3, ((0.6, -36, 9),)),
     (1, (125, 40), 6, 4, ((0.5, 40, 12),)),
     (1, (120, 92), 6, 3, ((0.7, -34, 8),))),
)


def _jag(p, q, n, amp, rnd):
    """A zigzag from p to q in n segments, the bends pushed alternately either side."""
    (x0, y0), (x1, y1) = p, q
    length = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    pts = [p]
    for k in range(1, n):
        t = k / n
        off = amp * (1 if k % 2 else -1) * (0.55 + 0.45 * rnd.random())
        pts.append((round(x0 + (x1 - x0) * t + nx * off), round(y0 + (y1 - y0) * t + ny * off)))
    pts.append(q)
    return pts


def _burst_drawing(spec, seed, keepout):
    import random
    rnd = random.Random(seed)
    trunk, branch, twig = set(), set(), set()

    def path_pixels(pts):
        out = set()
        for a, b in zip(pts, pts[1:]):
            out |= s2._line(a, b)
        return out
    for cheek, end, n, amp, forks in spec:
        start = CHEEKS[cheek]
        pts = _jag(start, end, n, amp, rnd)
        seg = len(pts) - 1
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            (trunk if i < seg * 0.7 else branch).update(s2._line(a, b))
        # forks off the trunk, thinner
        for where, turn, flen in forks:
            k = max(1, min(seg - 1, round(where * seg)))
            bx, by = pts[k]
            ang = math.atan2(end[1] - start[1], end[0] - start[0]) + math.radians(turn)
            fe = (round(bx + math.cos(ang) * flen), round(by + math.sin(ang) * flen))
            fp = _jag((bx, by), fe, 3, 2, rnd)
            branch |= path_pixels(fp)
            twig |= path_pixels([fe, (fe[0] + round(math.cos(ang - 0.7) * 4), fe[1] + round(math.sin(ang - 0.7) * 4))])
        # the end splits into small twigs
        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        for turn, tl in ((-0.6, 5), (0.5, 4), (0.05, 3)):
            te = (round(end[0] + math.cos(ang + turn) * tl), round(end[1] + math.sin(ang + turn) * tl))
            twig |= path_pixels([end, te])
    core = set(trunk)
    for x, y in trunk:                      # the trunks' core two pixels thick
        core |= {(x + 1, y), (x, y + 1)}
    core |= branch
    halo1 = {(x + dx, y + dy) for x, y in core for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    halo2 = {(x + dx, y + dy) for x, y in trunk for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
             if abs(dx) + abs(dy) <= 3}
    img = [[0] * BURST for _ in range(BURST)]
    for layer, col in ((halo2, pika.SPARK), (halo1, pika.SPARK_PALE), (twig, pika.SPARK_PALE), (core, pika.WHITE)):
        for x, y in layer:
            if 0 <= x < BURST and BURST_ROWS[0] <= y <= BURST_ROWS[1]:
                img[y][x] = col
    # cut back one pixel further than the keep-out, then rim the cut ends, so every
    # lit pixel, rim included, stays BURST_KEEPOUT clear of PIKACHU
    for x, y in keepout[1]:
        img[y][x] = 0
    s2._rim(img, pika.SPARK_RIM)
    for y in range(BURST):
        for x in range(BURST):
            if (x, y) in keepout[0] or not BURST_ROWS[0] - 1 <= y <= BURST_ROWS[1] + 1:
                img[y][x] = 0
    return img


def burst_keepout(r=BURST_KEEPOUT):
    """Every pixel within r of the discharge poses' outlines, in the drawing."""
    ox, oy = BURST_AT
    solid = set()
    for stage in BURST_POSES:
        pose = pika.jump_frame(stage)
        solid |= {(x + ox, y + oy) for y in range(64) for x in range(64) if pose[y][x]}
    disc = [(dx, dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) <= r]
    return {(x + dx, y + dy) for x, y in solid for dx, dy in disc}


def burst_drawings():
    """The three 128x128 drawings."""
    keep = (burst_keepout(), burst_keepout(BURST_KEEPOUT + 1))
    return [_burst_drawing(spec, 11 + i, keep) for i, spec in enumerate(BURSTS)]


def burst_frames():
    """The burst strip: 4 * drawing + quarter (see BURSTS)."""
    out = []
    for img in burst_drawings():
        for qy in (0, 64):
            for qx in (0, 64):
                out.append([row[qx:qx + 64] for row in img[qy:qy + 64]])
    return out


# ---------------------------------------------------------------- choreography helpers
HIDE, FRONT, HFLIP, VFLIP = 1, 2, 4, 8
N_BIRDS = 12
EV_BLEND, EV_CRY = 0, 1
T_BG, T_OBJ, T_ALL = 0, 1, 2              # blend targets: scene BG, scene sprites, everything
STORM = (20, 24, 48)                      # the gloom the sprites take in the rain
WHITE_RGB = (255, 255, 255)


def ease_io(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def ease_out(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


def hidden():
    return (0, 0, 0, HIDE)


# ---------------------------------------------------------------- scene 4
def scene4_art():
    rv = red
    return {
        # 0-3 the run with the small PIKACHU in his arms, 4 turned (holding it), 5-6 the
        # in-betweens down into the crouch (the crouch itself is 'shield' 0)
        'red': ([rv.side_run(i, carry=True) for i in range(4)] + [rv.back_view(p) for p in ('stand', 'bend1', 'bend2')],
                rv.PAL, 64, 64),
        'shield': ([rv.back_view('shield'), rv.back_view('shield-open')], rv.SHIELD_PAL, 64, 64),
        'bird': (spearow_frames(), SPEAROW_PAL, 16, 16),
    }


S4_TRACKS = ['red', 'shield'] + ['bird%d' % i for i in range(N_BIRDS)]


# ---------------------------------------------------------------- scene 5
def scene5_art():
    sm = pika.small_frames()
    return {
        # 0 crouched without PIKACHU, 1 arms out, 2 crouched with it (as scene 4 ends)
        'shield5': ([red.back_view('shield', pikachu=False), red.back_view('shield-open', pikachu=False),
                     red.back_view('shield')],
                   red.SHIELD_PAL, 64, 64),
        'small': ([sm['crouch'], sm['leap']], pika.PAL, 32, 32),
        # 0 rise, 1 air, 2 the wind-up (t74-76), 3-4 THUNDERBOLT (alternate from t77)
        'pika': ([pika.jump_frame(st) for st in ('rise', 'air', 'charge', 'zap', 'zap2')], pika.PAL, 64, 64),
        'crackleL': (s2.crackle_frames(), pika.PAL, 16, 16),
        'crackleR': (s2.crackle_frames(), pika.PAL, 16, 16),
        'boltA': (bolt_down_frames(), pika.PAL, 32, 64),
        'boltB': (bolt_down_frames(), pika.PAL, 32, 64),
        'burst': (burst_frames(), pika.PAL, 64, 64),
        'bird': (spearow_frames(), SPEAROW_PAL, 16, 16),
    }


S5_TRACKS = ['shield5', 'small', 'pika', 'crackleL', 'crackleR', 'boltA', 'boltB',
             'burst0', 'burst1', 'burst2', 'burst3'] + ['bird%d' % i for i in range(N_BIRDS)]
PIKA_X, PIKA_Y = 88, 54                       # big PIKACHU's corner in the sky (low enough
                                              # for the strike to show coming down)


# ---------------------------------------------------------------- scene 4 (draft B)
FLAP = (0, 2, 1, 2)                     # wings up, level, down, level
RED_WORLD_X = 150                       # where RED stops (front layer coordinates)
CAM_END = 62                            # the camera's pan, so RED ends in the middle
T_HIT = 88                              # scene 5: the flock is struck


def flap(t, i):
    return FLAP[((t + i) // 3) % 4]


def cam4(t):
    """One continuous pan: with RED running in, then on toward him while he turns and
    crouches (no cut: art review 4-5 A, change 1 b)."""
    return round(CAM_END * ease_io(min(1.0, t / 86.0)))


def _sweep(t, i):
    s = t - 30 - (i % 4) * 2
    if s < 0:
        return None
    return (250 - s * 6 + (i % 3) * 14 - (i // 3) * 6,
            40 + 10 * math.sin((s + i * 5) / 6.0) + (i % 4) * 7 - 12)


def _circle(u, i, cx, shake=0):
    """The flock circling RED; u counts from the start of bar 5."""
    a = u * 0.09 + i * (2 * math.pi / N_BIRDS)
    dive = 1.0 - 0.45 * math.sin(math.pi * max(0.0, min(1.0, (u - 30) / 25.0)))
    return (cx + 100 * dive * math.cos(a) - 8 + shake, 66 + 26 * dive * math.sin(a) - 18, math.sin(a) > 0)


def _bird_key(t, i, pos, prev, front, cx, frame=None, extra=0):
    """A bird's key: faces its way of flight; in front of RED only when it is not over
    his head and the small PIKACHU (art review 4-5 A, change 3)."""
    bx, by = pos
    if bx < -16 or bx > 240 or by > 160:
        return hidden()
    if front and abs(bx + 8 - cx) < 24:
        front = False
    flags = (FRONT if front else 0) | extra
    if prev is not None and pos[0] - prev[0] > 0.3:
        flags |= HFLIP                                       # flying right
    return (round(bx), round(by), flap(t, i) if frame is None else frame, flags)


def scene4():
    keys, scroll, layout, events = [], [], [], []
    prev = [None] * N_BIRDS
    for t in range(FRAMES):
        k = {tr: hidden() for tr in S4_TRACKS}
        cam = cam4(t)
        u = t - 77
        shake = {35: 1, 36: -1, 37: 1}.get(u, 0)
        scroll.append((cam // 4 - shake, 0, cam - shake, 0, (t * 2) % 256, (-t * 5) % 256))
        layout.append(1 if t >= 8 else 0)
        wx = -60 + 210 * ease_out(t / 44) if t < 44 else RED_WORLD_X
        x = round(wx - cam) + shake
        # RED: runs in carrying the small PIKACHU, stops, turns, bends, crouches
        if t < 44:
            k['red'] = (x, 60, (t // 3) % 4, 0)
        elif t < 48:
            k['red'] = (x, 60, 1, 0)
        elif t < 56:
            k['red'] = (x, 60, 4, 0)                     # turned, holding it
        elif t < 60:
            k['red'] = (x, 60, 5, 0)                     # knees bending
        elif t < 64:
            k['red'] = (x, 60, 6, 0)
        else:
            frame = 1 if 110 <= t < 140 else 0           # arms out as they dive
            breathe = -1 if frame == 0 and t >= 72 and (t // 8) % 2 else 0
            k['shield'] = (x, 60 + breathe, frame, 0)
        cx = RED_WORLD_X + 32 - cam + shake              # RED's middle on screen
        # the flock sweeps across, turns back and circles him
        for i in range(N_BIRDS):
            sw = _sweep(t, i)
            ci = _circle(u, i, cx, shake)
            if t < 66:
                pos, front = sw, False
            elif t < 86:
                p = ease_io((t - 66) / 20.0)
                pos = (sw[0] + (ci[0] - sw[0]) * p, sw[1] + (ci[1] - sw[1]) * p)
                front = ci[2] and p > 0.5
            else:
                pos, front = (ci[0], ci[1]), ci[2]
            if pos is None:
                continue
            k['bird%d' % i] = _bird_key(t, i, pos, prev[i], front, cx)
            prev[i] = pos
        keys.append(k)
    # the sky darkens over the first beat; the sprites take the storm's gloom
    for t in range(0, 25):
        events.append((t, EV_BLEND, T_BG, round(8 * (1 - t / 24)), (200, 204, 220)))
    events.append((0, EV_BLEND, T_OBJ, 5, STORM))
    # the distant flash on beat 4 of bar 5 (F1129, music direction): the sky lights,
    # the field only a little (art review change 10)
    for i, (c_sky, c_field) in enumerate(((10, 3), (6, 2), (3, 1), (0, 0))):
        events.append((134 + i, EV_BLEND_RANGE, rng(C1, 6), c_sky, GLOW_RGB))
        events.append((134 + i, EV_BLEND_RANGE, rng(GLOW, 2), c_sky, GLOW_RGB))
        events.append((134 + i, EV_BLEND_RANGE, rng(TREES, 5), c_field, GLOW_RGB))
    return keys, scroll, layout, events


EV_BLEND_RANGE = 2


def rng(first, count):
    """A BG palette range as an event target: first colour, count."""
    return first | ((count - 1) << 4)


GLOW_RGB = (230, 236, 255)


# ---------------------------------------------------------------- scene 5 (draft B)
def scene5():
    keys, scroll, layout, events = [], [], [], []
    prev = [None] * N_BIRDS
    ring_pos = [None] * N_BIRDS
    sky0, field0 = CAM_END // 4, CAM_END
    for t in range(FRAMES):
        k = {tr: hidden() for tr in S5_TRACKS}
        tilt = -round(112 * ease_io((t - 19) / 12.0)) if t >= 19 else 0
        shake = ((1 if (t // 2) % 2 else -1) if 77 <= t < 87 else 0)
        rain = ((t + 153) * 2 % 256, (-(t + 153) * 5) % 256)
        scroll.append((sky0 - shake, tilt, field0 - shake, tilt, rain[0], rain[1]))
        layout.append(0 if 37 <= t <= 44 else 1)          # no rain over its face at the strike
        cx = RED_WORLD_X + 32 - CAM_END
        # RED, crouched: PIKACHU has left his arms; he looks up after it (arms out)
        ry = 60 - tilt
        if ry < 128:
            k['shield5'] = (88 + shake, ry, 2 if t < 4 else 0 if t < 9 else 1, 0)
        # the small PIKACHU: crouched on his shoulder, then the spring
        if 4 <= t < 8:                       # it gets up on his shoulder (the cut itself
            k['small'] = (99, 64 + (1 if t >= 6 else 0) - tilt, 0, 0)   # keeps scene 4's picture)
        elif 8 <= t < 19:
            y = 58 - (t - 8) * 7
            if y > 0:
                k['small'] = (92, y, 1, 0)
        # the big PIKACHU: rises once RED is out of the picture, is struck, hangs,
        # winds up (t74-76) and discharges from bar 7 (t77)
        if 30 <= t < 39:
            k['pika'] = (PIKA_X, round(128 - 74 * ease_out((t - 29) / 9.0)), 0, 0)
        elif 39 <= t < 74:
            k['pika'] = (PIKA_X, PIKA_Y + (-1 if (t // 8) % 2 else 0), 1, 0)
        elif 74 <= t < 77:
            k['pika'] = (PIKA_X, PIKA_Y, 2, 0)
        elif t >= 77:
            k['pika'] = (PIKA_X + shake, PIKA_Y, 3 + ((t - 77) // 3) % 2, 0)
        py = k['pika'][1]
        # the strike: two stacked bolts from the top of the picture to its head
        if 37 <= t < 44:
            k['boltA'] = (PIKA_X + 16, py - 96, t % 2, 0)
            k['boltB'] = (PIKA_X + 16, py - 32, (t + 1) % 2, 0)
        # cheeks crackling while it hangs (the discharge poses spark by themselves)
        if 44 <= t < 74 and (t // 2) % 3 != 2:
            k['crackleL'] = (PIKA_X + 4, py + 18, (t // 2) % 2, 0)
            k['crackleR'] = (PIKA_X + 44, py + 18, (t // 2) % 2, HFLIP)
        # THUNDERBOLT: three different drawings in turn, 4 frames each, 4 quarters
        if t >= 77:
            d = ((t - 77) // 4) % 3
            bx0, by0 = PIKA_X - BURST_AT[0] + shake, PIKA_Y - BURST_AT[1]
            for q in range(4):
                k['burst%d' % q] = (bx0 + (q % 2) * 64, by0 + (q // 2) * 64, 4 * d + q, 0)
        for i in range(N_BIRDS):
            side = -1 if i % 2 == 0 else 1
            lane = (i // 2) % 6
            ring = 50 + lane * 5
            key = None
            if t < 34:                       # still circling RED, carried off by the tilt
                bx, by, front = _circle(t + 76, i, cx, shake)
                key = _bird_key(t, i, (bx, by - tilt), prev[i], front, cx) if by - tilt < 128 else hidden()
                pos = (bx, by - tilt)
            elif 60 <= t < T_HIT:            # rushing in from both sides to a ring round it
                s = max(0.0, (t - 60 - lane * 2) / 28.0)
                start = 150 + lane * 10
                pos = (120 + side * (start - (start - ring) * s) - 8,
                       34 + lane * 10 + 4 * math.sin(t / 4.0 + i) - 8)
                ring_pos[i] = pos
                key = _bird_key(t, i, pos, prev[i], True, -999)
            elif T_HIT <= t < T_HIT + 2:     # struck: a white silhouette, 2 frames
                pos = ring_pos[i]
                key = _bird_key(t, i, pos, None, True, -999, frame=3 + (t - T_HIT), extra=HFLIP if side < 0 else 0)
            elif t >= T_HIT + 2:             # upside down, falling away
                s = t - T_HIT - 2
                hx, hy = ring_pos[i]
                pos = (hx - side * 1.2 * s, hy - 2.5 * s + 0.22 * s * s)
                key = _bird_key(t, i, pos, None, True, -999, frame=1 + (t // 4) % 2,
                                extra=VFLIP | (HFLIP if side < 0 else 0))
            else:
                pos = None
            if key is not None:
                k['bird%d' % i] = key
            prev[i] = pos
        keys.append(k)
    events.append((0, EV_BLEND, T_OBJ, 5, STORM))
    # the strike (beat 3, F1186): the whole sky lights once; the cry
    for i, c in enumerate((12, 7, 3, 0)):
        events.append((38 + i, EV_BLEND, T_BG, c, GLOW_RGB))
    events.append((39, EV_CRY, 0, 0, (0, 0, 0)))
    events.append((30, EV_BLEND, T_OBJ, 0, STORM))
    # white-out into scene 6 from beat 3 of bar 7 (t115 = F1263, music direction): +1
    # every 2 frames, white at bar 8
    for t in range(115, FRAMES):
        events.append((t, EV_BLEND, T_ALL, min(16, (t - 115) // 2 + 1), WHITE_RGB))
    return keys, scroll, layout, events


# ---------------------------------------------------------------- rendering (mock-ups)
def blend(c, coeff, target):
    """BlendPalettes on one colour, in the GBA's 5 bits a channel."""
    out = []
    for v, tv in zip(c, target):
        v5, t5 = v >> 3, tv >> 3
        r = v5 + (((t5 - v5) * coeff) >> 4)
        out.append(r * 255 // 31)
    return tuple(out)


def gba(c):
    return tuple((v >> 3) * 255 // 31 for v in c)


class Mock:
    """Draws a scene's frames the way the game does, palettes included."""

    def __init__(self, layers, art, tracks, events):
        self.layers = layers                  # back (sky), front (field), top (rain)
        self.art = art
        self.tracks = tracks
        self.events = events
        self.coeff = {T_BG: (0, (0, 0, 0)), T_OBJ: (0, (0, 0, 0)), T_ALL: (0, (0, 0, 0))}
        self.bg = [(0, (0, 0, 0))] * 16            # BG blends are per colour (ranges)

    def pal(self, pal, target):
        c, col = self.coeff[T_ALL]
        if c:
            return [blend(p, c, col) for p in pal]
        if target == T_BG:
            return [blend(p, c, col) if c else gba(p) for p, (c, col) in zip(pal, self.bg)]
        c, col = self.coeff[target]
        return [blend(p, c, col) if c else gba(p) for p in pal]

    def frame(self, t, k, sc, lay):
        for (et, typ, target, coeff, col) in self.events:
            if et == t and typ == EV_BLEND:
                self.coeff[target] = (coeff, col)
                if target == T_BG:
                    self.bg = [(coeff, col)] * 16
            elif et == t and typ == EV_BLEND_RANGE:
                first, count = target & 15, (target >> 4) + 1
                for i in range(first, first + count):
                    self.bg[i] = (coeff, col)
        screen = Image.new('RGB', (240, 160), (0, 0, 0))
        bgpal = self.pal(BG_PAL, T_BG)
        px = screen.load()
        shown = [(self.layers[0], sc[0], sc[1]), (self.layers[1], sc[2], sc[3])]
        if lay == 1:
            shown.append((self.layers[2], sc[4], sc[5]))
        # back, front: behind the sprites; top (rain): in front of them
        for layer, lx, ly in shown[:2]:
            for y in range(VIEW_H):
                row = layer[(y + VIEW_Y + ly) % MAP]
                for x in range(240):
                    v = row[(x + lx) % MAP]
                    if v:
                        px[x, y + VIEW_Y] = bgpal[v]
        order = sorted(self.tracks, key=lambda tr: -self.sub(tr, k[tr][3]))
        for tr in order:
            x, y, f, fl = k[tr]
            if fl & HIDE:
                continue
            frames, pal, w, h = self.art[self.base(tr)]
            p = self.pal(pal, T_OBJ)
            img = frames[f]
            for yy in range(h):
                for xx in range(w):
                    sx_ = w - 1 - xx if fl & HFLIP else xx
                    sy_ = h - 1 - yy if fl & VFLIP else yy
                    v = img[sy_][sx_]
                    X, Y = (x + xx) % 512, (y + yy) % 256
                    if X >= 256:
                        X -= 512
                    if v and 0 <= X < 240 and 0 <= Y < 160:
                        px[X, Y] = p[v]
        for layer, lx, ly in shown[2:]:
            for y in range(VIEW_H):
                row = layer[(y + VIEW_Y + ly) % MAP]
                for x in range(240):
                    v = row[(x + lx) % MAP]
                    if v:
                        px[x, y + VIEW_Y] = bgpal[v]
        for y in list(range(VIEW_Y)) + list(range(VIEW_Y + VIEW_H, 160)):
            for x in range(240):
                px[x, y] = (0, 0, 0)
        return screen

    @staticmethod
    def base(tr):
        return tr.rstrip('0123456789') if tr.rstrip('0123456789') in ('bird', 'burst') else tr

    def sub(self, tr, flags):
        return track_sub(tr)[1 if flags & FRONT else 0]


def track_sub(tr):
    """(subpriority, subpriority with FRONT) of a track; lower is in front. Each bird
    has its own, so overlapping birds stack the same way here and in the game."""
    if tr.startswith('bird'):
        i = int(tr[4:])
        return 20 + i, i
    return TRACK_INFO[tr.rstrip('0123456789') if tr.startswith('burst') else tr]


# draw order per kind of track: (subpriority, subpriority when FRONT); lower in front
TRACK_INFO = {
    'red': (10, 10), 'shield': (10, 10), 'shield5': (10, 10), 'small': (12, 12), 'pika': (13, 13),
    'crackleL': (14, 14), 'crackleR': (15, 15), 'boltA': (16, 16), 'boltB': (17, 17), 'burst': (18, 18),
}


# ---------------------------------------------------------------- output
def strip(frames, pal):
    return to_image([r for f in frames for r in f], pal)


def tiles_and_maps(layers, bank):
    """One shared tile set; each layer a 32x32 tilemap of the whole 256x256 map."""
    def flip(t, h, v):
        return tuple(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))
    uniq = [tuple([0] * 64)]
    index = {uniq[0]: 0}
    maps = []
    for img in layers:
        entries = []
        for ty in range(32):
            for tx in range(32):
                t = tuple(img[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
                entry = None
                for h, v, bits in ((0, 0, 0), (1, 0, 0x400), (0, 1, 0x800), (1, 1, 0xC00)):
                    f = flip(t, h, v)
                    if f in index:
                        entry = index[f] | bits
                        break
                if entry is None:
                    index[t] = len(uniq)
                    uniq.append(t)
                    entry = index[t]
                entries.append(entry | (bank << 12))
        maps.append(entries)
    sheet = [[0] * 128 for _ in range(((len(uniq) + 15) // 16) * 8)]
    for i, t in enumerate(uniq):
        r, c = divmod(i, 16)
        for k, v in enumerate(t):
            sheet[r * 8 + k // 8][c * 8 + k % 8] = v
    return sheet, maps, len(uniq)


def write_header(scenes, path):
    L = ['// Generated by tools/make_intro_opening_scene45.py. Do not edit: change the',
         '// choreography there and run it again.',
         '// Scenes 4 and 5 of the opening: per frame (code frames; seen one frame later)',
         '// each sprite track {x, y, frame, flags}, the scroll of BG3/BG2/BG1, which',
         '// backgrounds show, and the palette events.', '']
    for name, tracks, (keys, scroll, layout, events) in scenes:
        up = name.upper()
        L.append('#define %s_FRAMES %d' % (up, FRAMES))
        L.append('enum {')
        L += ['    %s_TRACK_%s,' % (up, t.upper()) for t in tracks]
        L += ['    %s_TRACK_COUNT' % up, '};', '']
        L.append('static const struct OpeningKey s%s_Keys[%s_FRAMES][%s_TRACK_COUNT] = {' % (name.capitalize(), up, up))
        for t, k in enumerate(keys):
            L.append('    [%d] = {%s},' % (t, ', '.join('{%d, %d, %d, %d}' % k[tr] for tr in tracks)))
        L += ['};', '', 'static const struct OpeningScroll s%s_Scroll[%s_FRAMES] = {' % (name.capitalize(), up)]
        for t, s in enumerate(scroll):
            L.append('    [%d] = {%d, %d, %d, %d, %d, %d},' % ((t,) + tuple(s)))
        L += ['};', '', 'static const u8 s%s_Layout[%s_FRAMES] = {' % (name.capitalize(), up)]
        for i in range(0, FRAMES, 25):
            L.append('    ' + ', '.join(str(v) for v in layout[i:i + 25]) + ',')
        L += ['};', '', 'static const struct OpeningEvent s%s_Events[] = {' % name.capitalize()]
        for (t, typ, target, coeff, col) in sorted(events, key=lambda e: e[0]):
            L.append('    {%d, %d, %d, %d, RGB(%d, %d, %d)},' % (t, typ, target, coeff, col[0] >> 3, col[1] >> 3, col[2] >> 3))
        L += ['    {0xFFFF},', '};', '']
    open(path, 'w').write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None)
    ap.add_argument('--every', type=int, default=1, help='mock only every Nth frame')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    layers = (sky_layer(), field_layer(), rain_layer())
    tiles, maps, n = tiles_and_maps(layers, BG_PAL_BANK)
    to_image(tiles, BG_PAL).save(OUT + '/bg.png')
    for name, m in zip(('bg_sky', 'bg_field', 'bg_rain'), maps):
        with open(OUT + '/%s.bin' % name, 'wb') as f:
            f.write(struct.pack('<%dH' % len(m), *m))
    art4, art5 = scene4_art(), scene5_art()
    sheets = {}
    for art in (art4, art5):
        for name, (frames, pal, w, h) in art.items():
            sheets[name] = strip(frames, pal)
    for name, im in sheets.items():
        if name not in ('crackleR', 'boltB'):          # the same sheets as crackleL, boltA
            im.save(OUT + '/%s.png' % name)
    s4, s5 = scene4(), scene5()
    write_header((('scene4', S4_TRACKS, s4), ('scene5', S5_TRACKS, s5)), HEADER)
    print('scenes 4-5: %d background tiles' % n)
    if a.preview:
        for name, art, tracks, (keys, scroll, layout, events) in (('mock4', art4, S4_TRACKS, s4),
                                                                   ('mock5', art5, S5_TRACKS, s5)):
            d = os.path.join(a.preview, name)
            os.makedirs(d, exist_ok=True)
            m = Mock(layers, art, tracks, events)
            for t in range(FRAMES):
                im = m.frame(t, keys[t], scroll[t], layout[t])
                if t % a.every == 0:
                    im.save('%s/t%03d.png' % (d, t))


if __name__ == '__main__':
    main()
