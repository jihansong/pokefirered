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


# ---------------------------------------------------------------- the cuts (draft B2)
ROUTE_H = 40 * 16
# RED leaves his house (door under the left house) and walks to the gap north of town
C1_PATH = [(96, ROUTE_H + 120), (96, ROUTE_H + 136), (200, ROUTE_H + 136), (200, ROUTE_H - 64)]


def c1_red(t):
    """RED's position (left, feet line) and which leg of the path he is on."""
    seg = [math.dist(C1_PATH[i], C1_PATH[i + 1]) for i in range(3)]
    d = max(0.0, t - 8) * 2.0
    for i in range(3):
        if d <= seg[i]:
            f = d / seg[i]
            return (C1_PATH[i][0] + (C1_PATH[i + 1][0] - C1_PATH[i][0]) * f,
                    C1_PATH[i][1] + (C1_PATH[i + 1][1] - C1_PATH[i][1]) * f, i)
        d -= seg[i]
    return C1_PATH[-1][0], C1_PATH[-1][1], 2


def cut1(t):
    """Pallet Town at dawn. The camera comes down from above onto RED's door (t0-23),
    follows him north, and stops at t100 so that PIKACHU, who sits down and looks back
    at t110, stays whole in the picture while RED walks on out of the top."""
    m = pallet_map()
    rx, ry, leg = c1_red(t)
    ft = min(t, 100)
    fx, fy, _ = c1_red(ft)
    cam_x = max(0, min(m.size[0] - W, fx - W // 2 + 8))
    cam_y = max(0, min(m.size[1] - VIEW_H, fy - VIEW_H // 2 - 8))
    if t < 24:                                            # the opening tilt down
        cam_y -= round(72 * (1 - s_ease(t / 24.0)))
    view = m.crop((int(cam_x), int(cam_y), int(cam_x) + W, int(cam_y) + VIEW_H)).convert('RGBA')
    step = (t // 8) % 2
    walking = t >= 8
    red_i = {0: 3 + step, 1: 7 + step, 2: 5 + step}[leg] if walking else 0
    r = red_field(red_i)
    if leg == 1 and walking:
        r = r.transpose(Image.FLIP_LEFT_RIGHT)
    put(view, r, rx - cam_x, ry - cam_y - 16)
    # PIKACHU walks where RED was 11 frames before; at t110 it stops and turns round
    pt = min(t, 110) - 11
    px_, py_, pleg = c1_red(pt)
    if t >= 110:
        pk = pika_field(0)
    else:
        pk = pika_field({0: 3 + step, 1: 7 + step, 2: 5 + step}[pleg] if pt >= 8 else 0)
        if pleg == 1 and pt >= 8:
            pk = pk.transpose(Image.FLIP_LEFT_RIGHT)
    if t >= 11:
        put(view, pk, px_ - cam_x, py_ - cam_y)
    view = blend(view, (255, 156, 82), max(0, 4 - t // 6))    # dawn warming to day (first 24 frames)
    return frame(view)


def s_ease(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def battle_bg():
    return bg('graphics/battle_terrain/grass/terrain', width=64)


# RED's throw, timed as FR/LG's sAnimCmd_Red_1 (src/data/trainer_graphics/back_pic_anims.h):
# frame 1 for 20, 2 for 6, 3 for 6, 4 for 24, then 0. The ball leaves on frame 3.
RED_THROW = [(4, 0), (24, 1), (30, 2), (36, 3), (60, 4), (999, 0)]
BALL_OUT, BALL_HIT = 32, 48


def red_throw_frame(t):
    for until, f in RED_THROW:
        if t < until:
            return f
    return 0


def cut2(t):
    """The ball it hates: a battle stage. RED (back) throws, the ball arcs over, PIKACHU
    hops and zaps it, and the ball flies back past RED."""
    view = tiled(battle_bg(), 0, 16)
    pk = mon('pikachu')
    hop = -round(8 * math.sin(math.pi * (t - 44) / 14.0)) if 44 <= t < 58 else 0
    put(view, pk, 144, -6 + hop)
    put(view, red_back(red_throw_frame(t)), 24, 32)
    if BALL_OUT <= t < BALL_HIT:                           # the arc toward PIKACHU
        f = (t - BALL_OUT) / float(BALL_HIT - BALL_OUT)
        put(view, ball((t // 2) % 2), 72 + 96 * f, 40 - 24 * math.sin(math.pi * f) - 16 * f)
    if BALL_HIT <= t < 56:                                 # the zap round PIKACHU
        for k in range(4):
            a = t / 3.0 + k * math.pi / 2
            put(view, anim('electricity', (t + k) % 4, 32, 32, SPARK), 160 + 26 * math.cos(a), 20 + 20 * math.sin(a))
    if BALL_HIT <= t < 70:                                 # the ball bounced back over RED
        f = (t - BALL_HIT) / 22.0
        put(view, ball((t // 2) % 2), 168 - 190 * f, 20 - 40 * math.sin(math.pi * f * 0.8) + 40 * f * f)
    if t in (BALL_HIT, BALL_HIT + 1):
        view = blend(view, (255, 255, 255), 10)
    return frame(view)


def forest():
    return bg('graphics/intro/scene_3/bg')


def swoop(t, t0, dur, left_to_right):
    """A close SPEAROW coming in at a slant from off-screen, grazing over RED's head
    (RED's head at about (120, 34)), and leaving: a parabola, 1x."""
    f = (t - t0) / float(dur)
    x0, x1 = (-70, 250) if left_to_right else (250, -70)
    x = x0 + (x1 - x0) * f
    y = -6 + 60 * (f - 0.5) ** 2 * 4 - 40
    return x, y


def cut3(t):
    """Rain and SPEAROW: the opening's own forest, darkened, scrolling fast; RED runs (the
    credits run cycle); the far flock flaps; two SPEAROW swoop over his head in turn."""
    fo = forest()
    view = Image.new('RGBA', (W, VIEW_H), (24, 40, 64, 255))
    view.alpha_composite(tiled(fo, t * 4, 40))
    view = blend(view, (16, 24, 56), 9)
    for k in range(9):                                     # far flock (field sprites, flapping)
        fx = (300 - t * 3 + k * 23) % 320 - 40
        put(view, sprite('graphics/object_events/pics/pokemon/spearow.png', (t // 4 + k) % 3, 16, 16),
            fx, 4 + (k * 7) % 20)
    put(view, sprite('graphics/credits/player_male.png', (t // 5) % 6, 64, 64), 88, 30)
    for t0, ltr in ((20, False), (60, True), (110, False)):
        if t0 <= t < t0 + 26:
            sp = mon('spearow')
            if ltr:
                sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
            x, y = swoop(t, t0, 26, ltr)
            put(view, sp, x, y + 40)
    for k in range(14):                                    # the game's rain sprite
        put(view, rain((t // 2 + k) % 4), (k * 37 + t * 5) % 256 - 16, (k * 29 + t * 9) % 128 - 32)
    if t % 60 in (40, 41):                                 # lightning: grey wash for 2 frames only
        view = blend(view, (255, 255, 255), 8)
        put(view, anim('lightning', 2, 32, 32, None), 180, 0)
    return frame(view)


def thunder_clouds():
    """Only the cloud rows of the Thunder background (the top 64 lines), stacked so they
    can flow vertically without the flat striped lower half."""
    def build():
        th = bg('graphics/battle_anims/backgrounds/thunder')
        band = th.crop((0, 0, 256, 64))
        out = Image.new('RGBA', (256, 128))
        out.paste(band, (0, 0))
        out.paste(band, (0, 64))
        return out
    return layer('thunder_clouds', build)


def cut4(t):
    """THUNDERBOLT: the Thunder clouds flowing down, darkened as in battle; PIKACHU at 1x
    comes up into the middle, sparks round it; bolts strike the two SPEAROW, which blink
    white three times and drop straight down out of the picture."""
    view = tiled(thunder_clouds(), 0, -t * 2)
    view = blend(view, (0, 0, 0), 9)                      # the battle's darkening (BLDY)
    shake = (1 if t % 2 else -1) if 50 <= t < 62 else 0
    rise = round(24 * (1 - s_ease(t / 30.0)))
    put(view, mon('pikachu'), W // 2 - 32 + shake, 16 + rise)
    for k in range(4):
        a = t / 4.0 + k * math.pi / 2
        put(view, anim('electricity', (t + k) % 4, 32, 32, SPARK), 104 + 50 * math.cos(a), 30 + 30 * math.sin(a))
    for k, x in enumerate((8, 168)):
        sp = mon('spearow')
        if k == 0:
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        y = 4 + round(3 * math.sin(t / 5.0 + k))
        if 50 <= t < 62 and (t - 50) % 4 < 2:              # three white blinks
            sp = blend(sp, (255, 255, 255), 16)
        if t >= 62:
            y += (t - 62) * (t - 62) // 4                   # falls, facing the same way
        put(view, sp, x, y)
        if 48 <= t < 56:
            put(view, anim('lightning', 0 if (t // 2) % 2 else 2, 32, 32, None), x + 16, -8)
    if t in (50, 51):
        view = blend(view, (255, 255, 255), 10)
    return frame(view)


def gold_field_hooh(i):
    """The field sprite of HO-OH, its palette recoloured to a gold ramp (order kept)."""
    return silhouette_gold(sprite('graphics/object_events/pics/pokemon/ho_oh.png', i, 32, 32))


def cut5(t):
    """After the storm: a clear sky (the backdrop colour changed every 8 lines, 12 steps),
    two layers of the game's weather clouds, HO-OH's gold field sprite crossing the top
    third with three gold stars behind it; RED and PIKACHU from behind in the bottom third."""
    view = Image.new('RGBA', (W, VIEW_H))
    d = ImageDraw.Draw(view)
    top, bot = (99, 156, 222), (206, 234, 255)
    for y in range(VIEW_H):
        k = min(11, y // 8) / 11.0
        c = tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    cl = cloud()
    for x0, y, speed, flip in ((30, 16, 0.25, False),):                            # far layer
        put(view, cl.transpose(Image.FLIP_LEFT_RIGHT) if flip else cl, (x0 - t * speed) % 320 - 64, y)
    for x0, y, speed, flip in ((110, 44, 0.75, False), (290, 50, 0.75, True)):     # near layer
        put(view, cl.transpose(Image.FLIP_LEFT_RIGHT) if flip else cl, (x0 - t * speed) % 320 - 64, y)
    hx = 240 - t * 3.6
    hy = 2 + round(2 * math.sin(t / 6.0))
    for k in range(3):
        put(view, anim('gold_stars', (t // 3 + k) % 3, 16, 8, 'graphics/battle_anims/sprites/gold_stars.gbapal'),
            hx + 30 + k * 18, hy + 16 + (k % 2) * 3)
    put(view, gold_field_hooh((t // 8) % 2), hx, hy)
    put(view, red_back(0), 40, 48)          # head on the lower-third line (y 64 of 96)
    put(view, mon('pikachu', 'back'), 120, 56)
    return frame(view)


CUTS = [  # (name, key frames t, the original capture it is compared with)
    ('c1_pallet', (4, 40, 118), '0790-s2-forest-wide.png'),
    ('c2_ball', (20, 40, 50, 60), '0970-s3-standoff.png'),
    ('c3_storm', (12, 33, 72), '1095-s3-gengar-swipe.png'),
    ('c4_thunderbolt', (10, 51, 66), '1376-s3-zoom.png'),
    ('c5_hooh', (10, 40, 64), '0860-s2-closeup.png'),
]
FUNCS = {'c1_pallet': cut1, 'c2_ball': cut2, 'c3_storm': cut3, 'c4_thunderbolt': cut4, 'c5_hooh': cut5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/official-B2'))
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
        sheet = Image.new('RGB', (cw * 5, ch * len(rows) + 16), (40, 40, 40))
        d = ImageDraw.Draw(sheet)
        d.text((4, 2), 'Opening plan B2: official repository graphics only (left: the FR/LG original)', fill=(255, 255, 255))
        for r, row in enumerate(rows):
            for c, (label, im) in enumerate(row):
                x, y = c * cw, 16 + r * ch
                d.text((x + 2, y + 2), label, fill=(255, 255, 255))
                sheet.paste(im.resize((W * scale, H * scale), Image.NEAREST), (x, y + 14))
        sheet.save(os.path.join(a.out, fn))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
