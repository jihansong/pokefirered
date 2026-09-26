#!/usr/bin/env python3
"""Mock-ups of opening plan B: every picture element is an official graphic already in this
repository (FR/LG backgrounds, tilesets, battle/trainer/field sprites, battle animation and
weather graphics). The code only places, scrolls, scales (affine), tints (palette blends)
and times them, which is what the ROM will do. The only change to any picture is a palette
recolour (HO-OH's gold silhouette), allowed by the direction change of 2026-09-26.

    python3 tools/make_intro_opening_official_mock.py [--out docs/anim/drafts/official-B]

Writes cN_x.png key frames (240x160, 1x and 3x) and compare.png / compare_x3.png, each cut
next to the original FR/LG opening capture it is measured against.
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from official_gfx import ROOT, read_pal, render_layout, render_map, sprite  # noqa: E402

W, H, VIEW_Y, VIEW_H = 240, 160, 32, 96        # the FR/LG opening's letterbox, kept
ORIG = ROOT + '/docs/anim/shots/intro-original/'
SPARK = 'graphics/battle_anims/sprites/spark.gbapal'
PAL_OF = {'lightning': 'graphics/battle_anims/sprites/lightning_2.gbapal',
          'shock': 'graphics/battle_anims/sprites/shock_4.gbapal',
          'electricity': 'graphics/battle_anims/sprites/electric_orbs.gbapal'}  # as src/data/battle_anim.h pairs them


def blend(img, color, coeff):
    """What BLDY / BlendPalette does: move every colour coeff/16 toward color."""
    if coeff <= 0:
        return img
    over = Image.new('RGBA', img.size, color + (255,))
    base = img.convert('RGBA')
    out = Image.blend(base, over, coeff / 16.0)
    out.putalpha(base.getchannel('A'))
    return out


def affine(spr, scale, angle=0):
    """The OBJ affine unit: nearest-neighbour scale and rotation."""
    w, h = spr.size
    out = spr.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.NEAREST)
    if angle:
        out = out.rotate(angle, resample=Image.NEAREST, expand=True)
    return out


def frame(view):
    """Put a 240x96 view into the letterboxed 240x160 screen."""
    scr = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    scr.paste(view.crop((0, 0, W, VIEW_H)), (0, VIEW_Y))
    return scr


def put(canvas, spr, x, y):
    canvas.alpha_composite(spr, (int(x), int(y)))


# ---------------------------------------------------------------- the official pieces
def red_field(i):
    return sprite('graphics/object_events/pics/people/red_normal.png', i, 16, 32)


def pika_field(i):
    return sprite('graphics/object_events/pics/pokemon/pikachu.png', i, 16, 16)


def red_back(i):
    return sprite('graphics/trainers/back_pics/red_back_pic.png', i, 64, 64)


def mon(name, side='front', pal=None):
    return sprite('graphics/pokemon/%s/%s.png' % (name, side), 0, 64, 64,
                  pal or 'graphics/pokemon/%s/normal.pal' % name)


def silhouette_gold(spr):
    """HO-OH's palette recoloured to one gold ramp (the shading of the original kept)."""
    out = spr.copy()
    px = out.load()
    for y in range(out.size[1]):
        for x in range(out.size[0]):
            r, g, b, a = px[x, y]
            if a:
                lum = (r * 3 + g * 6 + b) / 2550.0
                k = min(3, int(lum * 4))
                px[x, y] = [(123, 74, 16), (197, 131, 41), (246, 197, 74), (255, 238, 156)][k] + (255,)
    return out


def ball(i):
    return sprite('graphics/interface/ball/poke.png', i, 16, 16)


def anim(name, i, w, h, pal):
    return sprite('graphics/battle_anims/sprites/%s.png' % name, i, w, h, PAL_OF.get(name, pal))


def rain(i):
    return sprite('graphics/weather/rain.png', i, 16, 32, 'graphics/weather/default.gbapal')


def cloud():
    return sprite('graphics/weather/cloud.png', 0, 64, 64, 'graphics/weather/cloud.gbapal')


_cache = {}


def layer(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def pallet_map():
    """Route 1 above Pallet Town, as the game joins them (same width, 24 blocks)."""
    def build():
        ts = ('data/tilesets/primary/general', 'data/tilesets/secondary/pallet_town')
        town = render_layout('data/layouts/PalletTown', *ts, 24)
        route = render_layout('data/layouts/Route1', *ts, 24)
        img = Image.new('RGBA', (town.size[0], town.size[1] + route.size[1]))
        img.paste(route, (0, 0))
        img.paste(town, (0, route.size[1]))
        return img
    return layer('pallet', build)


def bg(path, pal=None, width=32):
    def build():
        base = ROOT + '/' + path
        p = pal or (base + '.gbapal' if os.path.exists(base + '.gbapal') else base + '.png')
        return render_map(path + '.png', path + '.bin', read_pal(p), width=width)
    return layer(path, build)


def tiled(img, sx, sy, w=W, h=VIEW_H):
    """A BG layer seen through the screen at scroll (sx, sy), wrapping like the hardware."""
    out = Image.new('RGBA', (w, h))
    iw, ih = img.size
    for oy in range(-(sy % ih), h, ih):
        for ox in range(-(sx % iw), w, iw):
            out.alpha_composite(img, (ox, oy)) if (ox >= 0 and oy >= 0) else out.paste(img, (ox, oy), img)
    return out


# ---------------------------------------------------------------- the cuts
ROUTE_H = 40 * 16


def cut1(t):
    """Pallet Town at dawn: the camera follows RED north out of town, PIKACHU trailing."""
    m = pallet_map()
    # RED leaves his house (door at block (5,7) of Pallet Town) and walks to the gap at the top
    path = [(5 * 16, ROUTE_H + 8 * 16), (5 * 16, ROUTE_H + 10 * 16 + 8), (11 * 16, ROUTE_H + 10 * 16 + 8),
            (11 * 16, ROUTE_H - 2 * 16)]
    seg = [math.dist(path[i], path[i + 1]) for i in range(3)]
    d = min(t * 2.0, sum(seg))
    for i in range(3):
        if d <= seg[i]:
            f = d / seg[i]
            rx = path[i][0] + (path[i + 1][0] - path[i][0]) * f
            ry = path[i][1] + (path[i + 1][1] - path[i][1]) * f
            leg = i
            break
        d -= seg[i]
    else:
        rx, ry, leg = path[-1][0], path[-1][1], 2
    cam_x = max(0, min(m.size[0] - W, rx - W // 2 + 8))
    cam_y = max(0, min(m.size[1] - VIEW_H, ry - VIEW_H // 2))
    view = m.crop((int(cam_x), int(cam_y), int(cam_x) + W, int(cam_y) + VIEW_H)).convert('RGBA')
    step = (t // 8) % 2
    red_i = {0: 3 + step, 1: 7 + step, 2: 5 + step}[leg]       # down / sideways (flipped) / up walk
    r = red_field(red_i)
    if leg == 1:
        r = r.transpose(Image.FLIP_LEFT_RIGHT)
    put(view, r, rx - cam_x, ry - cam_y - 16)
    # PIKACHU 20 px behind; from t110 it sits down and looks back (it does not want to go)
    lag = 22 if t < 110 else 22 + (t - 110) * 2
    px_, py_ = (rx, ry + lag) if leg == 2 else (rx - lag, ry)
    pk = pika_field(0 if t >= 110 else 5 + step if leg == 2 else 7 + step)
    if leg == 1 and t < 110:
        pk = pk.transpose(Image.FLIP_LEFT_RIGHT)
    put(view, pk, px_ - cam_x, py_ - cam_y)
    view = blend(view, (255, 156, 82), max(0, 2 - t // 20))    # dawn warming to day
    return frame(view)


def battle_bg():
    return bg('graphics/battle_terrain/grass/terrain', width=64)


def cut2(t):
    """The ball it hates: a battle stage. RED (back) throws, PIKACHU zaps the ball away."""
    view = tiled(battle_bg(), 0, 16)
    pk = mon('pikachu')
    hop = -abs(round(6 * math.sin(t / 4.0))) if 30 <= t < 46 else 0
    put(view, pk, 144, -6 + hop)
    frames = [0, 0, 1, 2, 3, 4]
    put(view, red_back(frames[min(5, max(0, (t - 10) // 4))]), 24, 32)
    if 18 <= t < 34:                               # the ball's arc toward PIKACHU
        f = (t - 18) / 16.0
        put(view, ball((t // 2) % 3), 70 + 100 * f, 30 - 50 * f * (1 - f) * 2)
    if 34 <= t < 54:                               # the zap: sparks round it, the ball flies off
        for k in range(4):
            a = t / 3.0 + k * math.pi / 2
            put(view, anim('electricity', (t + k) % 4, 32, 32, SPARK), 160 + 26 * math.cos(a), 20 + 20 * math.sin(a))
        f = (t - 34) / 20.0
        put(view, ball(2), 150 - 150 * f, 20 - 60 * f * (1 - f))
    if t in (34, 35):
        view = blend(view, (255, 255, 255), 10)
    return frame(view)


def forest():
    return bg('graphics/intro/scene_3/bg')


def cut3(t):
    """Rain and SPEAROW: the opening's own forest, darkened, scrolling fast; RED runs (the
    credits run cycle) while a flock of SPEAROW comes down on him."""
    fo = forest()
    view = Image.new('RGBA', (W, VIEW_H), (24, 40, 64, 255))
    view.alpha_composite(tiled(fo, t * 4, 40))
    view = blend(view, (16, 24, 56), 9)
    for k in range(9):                             # far flock (field sprites, flapping)
        fx = (300 - t * 3 + k * 23) % 320 - 40
        put(view, sprite('graphics/object_events/pics/pokemon/spearow.png', (t // 4 + k) % 3, 16, 16),
            fx, 4 + (k * 7) % 20)
    run = sprite('graphics/credits/player_male.png', (t // 5) % 6, 64, 64)
    put(view, run, 88, 30)
    for k, (sx, sy, sc) in enumerate(((150, -20, 1.0), (40, -10, 0.75))):
        sp = affine(mon('spearow'), sc)
        put(view, sp, sx + (t % 40) - 20 * k, sy + (t % 30))
    for k in range(14):                            # the game's rain sprite
        put(view, rain((t // 2 + k) % 4), (k * 37 + t * 5) % 256 - 16, (k * 29 + t * 9) % 128 - 32)
    if t % 60 in (40, 41):                         # a lightning flash (under 3 a second)
        view = blend(view, (255, 255, 255), 8)
        put(view, anim('lightning', 2, 32, 32, SPARK), 180, 0)
    return frame(view)


def cut4(t):
    """THUNDERBOLT: the Thunder battle background, PIKACHU zooming in, the flock struck."""
    th = bg('graphics/battle_anims/backgrounds/thunder')
    view = tiled(th, 0, -t * 2)
    sc = 1.0 + min(1.0, t / 60.0)
    pk = affine(mon('pikachu'), sc)
    put(view, pk, W // 2 - pk.size[0] // 2, VIEW_H // 2 - pk.size[1] // 2 + 8)
    for k in range(6):
        a = t / 4.0 + k * math.pi / 3
        put(view, anim('electricity', (t + k) % 4, 32, 32, SPARK), 104 + 64 * math.cos(a), 32 + 36 * math.sin(a))
    if t >= 50:
        for k, x in enumerate((20, 190)):
            sp = mon('spearow')
            sp = blend(sp, (255, 255, 255), 16) if t % 4 < 2 else sp
            put(view, affine(sp, 0.75, angle=(t - 50) * 6 * (1 if k else -1)), x, -10 + (t - 50) * 2)
        for k in range(3):
            put(view, anim('lightning', (t // 2 + k) % 5, 32, 32, SPARK), 20 + k * 90, 0)
    return frame(view)


def cut5(t):
    """After the storm: a clear sky (the backdrop colour stepped per scanline), the game's
    weather clouds drifting, HO-OH's gold silhouette crossing far off with a trail of gold
    stars; RED and PIKACHU from behind, looking up."""
    view = Image.new('RGBA', (W, VIEW_H))
    d = ImageDraw.Draw(view)
    for y in range(VIEW_H):
        c = [(99, 156, 222), (123, 181, 238), (156, 205, 246), (189, 222, 255)][min(3, y // 24)]
        d.line([(0, y), (W, y)], fill=c + (255,))
    for k in range(4):
        put(view, cloud(), (k * 80 - t // 2) % 320 - 64, 40 + (k % 2) * 16)
    ho = silhouette_gold(affine(mon('ho_oh'), 0.5))
    hx = 230 - t * 2.4
    put(view, ho, hx, 6 + 4 * math.sin(t / 6.0))
    for k in range(6):
        put(view, anim('gold_stars', (t + k) % 3, 16, 8, 'graphics/battle_anims/sprites/gold_stars.gbapal'),
            hx + 30 + k * 10, 20 + (k % 2) * 4)
    put(view, red_back(0), 60, 44)
    put(view, mon('pikachu', 'back'), 108, 52)
    return frame(view)


CUTS = [  # (name, key frames t, the original capture it is compared with)
    ('c1_pallet', (10, 60, 118), '0790-s2-forest-wide.png'),
    ('c2_ball', (22, 36, 48), '0970-s3-standoff.png'),
    ('c3_storm', (10, 41, 75), '1095-s3-gengar-swipe.png'),
    ('c4_thunderbolt', (10, 45, 70), '1376-s3-zoom.png'),
    ('c5_hooh', (10, 40, 64), '0860-s2-closeup.png'),
]
FUNCS = {'c1_pallet': cut1, 'c2_ball': cut2, 'c3_storm': cut3, 'c4_thunderbolt': cut4, 'c5_hooh': cut5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/official-B'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for name, keys, orig in CUTS:
        shots = []
        for t in keys:
            im = FUNCS[name](t).convert('RGB')
            im.save(os.path.join(a.out, '%s_t%03d.png' % (name, t)))
            im.resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(a.out, '%s_t%03d_x3.png' % (name, t)))
            shots.append(('%s t%d' % (name, t), im))
        rows.append([('FR/LG original ' + orig[:4], Image.open(ORIG + orig).convert('RGB'))] + shots)
    for scale, fn in ((1, 'compare.png'), (3, 'compare_x3.png')):
        cw, ch, bar = W * scale + 6, H * scale + 16, 0
        sheet = Image.new('RGB', (cw * 4, ch * len(rows) + 16), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        d.text((4, 2), 'Opening plan B: official repository graphics only (left: the FR/LG original)', fill=(255, 255, 255))
        for r, row in enumerate(rows):
            for c, (label, im) in enumerate(row):
                x, y = c * cw, 16 + r * ch
                d.text((x + 2, y + 2), label, fill=(255, 255, 255))
                sheet.paste(im.resize((W * scale, H * scale), Image.NEAREST), (x, y + 14))
        sheet.save(os.path.join(a.out, fn))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
