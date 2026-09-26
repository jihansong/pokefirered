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


def sky_layer():
    """The storm sky over the whole 256x256 map. World row wy = 0 is the top of the
    picture at rest; negative rows are the sky above, seen when the camera tilts up.
    Big flat cloud masses (few tiles), lighter toward the horizon, and a pale break
    high up where the lightning comes from."""
    img = [[0] * MAP for _ in range(MAP)]
    for r in range(MAP):
        wy = ((r - VIEW_Y + 128) % MAP) - 128
        for x in range(MAP):
            n = _noise(x, r, 0.0) * 0.9 + _noise(x * 2 % MAP, r, 1.7) * 0.25
            base = 2.2 + wy / 40.0                 # lighter toward the horizon
            if wy < -60:                           # the break in the clouds above
                d = math.hypot((x - 130) / 70.0, (wy + 95) / 26.0)
                base += max(0.0, 1.4 - d) * 2.2
            v = base + n * 0.9
            img[r][x] = (C1, C2, C3, C4, C5, C6)[max(0, min(5, int(v)))]
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
SPEAROW_PAL = [(0, 0, 0), (255, 213, 180), (246, 189, 148), (222, 148, 115), (123, 65, 65),
               (205, 172, 98), (123, 115, 65), (57, 57, 24), (230, 106, 74), (148, 57, 41),
               (82, 16, 0), (197, 197, 213), (139, 139, 148), (74, 74, 90), (255, 255, 255), (16, 16, 16)]
SP_COLORS = {
    'B': dict(base=6, rim=7, rim_dark=15, line=7, mid=7, shade=(2, 2)),      # brown body
    'W': dict(base=8, rim=9, rim_dark=15, line=9, mid=9, shade=(2, 2)),      # red-brown wings
    'F': dict(base=5, rim=6, rim_dark=15, mid=6, shade=(1, 1)),              # beige face
    'K': dict(base=5, rim=15, rim_dark=15),                                   # beak
}


def spearow_frames():
    """SPEAROW far off, 16x16, flying left: wings up, wings down."""
    out = []
    for up in (True, False):
        f = Figure(16, 16)
        if up:
            f.poly('wingFar', [(8, 8), (12, 1), (14, 2), (11, 9)], kind='W')
        f.poly('tail', [(11, 8), (15, 6), (15, 10), (11, 10)], kind='B')
        f.ellipse('body', 8.5, 9, 4.2, 2.8, kind='B')
        f.ellipse('head', 4.5, 7.5, 2.6, 2.4, kind='F')
        f.poly('beak', [(2.5, 7), (0, 8), (2.5, 9)], kind='K')
        if up:
            f.poly('wing', [(6, 8), (9, 1), (11.5, 2), (10, 9)], kind='W')
        else:
            f.poly('wing', [(6, 9), (9, 15), (11.5, 14), (10, 8.5)], kind='W')
        img = f.render(SP_COLORS)
        stamp(img, 4, 7, ['K'], {'K': 15})
        out.append(img)
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


def burst_frame():
    """One quarter of the THUNDERBOLT burst, 64x64: jagged rays from the lower right
    corner (PIKACHU's middle) out to the upper left. The other quarters are this one
    mirrored; swapping the mirrors changes the rays without any blinking."""
    img = [[0] * 64 for _ in range(64)]
    for ang, length, wiggle in ((198, 58, 5), (222, 62, 6), (246, 54, 5), (262, 40, 4), (184, 36, 4), (234, 30, 3)):
        a = math.radians(ang)
        pts = []
        for k in range(8):
            d = 10 + (length - 10) * k / 7
            off = wiggle * (1 if k % 2 else -1)
            x = 63 + d * math.cos(a) - off * math.sin(a)
            y = 63 + d * math.sin(a) + off * math.cos(a)
            pts.append((round(x), round(y)))
        _zig(img, pts, pika.WHITE, pika.SPARK_PALE, pika.SPARK_RIM, pale=pika.SPARK)
    # the glow round the middle
    for y in range(64):
        for x in range(64):
            d = math.hypot(63 - x, 63 - y)
            if d < 9 and img[y][x] == 0:
                img[y][x] = pika.SPARK_PALE if d < 6 else pika.SPARK
    s2._rim(img, pika.SPARK_RIM)
    return img


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
        'red': ([rv.side_run(i) for i in range(4)] + [rv.back_view('stand')], rv.PAL, 64, 64),
        'shield': ([rv.back_view('shield'), rv.back_view('shield-open')], rv.SHIELD_PAL, 64, 64),
        'bird': (spearow_frames(), SPEAROW_PAL, 16, 16),
    }


S4_TRACKS = ['red', 'shield'] + ['bird%d' % i for i in range(N_BIRDS)]


def scene4():
    keys, scroll, layout, events = [], [], [], []
    for t in range(FRAMES):
        k = {tr: hidden() for tr in S4_TRACKS}
        if t < 77:
            cam = round(44 * ease_io(t / 76))
            sx = 0
            scroll.append((cam // 4, 0, cam, 0, (t * 2) % 256, (-t * 5) % 256))
            layout.append(1 if t >= 8 else 0)
            wx = -60 + 210 * ease_out(t / 44)
            x = round(wx - cam)
            if t < 44:
                k['red'] = (x, 60, (t // 3) % 4, 0)
            elif t < 48:
                k['red'] = (x, 60, 1, 0)                   # the stop
            else:
                k['red'] = (x, 60, 4, 0)                   # turned: back view
            for i in range(N_BIRDS):                      # the flock sweeps across
                s = t - 30 - (i % 4) * 2
                if s < 0:
                    continue
                bx = 250 - s * 6 + (i % 3) * 14 - (i // 3) * 6
                by = 40 + 10 * math.sin((s + i * 5) / 6.0) + (i % 4) * 7 - 12
                if bx < -16:
                    continue
                k['bird%d' % i] = (round(bx), round(by), ((t + i) // 3) % 2, 0)
        else:
            u = t - 77
            shake = {35: 1, 36: -1, 37: 1}.get(u, 0)
            scroll.append((20 - shake, 0, 70 - shake, 4, (t * 2) % 256, (-t * 5) % 256))
            layout.append(1)
            frame = 1 if 33 <= u < 63 else 0
            breathe = -1 if frame == 0 and (u // 8) % 2 else 0
            k['shield'] = (88 + shake, 60 + breathe, frame, 0)
            for i in range(N_BIRDS):                      # circling, diving at u 33
                a = u * 0.09 + i * (2 * math.pi / N_BIRDS)
                dive = 1.0 - 0.45 * math.sin(math.pi * max(0.0, min(1.0, (u - 30) / 25.0)))
                rx, ry = 100 * dive, 26 * dive
                bx = 120 + rx * math.cos(a) - 8 + shake
                by = 66 + ry * math.sin(a) - 8 - 10
                front = FRONT if math.sin(a) > 0 else 0
                flip = HFLIP if math.sin(a) < 0 else 0     # flying right on the far side
                k['bird%d' % i] = (round(bx), round(by), ((t + i) // 3) % 2, front | flip)
        keys.append(k)
    # the sky darkens over the first beat; the sprites take the storm's gloom
    for t in range(0, 25):
        events.append((t, EV_BLEND, T_BG, round(8 * (1 - t / 24)), (200, 204, 220)))
    events.append((0, EV_BLEND, T_OBJ, 5, STORM))
    # one distant flash (4b u 53 = t 130), BG only
    for i, c in enumerate((10, 6, 3, 0)):
        events.append((130 + i, EV_BLEND, T_BG, c, GLOW_RGB))
    return keys, scroll, layout, events


GLOW_RGB = (230, 236, 255)


# ---------------------------------------------------------------- scene 5
def scene5_art():
    sm = pika.small_frames()
    return {
        'shield5': ([red.back_view('shield', pikachu=False), red.back_view('shield-open', pikachu=False)],
                   red.SHIELD_PAL, 64, 64),
        'small': ([sm['crouch'], sm['leap']], pika.PAL, 32, 32),
        'pika': ([pika.jump_frame('rise'), pika.jump_frame('air')], pika.PAL, 64, 64),
        'crackleL': (s2.crackle_frames(), pika.PAL, 16, 16),
        'crackleR': (s2.crackle_frames(), pika.PAL, 16, 16),
        'boltA': (bolt_down_frames(), pika.PAL, 32, 64),
        'boltB': (bolt_down_frames(), pika.PAL, 32, 64),
        'burst': ([burst_frame()], pika.PAL, 64, 64),
        'bird': (spearow_frames(), SPEAROW_PAL, 16, 16),
    }


S5_TRACKS = ['shield5', 'small', 'pika', 'crackleL', 'crackleR', 'boltA', 'boltB',
             'burst0', 'burst1', 'burst2', 'burst3'] + ['bird%d' % i for i in range(N_BIRDS)]
PIKA_X, PIKA_Y = 88, 54                       # big PIKACHU's corner in the sky (low enough
                                              # for the strike to show coming down)


def scene5():
    keys, scroll, layout, events = [], [], [], []
    for t in range(FRAMES):
        k = {tr: hidden() for tr in S5_TRACKS}
        tilt = -round(112 * ease_io((t - 19) / 12.0)) if t >= 19 else 0
        shake = ((1 if (t // 2) % 2 else -1) if 77 <= t < 87 else 0)
        rain = ((t + 153) * 2 % 256, (-(t + 153) * 5) % 256)
        scroll.append((20 - shake, tilt, 70 - shake, 4 + tilt, rain[0], rain[1]))
        layout.append(1)
        # RED, crouched: PIKACHU has left his arms; he looks up after it (arms out)
        ry = 60 - tilt
        if ry < 128:
            k['shield5'] = (88 + shake, ry, 0 if t < 9 else 1, 0)
        # the small PIKACHU: crouched on his shoulder, then the spring
        if t < 8:
            k['small'] = (94, 64 + (1 if t >= 4 else 0) - tilt, 0, 0)
        elif t < 19:
            y = 58 - (t - 8) * 7
            if y > 0:
                k['small'] = (92, y, 1, 0)
        # the big PIKACHU rises into the sky once RED is out of the picture
        if 30 <= t < 39:
            y = round(128 - 74 * ease_out((t - 29) / 9.0))
            k['pika'] = (PIKA_X, y, 0, 0)
        elif t >= 39:
            bob = -1 if (t // 8) % 2 else 0
            k['pika'] = (PIKA_X + shake, PIKA_Y + bob, 1, 0)
        py = k['pika'][1]
        # the strike: two stacked bolts from the top of the picture to its head
        if 37 <= t < 44:
            k['boltA'] = (PIKA_X + 16, py - 96, t % 2, 0)
            k['boltB'] = (PIKA_X + 16, py - 32, (t + 1) % 2, 0)
        # cheeks crackling
        if t >= 44 and t < 77 or t >= 77:
            if (t // 2) % 3 != 2:
                k['crackleL'] = (PIKA_X + 4 + shake, py + 18, (t // 2) % 2, 0)
                k['crackleR'] = (PIKA_X + 44 + shake, py + 18, (t // 2) % 2, HFLIP)
        # THUNDERBOLT: four mirrored quarters round its middle, the mirrors swapped
        if t >= 77:
            cx, cy = PIKA_X + 32 + shake, py + 36
            swap = (t // 4) % 2
            quads = [(cx - 64, cy - 64, 0), (cx, cy - 64, HFLIP), (cx - 64, cy, VFLIP), (cx, cy, HFLIP | VFLIP)]
            for q, (x, y, fl) in enumerate(quads):
                if swap:
                    fl ^= HFLIP | VFLIP
                    x, y = quads[3 - q][0], quads[3 - q][1]
                    fl = quads[q][2] ^ (HFLIP | VFLIP)
                    x, y = (cx - 64 if fl & HFLIP == 0 else cx), (cy - 64 if fl & VFLIP == 0 else cy)
                k['burst%d' % q] = (x, y, 0, fl)
        # the flock keeps circling RED (as at the end of scene 4) until the tilt leaves it
        if t < 34:
            u = t + 76
            for i in range(N_BIRDS):
                a = u * 0.09 + i * (2 * math.pi / N_BIRDS)
                bx = 120 + 100 * math.cos(a) - 8 + shake
                by = 66 + 26 * math.sin(a) - 18 - tilt
                if by < 128:
                    front = FRONT if math.sin(a) > 0 else 0
                    flip = HFLIP if math.sin(a) < 0 else 0
                    k['bird%d' % i] = (round(bx), round(by), ((u + 77 + i) // 3) % 2, front | flip)
        # the flock: rushes in from both sides, is caught, scatters tumbling
        for i in range(N_BIRDS):
            side = -1 if i % 2 == 0 else 1
            lane = (i // 2) % 6
            ring = 50 + lane * 5                  # they close in, but not onto PIKACHU
            if 60 <= t < 88:
                s = max(0.0, (t - 60 - lane * 2) / 28.0)
                start = 150 + lane * 10
                bx = 120 + side * (start - (start - ring) * s) - 8
                by = 34 + lane * 10 + 4 * math.sin(t / 4.0 + i) - 8
                if -16 < bx < 240:
                    k['bird%d' % i] = (round(bx), round(by), (t + i) // 3 % 2, FRONT | (HFLIP if side < 0 else 0))
            elif 88 <= t < 130:
                s = t - 88
                ang = math.radians(-150 + i * 27)
                bx = 120 + math.cos(ang) * (ring + s * 5) - 8
                by = 80 + math.sin(ang) * (26 + s * 3) - 8 + s * s * 0.03
                if -16 < bx < 240 and -16 < by < 160:
                    k['bird%d' % i] = (round(bx), round(by), (t + i) % 2,
                                       FRONT | VFLIP | (HFLIP if math.cos(ang) > 0 else 0))
        keys.append(k)
    events.append((0, EV_BLEND, T_OBJ, 5, STORM))
    # the strike: the sky lights once; the cry
    for i, c in enumerate((12, 7, 3, 0)):
        events.append((38 + i, EV_BLEND, T_BG, c, GLOW_RGB))
    events.append((39, EV_CRY, 0, 0, (0, 0, 0)))
    # the sprites lose the gloom once PIKACHU is up in the light
    events.append((30, EV_BLEND, T_OBJ, 0, STORM))
    # white-out into scene 6: +1 every 2 frames from t118
    for t in range(118, FRAMES):
        events.append((t, EV_BLEND, T_ALL, min(16, (t - 118) // 2 + 1), WHITE_RGB))
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

    def pal(self, pal, target):
        c, col = self.coeff[T_ALL]
        if c:
            return [blend(p, c, col) for p in pal]
        c, col = self.coeff[target]
        return [blend(p, c, col) if c else gba(p) for p in pal]

    def frame(self, t, k, sc, lay):
        for (et, typ, target, coeff, col) in self.events:
            if et == t and typ == EV_BLEND:
                self.coeff[target] = (coeff, col)
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
