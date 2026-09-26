#!/usr/bin/env python3
"""Draw and time scene 6 of the new opening: the rainbow and the golden bird (draft).

docs/anim/opening-storyboard.md, scene 6: code frames F1301-1377 (77 frames, bar 8 of
MUS_INTRO_FIGHT; beats at t0, 19, 38, 57; scene 7 at bar 9). Captures one frame later.

  t0-15   out of scene 5's white (the whole picture un-blends 1/16 a frame), the
          storm gone: a washed sky, the rainbow, RED and PIKACHU small on a hill,
          from behind, looking at it (FR/LG's own overworld sprites: the size rule
          puts PIKACHU at RED's scale, and the storyboard asks for field-sprite size)
  t0-18   a breath; PIKACHU's ears twitch (its walk frames), clouds drift
  t19-50  beat 2: the camera tilts up 40 px (ease): the hill leaves the bottom of the
          picture, the whole arc of the rainbow and the high clouds come in
  t34-76  far off, HO-OH's golden silhouette crosses right to left, high and small
          (3 wing frames), a sparkle trail behind it; on beat 4 (t57) it passes the
          top of the rainbow. Far away on purpose: not the anime's first-episode shot
          (a figure looking up at a close bird), storyboard 4.

Layers: BG3 sky, rainbow and far clouds; BG2 the hill; BG1 near clouds in front
(drifting). One BG palette: sky 3, clouds 3, rainbow 5, hill 4.

Writes graphics/intro/opening/scene6/* and src/data/intro_opening_scene6.h; with
--preview DIR the mock-ups DIR/mock6/tNN.png. Uses the scene 4-5 tool's mock-up
renderer (same player, same rules).
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_opening_art import Figure, stamp, to_image  # noqa: E402
import make_intro_opening_scene45 as s45  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = ROOT + '/graphics/intro/opening/scene6'
HEADER = ROOT + '/src/data/intro_opening_scene6.h'
FRAMES = 77
MAP, VIEW_Y, VIEW_H = 256, 32, 96
BG_PAL_BANK = 4

BG_PAL = [(0, 0, 0), (98, 156, 222), (140, 188, 238), (190, 222, 246),       # sky, high to low
          (255, 255, 255), (222, 230, 242), (180, 194, 214),                 # clouds
          (246, 132, 132), (250, 196, 120), (246, 238, 140), (150, 222, 150), (140, 170, 238),  # rainbow
          (164, 214, 106), (118, 180, 82), (78, 138, 64), (40, 82, 44)]      # the hill
SKY1, SKY2, SKY3, CL_W, CL_L, CL_S = 1, 2, 3, 4, 5, 6
BOW = (7, 8, 9, 10, 11)
H_L, H_M, H_D, H_O = 12, 13, 14, 15
TILT = 40


def wrap_row(r):
    """World row of a map row: 0 is the top of the picture before the tilt; rows up to
    -128 are the sky above."""
    return ((r - VIEW_Y + 128) % MAP) - 128


def cloud_puffs(x, y0, puffs, period=128):
    """Height of the scalloped cloud top over column x."""
    best = None
    for pc, hw, h in puffs:
        for rep in (-period, 0, period):
            dx = (x % period) - (pc + rep)
            if abs(dx) < hw:
                top = y0 - round(h * math.sqrt(1 - (dx / hw) ** 2))
                best = top if best is None else min(best, top)
    return best


def sky_layer():
    img = [[0] * MAP for _ in range(MAP)]
    for r in range(MAP):
        wy = wrap_row(r)
        for x in range(MAP):
            if wy < -30:
                c = SKY1
            elif wy < 30:
                c = SKY2 if not (wy == -30 and x % 2) else SKY1
            else:
                c = SKY3 if not (wy == 30 and x % 2) else SKY2
            img[r][x] = c
    # the rainbow: five soft bands round a centre below the hill
    cx, cy, r0 = 120, 150, 136
    for r in range(MAP):
        wy = wrap_row(r)
        for x in range(MAP):
            d = math.hypot(x - cx, wy - cy)
            k = int((r0 - d) / 3)
            if 0 <= k < 5 and wy < 70:
                img[r][x] = BOW[k]
    # far clouds low over the horizon, flat bottoms
    far = [(10, 18, 8), (40, 14, 6), (70, 22, 10), (104, 16, 7)]
    for x in range(MAP):
        top = cloud_puffs(x, 58, far)
        if top is None:
            continue
        for wy in range(top, 62):
            img[(wy + VIEW_Y) % MAP][x] = CL_W if wy - top < 2 else CL_L if wy < 60 else CL_S
    return img


def near_cloud_layer():
    """Near clouds high in the sky (in front of the far bird's path edges), seen
    after the tilt; they drift."""
    img = [[0] * MAP for _ in range(MAP)]
    puffs = [(8, 22, 8), (34, 12, 5), (214, 16, 7), (236, 22, 9)]
    for x in range(MAP):
        top = cloud_puffs(x, -14, puffs, period=256)
        if top is None:
            continue
        for wy in range(top, -9):
            c = CL_W if wy - top < 2 else CL_L if wy < -11 else CL_S
            img[(wy + VIEW_Y) % MAP][x] = c
    return img


def hill_layer():
    img = [[0] * MAP for _ in range(MAP)]
    for x in range(MAP):
        top = 74 + round(10 * ((x - 120) / 130.0) ** 2 * 1.4 + 1.5 * math.sin(x / 9.0))
        for wy in range(max(0, top), VIEW_H + TILT + 8):
            if wy >= 128:
                break
            d = wy - top
            c = H_O if d == 0 else H_L if d < 3 else H_M if d < 12 else H_D
            if d >= 3 and (x * 5 + wy * 3) % 17 == 0:
                c = H_L                                    # flowers of light in the grass
            img[(wy + VIEW_Y) % MAP][x] = c
    return img


# ---------------------------------------------------------------- sprites
HOOH_PAL = [(0, 0, 0), (255, 246, 200), (255, 222, 106), (238, 180, 57), (197, 131, 41),
            (148, 90, 32), (98, 57, 24), (255, 255, 255)] + [(0, 0, 0)] * 8
HO_COLORS = {'G': dict(base=4, rim=2, rim_dark=6, line=3, mid=5, shade=(1, 2))}


def hooh_frames():
    """HO-OH far off, flying left, as a golden silhouette (backlit: dark gold body,
    a bright rim on top): 32x32, wings up, level, down. Not detailed on purpose."""
    out = []
    for wing in ('up', 'level', 'down'):
        f = Figure(32, 32)
        f.poly('tail', [(20, 16), (31, 12), (30, 16), (31, 21), (21, 19)], kind='G')
        f.ellipse('body', 16, 17, 6, 3, kind='G', rot=-0.1)
        f.ellipse('head', 9, 14, 2.6, 2.4, kind='G')
        f.poly('crest', [(9, 12), (13, 7), (12, 12)], kind='G')
        f.poly('beak', [(7, 14), (4, 15), (7, 15.5)], kind='G')
        tip = {'up': (22, 2), 'level': (27, 9), 'down': (22, 29)}[wing]
        far = {'up': (17, 3), 'level': (20, 10), 'down': (18, 27)}[wing]
        f.poly('wingFar', [(14, 16), far, (far[0] + 3, far[1] + 1), (18, 17)], kind='G')
        f.poly('wing', [(13, 17), tip, (tip[0] + 3, tip[1] + 2), (19, 18)], kind='G')
        out.append(f.render(HO_COLORS))
    return out


def sparkle_frames():
    """8x8 twinkles: a small cross, a bigger star."""
    a = ['........', '........', '...1....', '..121...', '...1....', '........', '........', '........']
    b = ['...1....', '...2....', '.1.2.1..', '..222...', '12272 1.', '..222...', '.1.2.1..', '...2....']
    out = []
    for rows in (a, b):
        img = [[0] * 8 for _ in range(8)]
        stamp(img, 0, 0, rows, {'1': 2, '2': 1, '7': 7}, clip=False)
        out.append(img)
    return out


def overworld_frame(path, w, h, i):
    im = Image.open(ROOT + '/' + path)
    frame = im.crop((i * w, 0, i * w + w, h))
    return [[frame.getpixel((x, y)) for x in range(w)] for y in range(h)], im.getpalette()[:48]


def art():
    red_back, red_pal = overworld_frame('graphics/object_events/pics/people/red_normal.png', 16, 32, 1)
    pk = [overworld_frame('graphics/object_events/pics/pokemon/pikachu.png', 16, 16, i) for i in (1, 4)]
    pk_pal = pk[0][1]
    tup = lambda p: [tuple(p[i:i + 3]) for i in range(0, 48, 3)]
    out = {'red': ([red_back], tup(red_pal), 16, 32),
           'pika': ([pk[0][0], pk[1][0]], tup(pk_pal), 16, 16),
           'hooh': (hooh_frames(), HOOH_PAL, 32, 32)}
    for i in range(N_SPARKS):
        out['spark%d' % i] = (sparkle_frames(), HOOH_PAL, 8, 8)
    return out


N_SPARKS = 6
TRACKS = ['red', 'pika', 'hooh'] + ['spark%d' % i for i in range(N_SPARKS)]
s45.TRACK_INFO.update({'red': (10, 10), 'pika': (11, 11), 'hooh': (12, 12)})
s45.TRACK_INFO.update({'spark%d' % i: (13 + i, 13 + i) for i in range(N_SPARKS)})


def hooh_path(t):
    """Corner of HO-OH's sprite in world coordinates (right to left, a shallow arc)."""
    p = (t - 34) / 42.0
    x = 214 - 260 * p
    y = -40 + 8 * math.sin(math.pi * p)
    return x, y


def scene6():
    keys, scroll, layout, events = [], [], [], []
    hide = (0, 0, 0, s45.HIDE)
    for t in range(FRAMES):
        k = {tr: hide for tr in TRACKS}
        v = -round(TILT * s45.ease_io((t - 19) / 31.0)) if t >= 19 else 0
        drift = t // 2
        scroll.append((0, v, 0, v, drift, v))
        layout.append(1)
        # RED and PIKACHU on the hill, from behind (they drop out with the tilt)
        ry = 76 + VIEW_Y - 30 - v
        if ry < 160:
            k['red'] = (112, ry, 0, 0)
            k['pika'] = (128, ry + 16, 1 if 8 <= t < 11 else 0, 0)
        # HO-OH far off and its sparkle trail
        if t >= 34:
            hx, hy = hooh_path(t)
            k['hooh'] = (round(hx), round(hy + VIEW_Y - v), (t // 4) % 3, 0)
            for i in range(N_SPARKS):
                born = t - (i * 4 + (t % 4))
                if born >= 34 and t - born < 16:
                    sx, sy = hooh_path(born)
                    k['spark%d' % i] = (round(sx + 24), round(sy + 16 + VIEW_Y - v + (t - born) // 3),
                                        0 if (t - born) % 6 < 3 else 1, 0)
        keys.append(k)
    # out of the white of scene 5's end
    for t in range(0, 17):
        events.append((t, s45.EV_BLEND, s45.T_ALL, 16 - t, s45.WHITE_RGB))
    return keys, scroll, layout, events


def write_header(tracks, data, path):
    keys, scroll, layout, events = data
    L = ['// Generated by tools/make_intro_opening_scene6.py. Do not edit.', '',
         '#define SCENE6_FRAMES %d' % FRAMES, 'enum {']
    L += ['    SCENE6_TRACK_%s,' % t.upper() for t in tracks]
    L += ['    SCENE6_TRACK_COUNT', '};', '',
          'static const struct OpeningKey sScene6_Keys[SCENE6_FRAMES][SCENE6_TRACK_COUNT] = {']
    for t, k in enumerate(keys):
        L.append('    [%d] = {%s},' % (t, ', '.join('{%d, %d, %d, %d}' % k[tr] for tr in tracks)))
    L += ['};', '', 'static const struct OpeningScroll sScene6_Scroll[SCENE6_FRAMES] = {']
    for t, s in enumerate(scroll):
        L.append('    [%d] = {%d, %d, %d, %d, %d, %d},' % ((t,) + tuple(s)))
    L += ['};', '', 'static const u8 sScene6_Layout[SCENE6_FRAMES] = {']
    for i in range(0, FRAMES, 25):
        L.append('    ' + ', '.join(str(v) for v in layout[i:i + 25]) + ',')
    L += ['};', '', 'static const struct OpeningEvent sScene6_Events[] = {']
    for (t, typ, target, coeff, col) in sorted(events, key=lambda e: e[0]):
        L.append('    {%d, %d, %d, %d, RGB(%d, %d, %d)},' % (t, typ, target, coeff, col[0] >> 3, col[1] >> 3, col[2] >> 3))
    L += ['    {0xFFFF},', '};', '']
    open(path, 'w').write('\n'.join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    layers = (sky_layer(), hill_layer(), near_cloud_layer())
    tiles, maps, n = s45.tiles_and_maps(layers, BG_PAL_BANK)
    to_image(tiles, BG_PAL).save(OUT + '/bg.png')
    for name, m in zip(('bg_sky', 'bg_hill', 'bg_clouds'), maps):
        with open(OUT + '/%s.bin' % name, 'wb') as f:
            f.write(struct.pack('<%dH' % len(m), *m))
    sheets = art()
    for name in ('red', 'pika', 'hooh', 'spark0'):
        frames, pal, w, h = sheets[name]
        s45.strip(frames, pal).save(OUT + '/%s.png' % ('spark' if name == 'spark0' else name))
    data = scene6()
    write_header(TRACKS, data, HEADER)
    print('scene 6: %d background tiles' % n)
    if a.preview:
        d = os.path.join(a.preview, 'mock6')
        os.makedirs(d, exist_ok=True)
        s45.BG_PAL = BG_PAL                       # the renderer draws with the module's BG palette
        m = s45.Mock(layers, sheets, TRACKS, data[3])
        keys, scroll, layout, _ = data
        for t in range(FRAMES):
            m.frame(t, keys[t], scroll[t], layout[t]).save('%s/t%02d.png' % (d, t))


if __name__ == '__main__':
    main()
