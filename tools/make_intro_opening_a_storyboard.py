#!/usr/bin/env python3
"""Storyboard key frames for opening direction (a), PIKACHU vs RAICHU in VERMILION GYM
(docs/anim/opening-storyboard-A.md; user decision 2026-09-27).

Every picture element is an official graphic: FR/LG files in this repository and, where
the table says EM:, the Emerald file under /root/src/pokeemerald (Emerald in-game
graphics are allowed, 2026-09-27). The code only places, scrolls, flips, scales by an
integer (or the game's own send-out grow), alpha-blends (the hardware's OBJ blend, as
the battle's afterimages do) and palette-blends them. Nothing is drawn. Nothing under
reference/ is read.

    python3 tools/make_intro_opening_a_storyboard.py [--out docs/anim/drafts/storyboard-A]
        [--official DIR]   # the vanilla FR/LG opening frames dumped from the qa-base ROM

Writes kNN_<shot>_tNNN.png key frames (1x), contact.png / contact_x2.png (all keys) and
compare.png / compare_x2.png (each shot next to the FR/LG opening beat it replaces).
t is the code frame from F706 (plan B's skeleton: t0 = F706; revision 2 adds the bar-8
victory beat, the title at t672 = F1378).
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from official_gfx import ROOT, path, read_pal, render_map, sprite, tiles  # noqa: E402
from make_intro_opening_official_mock import (  # noqa: E402  plan B's verified helpers
    W, H, VIEW_H, blend, frame, put, tiled, s_ease, red_back)

SPR = 'graphics/battle_anims/sprites/'
ORANGE = (255, 148, 0)          # graphics/intro/scene_2/bg.gbapal: FR/LG's close-up backdrop

# the bars of MUS_INTRO_FIGHT in code frames (song starts t20; one beat = 19.15 frames)
BARS = [0, 59, 136, 212, 289, 365, 442, 519, 595, 672]   # t672 = F1378: the title (11.2 s)


def beat(bar, n):
    """Code frame of beat n (0-3) of bar (1-8)."""
    return round(BARS[bar] + 19.15 * n)


# ---------------------------------------------------------------- official pieces
_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def pika_front(flip=False, pose=0):
    """pose 0: FR/LG front.png (identical to Emerald anim_front frame 0);
    pose 1: Emerald anim_front frame 1."""
    def build():
        if pose == 0:
            s = sprite('graphics/pokemon/pikachu/front.png', 0, 64, 64, 'graphics/pokemon/pikachu/normal.pal')
        else:
            s = sprite('EM:graphics/pokemon/pikachu/anim_front.png', 1, 64, 64, 'EM:graphics/pokemon/pikachu/normal.pal')
        return s.transpose(Image.FLIP_LEFT_RIGHT) if flip else s
    return cached(('pf', flip, pose), build)


def raichu_front(pose=0, flip=False):
    """Emerald anim_front frames 0 (stance) and 1 (roar)."""
    def build():
        s = sprite('EM:graphics/pokemon/raichu/anim_front.png', pose, 64, 64, 'EM:graphics/pokemon/raichu/normal.pal')
        return s.transpose(Image.FLIP_LEFT_RIGHT) if flip else s
    return cached(('rf', pose, flip), build)


def pika_back():
    return cached('pb', lambda: sprite('graphics/pokemon/pikachu/back.png', 0, 64, 64, 'graphics/pokemon/pikachu/normal.pal'))


def surge_pic():
    return cached('surge', lambda: sprite('graphics/trainers/front_pics/leader_lt_surge_front_pic.png', 0, 64, 64))


def fx(name, i, w, h, pal):
    return cached(('fx', name, i), lambda: sprite(SPR + name + '.png', i, w, h, SPR + pal + '.gbapal'))


def impact():
    return fx('impact', 0, 32, 32, 'impact')


def spark16(i):          # ANIM_TAG_SPARK's 16x16 bolt pieces (ElectricBolt)
    return fx('spark_1', i % 4, 16, 16, 'spark')


def spark2(i):           # ANIM_TAG_SPARK_2
    return fx('spark_2', i % 3, 16, 16, 'spark_2')


def shock_ball():        # ANIM_TAG_SHOCK_3 frame 2: the Thunderbolt orb
    return fx('shock_3', 2, 32, 32, 'shock_3')


def electricity(i):
    return cached(('el', i), lambda: sprite(SPR + 'electricity.png', i % 4, 32, 32, SPR + 'electric_orbs.gbapal'))


def lightning(i):
    """Frames 0 and 2 only, with lightning_2.gbapal: the yellow/white pair plan B verified."""
    f = (0, 2)[i % 2]
    return cached(('li', f), lambda: sprite(SPR + 'lightning.png', f, 32, 32, SPR + 'lightning_2.gbapal'))


def dust(i):
    return fx('speed_dust', i % 3, 16, 16, 'speed_dust')


def ball(i):
    return cached(('ball', i), lambda: sprite('graphics/interface/ball/poke.png', i % 3, 16, 16))


def field(name, i, w=16, h=32):
    return cached(('field', name, i), lambda: sprite('graphics/object_events/pics/%s.png' % name, i, w, h))


def emote(n):
    """trainer_see.c's emoticon frame n (2x2 tiles, frames packed 4 tiles each)."""
    def build():
        ts = tiles('graphics/misc/emoticons.png')
        pal = read_pal('graphics/misc/emoticons.png')
        out = Image.new('RGBA', (16, 16))
        px = out.load()
        for q in range(4):
            tile = ts[n * 4 + q]
            for y in range(8):
                for x in range(8):
                    c = tile[y][x]
                    if c:
                        px[(q & 1) * 8 + x, (q >> 1) * 8 + y] = pal[c] + (255,)
        return out
    return cached(('emote', n), build)


def ghost(spr, alpha):
    """An afterimage: the same sprite through the OBJ alpha blend (AnimTask_TraceMonBlended)."""
    out = spr.copy()
    a = out.getchannel('A').point(lambda v: int(v * alpha))
    out.putalpha(a)
    return out


def scale2(spr):
    return spr.resize((spr.size[0] * 2, spr.size[1] * 2), Image.NEAREST)


def grow(spr, f):
    """The battle send-out: the OBJ affine scale growing to 1x (transitional only)."""
    s = max(0.1, min(1.0, f))
    w, h = spr.size
    out = spr.resize((max(1, round(w * s)), max(1, round(h * s))), Image.NEAREST)
    canvas = Image.new('RGBA', (w, h))
    canvas.alpha_composite(out, ((w - out.size[0]) // 2, h - out.size[1]))
    return canvas


def shaken(view, dx, dy):
    out = Image.new('RGBA', view.size, (0, 0, 0, 255))
    out.alpha_composite(view, (dx, dy)) if dx >= 0 and dy >= 0 else out.paste(view, (dx, dy), view)
    return out


# ---------------------------------------------------------------- backgrounds
def leader_stage():
    """BATTLE_TERRAIN_LEADER (src/battle_bg.c): the building terrain with the leader palette,
    the stage LT. SURGE's battle is fought on."""
    return cached('stage', lambda: render_map('graphics/battle_terrain/building/terrain.png',
                                              'graphics/battle_terrain/building/terrain.bin',
                                              read_pal('graphics/battle_terrain/indoor/leader.gbapal'),
                                              width=32, transparent=False))


def entry_lines():
    """The building terrain's battle-entry layer (anim.png/.bin): white speed streaks."""
    return cached('entry', lambda: render_map('graphics/battle_terrain/building/anim.png',
                                              'graphics/battle_terrain/building/anim.bin',
                                              read_pal('graphics/battle_terrain/indoor/leader.gbapal'),
                                              width=32, transparent=True))


def highspeed(side='opponent'):
    """BG_HIGHSPEED_OPPONENT / _PLAYER: the game picks the map by the attacker's side."""
    return cached(('hs', side), lambda: render_map('graphics/battle_anims/backgrounds/highspeed.png',
                                                   'graphics/battle_anims/backgrounds/highspeed_%s.bin' % side,
                                                   read_pal('graphics/battle_anims/backgrounds/highspeed.gbapal'),
                                                   width=32, transparent=False))


STORM = (16, 24, 56)            # plan B's verified storm blend colour (make_intro_opening_b.py)


def thunder_band():
    """The Thunder background's cloud rows, pixel lines 0-58 (rows 0-7 down to the rim;
    line 58 is almost one colour, the flat purple starts at 59)."""
    def build():
        th = render_map('graphics/battle_anims/backgrounds/thunder.png', 'graphics/battle_anims/backgrounds/thunder.bin',
                        read_pal('graphics/battle_anims/backgrounds/thunder.png'), width=32, transparent=False)
        return th.crop((0, 0, 256, 59))
    return cached('thunder_band', build)


def thunder_view(xu, xl):
    """Must-fix 1 (no seam, no flat band): two BG layers. The upper half is the cloud band
    upright (BG3), the lower half the same map rows with the V-flip bit (BG2), meeting at
    line 58, the rim, which is one colour across the screen: so the two layers may scroll
    at different speeds (xu, xl) without any cut, and the offset keeps the halves from
    reading as a mirror (thunder.bin itself offsets its mirrored half by 8 tiles). The
    band's top line lies outside the letterbox. The clouds slide sideways, as THUNDER's
    own AnimTask_StartSlidingBg does, instead of the vertical flow plan B used."""
    band = thunder_band()
    view = Image.new('RGBA', (W, VIEW_H))
    view.alpha_composite(tiled(band, xu, 11, h=48), (0, 0))
    view.alpha_composite(tiled(band.transpose(Image.FLIP_TOP_BOTTOM), xl + 64, 0, h=48), (0, 48))
    return view


def impact_bg():
    """BG_IMPACT_OPPONENT (the burst the game fades to for heavy hits)."""
    return cached('impbg', lambda: render_map('graphics/battle_anims/backgrounds/impact.png',
                                              'graphics/battle_anims/backgrounds/impact_opponent.bin',
                                              read_pal('graphics/battle_anims/backgrounds/impact.gbapal'),
                                              width=32, transparent=False))


def stage_view(sx=0, dark=0):
    v = tiled(leader_stage(), sx, 16)
    return blend(v, (0, 0, 0), dark) if dark else v


# VERMILION GYM map (layout VermilionCity_Gym, 11x21 blocks, gTileset_Building + gTileset_VermilionGym)
BEAM = {  # data/maps/VermilionCity_Gym/scripts.inc: On (map) -> HalfOn -> Off
    'half': {(3, 6): 0x2BB, (4, 6): 0x2BC, (5, 6): 0x2BD, (6, 6): 0x2BE, (7, 6): 0x2BF,
             (3, 7): 0x2C3, (4, 7): 0x2C4, (5, 7): 0x2C5, (6, 7): 0x2C6, (7, 7): 0x2C7},
    'off': {(3, 6): 0x293, (4, 6): 0x294, (5, 6): 0x281, (6, 6): 0x295, (7, 6): 0x296,
            (3, 7): 0x29B, (4, 7): 0x29C, (5, 7): 0x281, (6, 7): 0x29D, (7, 7): 0x29E},
}
GYM_X = 32          # the camera centred on column 5, as the game does: 2 border blocks each side


def gym_map(state, anim):
    """The gym as the game draws it: metatiles, the beam state and the motorized-door tile
    animation frame (src/tileset_anims.c: 7 tiles at 880)."""
    def build():
        prim, sec = 'data/tilesets/primary/building', 'data/tilesets/secondary/vermilion_gym'

        def tileset(d):
            ts = tiles(d + '/tiles.png')
            mt = [v for (v,) in struct.iter_unpack('<H', open(path(d + '/metatiles.bin'), 'rb').read())]
            return ts, [mt[i:i + 8] for i in range(0, len(mt), 8)]
        pt, pm = tileset(prim)
        st, sm = tileset(sec)
        st = list(st)
        at = tiles(sec + '/anim/motorizeddoor/%d.png' % anim)
        for k in range(7):
            if 240 + k < len(st):
                st[240 + k] = at[k]
        pals = []
        for i in range(16):
            f = prim if i < 7 else sec
            pp = path('%s/palettes/%02d.pal' % (f, i))
            pals.append(read_pal(pp)[:16] if os.path.exists(pp) else [(0, 0, 0)] * 16)
        blocks = [v & 0x3FF for (v,) in struct.iter_unpack('<H', open(path('data/layouts/VermilionCity_Gym/map.bin'), 'rb').read())]
        over = BEAM.get(state, {})
        bw, bh = 15, 23                     # 2 border blocks left/right, 2 rows above
        img = Image.new('RGB', (bw * 16, bh * 16))
        px = img.load()
        for by in range(bh):
            for bx in range(bw):
                mx, my = bx - 2, by - 2
                if 0 <= mx < 11 and 0 <= my < 21:
                    m = over.get((mx, my), blocks[my * 11 + mx])
                else:
                    m = 8                   # the layout's border block
                meta = pm[m] if m < 640 else sm[m - 640]
                for layer in range(2):
                    for q in range(4):
                        e = meta[layer * 4 + q]
                        t, hf, vf, bank = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
                        tile = pt[t] if t < 640 else (st[t - 640] if t - 640 < len(st) else None)
                        if tile is None:
                            continue
                        ox, oy = bx * 16 + (q & 1) * 8, by * 16 + (q >> 1) * 8
                        for y in range(8):
                            for x in range(8):
                                c = tile[7 - y if vf else y][7 - x if hf else x]
                                if c == 0 and layer:
                                    continue
                                px[ox + x, oy + y] = pals[bank][c]
        return img.convert('RGBA')
    return cached(('gym', state, anim), build)


# ---------------------------------------------------------------- the shots
def s1_gym(t):
    """S1 VERMILION GYM (t0-135): from white, the camera follows RED running north with
    PIKACHU behind; the beams go half-on (bar 1) and off (beat 2); RED stops before
    LT. SURGE, who sees him ('!', beat 4); the battle flash."""
    state = 'on' if t < BARS[1] else ('half' if t < beat(1, 1) else 'off')
    img = gym_map(state, (t // 2) % 2)
    feet0, stop = 16 * 16 + 16 + 32, 4 * 16 + 16 + 32     # feet lines in map pixels (+2 border rows)
    feet = max(stop, feet0 - max(0, t - 8) * 2)
    cam = min(max(feet - 72, 18), img.size[1] - VIEW_H)
    view = img.crop((0, cam, W, cam + VIEW_H)).convert('RGBA')
    # trainers of the map, standing (their map positions)
    for name, bx, by, fr in (('people/gym_guy', 4, 17, 0), ('people/sailor', 8, 13, 2),
                             ('people/gentleman', 7, 8, 2), ('people/balding_man', 2, 11, 0)):
        try:
            put(view, field(name, fr), GYM_X + bx * 16, (by + 2) * 16 + 16 - 32 - cam)
        except (OSError, IndexError):
            pass
    put(view, field('people/lt_surge', 0), GYM_X + 5 * 16, 4 * 16 + 16 - 32 - cam)
    running = feet > stop
    run_cycle = [(5, 6), (3, 7), (5, 6), (3, 8)]    # sAnim_RunNorth: pics 12,13,12,14 = surf_run 6,7,6,8
    if running:
        k = (t // 4) % 4
        rfr = sprite('graphics/object_events/pics/people/red_surf_run.png', run_cycle[k][1], 16, 32)
    else:
        rfr = field('people/red_normal', 1)
    # PIKACHU follows one tile behind, then steps up beside RED (walk frames, 1 px/frame)
    arrive = 8 + (feet0 - stop) // 2
    pfeet = feet + 16
    side = 0
    if t >= arrive:
        k = t - arrive
        side = min(16, 2 * k)                           # east first (2 px/frame) ...
        pfeet = stop + 16 - max(0, min(16, 2 * (k - 8)))  # ... then north beside RED
        pfr = field('pokemon/pikachu', 1 if k >= 16 else (7 + (k // 4) % 2) if k < 8 else (5 + (k // 4) % 2), 16, 16)
        if k < 8:
            pfr = pfr.transpose(Image.FLIP_LEFT_RIGHT)   # the east frames are the west ones flipped
    else:
        pfr = field('pokemon/pikachu', (5 + (t // 4) % 2) if running else 1, 16, 16)
    put(view, pfr, GYM_X + 5 * 16 + side, pfeet - 16 - cam)
    put(view, rfr, GYM_X + 5 * 16, feet - 32 - cam)
    e0 = beat(1, 3)
    if t >= e0:
        n = 0 if t < e0 + 2 else 1 if t < e0 + 4 else 2
        put(view, emote(n), GYM_X + 5 * 16, 4 * 16 + 16 - 32 - 16 - cam - (2 if t < e0 + 6 else 0))
    coeff = 0
    if t < 20:
        coeff = 16 - (t * 16) // 20
    if t in (124, 125, 126, 130, 131, 132) or t >= 133:
        coeff = 16 if t >= 133 else 12
    if coeff:
        # the fade is on the map's BG palettes and the OBJ palettes only: the border block
        # (black, colour 0 of its palette = backdrop) and the letterbox stay black (must-fix 2)
        faded = blend(view, (255, 255, 255), coeff)
        view.paste(faded.crop((GYM_X, 0, GYM_X + 176, VIEW_H)), (GYM_X, 0))
    return frame(view)


P_HOME, R_HOME = (24, 32), (148, 1)     # RAICHU at y+1: ears and tail inside the letterbox (rec. 9)                 # the battle layout inside the letterbox


def s2_battle(t):
    """S2 THE CHALLENGE (bar 2): the battle intro on SURGE's stage: trainers slide in,
    SURGE's ball sends RAICHU out (grow + white), RED raises his arm and leaves; PIKACHU
    runs in only after RED is more than half off the screen (rec. 8)."""
    u = t - BARS[2]
    view = stage_view()
    ein = s_ease(u / 24.0)
    sx = -64 + (R_HOME[0] - 4 + 64) * ein if u < 38 else R_HOME[0] - 4 + (u - 38) * 8
    if u < 24:                                         # the building terrain's entry streaks
        put(view, entry_lines(), -u * 8, 16)
    if sx < W:
        put(view, surge_pic(), sx, -6)
    rx = W - (W - P_HOME[0]) * ein if u < RED_OUT else P_HOME[0] - (u - RED_OUT) * 12
    rf = 1 if 52 <= u < RED_OUT + 4 else 0
    if rx > -64:
        put(view, red_back(rf), rx, 32)
    if 38 <= u < 50:                                   # SURGE's ball
        f = (u - 38) / 12.0
        put(view, ball(u // 2), 156 + 20 * f, 6 + 30 * f - 28 * math.sin(math.pi * f))
    if u >= 50:
        g = (u - 50) / 8.0
        r = raichu_front(1 if 60 <= u < 68 else 0)
        r = grow(r, 0.25 + 0.75 * g) if u < 58 else r
        if u < 62:
            r = blend(r, (255, 255, 255), max(0, 16 - (u - 50) * 16 // 12))
        put(view, r, *R_HOME)
    if u >= PIKA_IN:                                   # PIKACHU runs in (no ball: it lives outside)
        f = s_ease((u - PIKA_IN) / 8.0)
        px = -64 + (P_HOME[0] + 64) * f
        py = P_HOME[1] - (2 if u >= PIKA_IN + 8 else 0)
        if u < PIKA_IN + 8:
            for k, a in ((2, 0.3), (1, 0.55)):
                put(view, ghost(pika_back(), a), px - 14 * k, py)
        put(view, pika_back(), px, py)
    if u < 8:
        view = blend(view, (255, 255, 255), 16 - u * 2)
    return frame(view)


RED_OUT = 57            # beat 4 (t193): RED leaves at 12 px/frame, more than half out at u62
PIKA_IN = 66            # 4 frames after that; lands at u74 (t210)

# PIKACHU's cheeks in the flipped front sprite (red pixels of pikachu/front.png, mirrored)
CHEEKS = [(64 - 1 - 33, 26), (64 - 1 - 17, 27)]


def s3_faceoff(t):
    """S3 FACE-OFF (bar 3): 3a the 2x close-ups on FR/LG's own close-up orange (beats 1-2),
    3b the wide face-off on the stage with RAICHU's cry and PIKACHU's cheeks (beats 3-4)."""
    u = t - BARS[3]
    if u < 38:                                          # 3a
        view = Image.new('RGBA', (W, VIEW_H), ORANGE + (255,))
        f = s_ease(u / 12.0)
        pk = scale2(pika_front(flip=True))
        px, py = -128 + 104 * f, -22
        put(view, pk, px, py)
        if u >= 19:
            g = s_ease((u - 19) / 12.0)
            rc = scale2(raichu_front(1 if u >= 30 else 0))
            put(view, rc, 240 - 124 * g, -14)
        if u >= 28:
            # must-fix 6: the spark sits on PIKACHU's cheek, 2x like the face, in the
            # light yellow of electric_orbs.gbapal so it reads on orange (lightning_2
            # turns spark_2 purple: its low indices are the purple ramp)
            for k, (cx, cy) in enumerate(CHEEKS):
                if (u + k * 2) % 6 < 4:
                    sp = cached(('spk_eo', (u // 3 + k) % 3), lambda i=(u // 3 + k) % 3: sprite(
                        SPR + 'spark_2.png', i, 16, 16, SPR + 'electric_orbs.gbapal'))
                    put(view, scale2(sp), px + cx * 2 - 16 + (8 if k else -8), py + cy * 2 - 16)
        return frame(view)
    v = u - 38
    # must-fix 5: the side flow at 1 px/frame, and the stage's own entry streaks kept over
    # the floor at half strength (BLDALPHA) to break the flat white
    view = stage_view(sx=v)
    put(view, ghost(entry_lines(), 0.5), -(v * 3) % 256 - 256, 16)
    put(view, ghost(entry_lines(), 0.5), -(v * 3) % 256, 16)
    put(view, raichu_front(1 if v < 12 else 0), *R_HOME)
    dip = 2 if v >= 19 else 0
    put(view, pika_back(), P_HOME[0], P_HOME[1] + dip)
    if v >= 19:
        for k in range(3):
            a = v / 3.0 + k * 2.1
            put(view, spark2(v // 3 + k), P_HOME[0] + 24 + 26 * math.cos(a), P_HOME[1] + 12 + 12 * math.sin(a))
    return frame(view)


def dash(u, a, b, dur):
    f = min(1.0, u / float(dur))
    f = f * f                                           # accelerating, as Quick Attack's ellipse
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def trail(view, spr, pos_fn, u, n=3, step=3):
    for k in range(n, 0, -1):
        if u - k * step >= 0:
            put(view, ghost(spr, 0.6 - 0.15 * k), *pos_fn(u - k * step))
    put(view, spr, *pos_fn(u))


def s4_dashes(t):
    """S4 HIGH-SPEED EXCHANGES (bars 4-5, sparse: one hit per two beats).
    4a clash in the middle (stage), 4b racing side by side (Extreme Speed background),
    4c PIKACHU's Quick Attack over highspeed_opponent, 4d RAICHU's counter over
    highspeed_player (the scroll turns with the attacker, as the game does; must-fix 5)."""
    u = t - BARS[4]
    mid = ((P_HOME[0] + R_HOME[0]) / 2, (P_HOME[1] + R_HOME[1]) / 2)
    if u < 38:                                          # 4a
        view = stage_view(sx=u)
        put(view, ghost(entry_lines(), 0.5), -(u * 3) % 256 - 256, 16)
        put(view, ghost(entry_lines(), 0.5), -(u * 3) % 256, 16)
        hit = 19
        if u < hit:
            trail(view, pika_back(), lambda x: dash(x, P_HOME, (mid[0] - 24, mid[1] + 8), hit), u)
            trail(view, raichu_front(), lambda x: dash(x, R_HOME, (mid[0] + 24, mid[1] - 8), hit), u)
        else:
            f = s_ease((u - hit) / 18.0)
            put(view, pika_back(), mid[0] - 24 + (P_HOME[0] - mid[0] + 24) * f, mid[1] + 8 + (P_HOME[1] - mid[1] - 8) * f)
            put(view, raichu_front(), mid[0] + 24 + (R_HOME[0] - mid[0] - 24) * f, mid[1] - 8 + (R_HOME[1] - mid[1] + 8) * f)
            if u < hit + 6:
                put(view, impact(), mid[0] + 16, mid[1] + 16)
                view = shaken(view, 2 if u % 2 else -2, 0)
        return frame(view)
    if u < 76:                                          # 4b
        v = u - 38
        view = tiled(highspeed('opponent'), v * 8, 0)
        jit = lambda k: round(2 * math.sin(v * 1.3 + k))
        # rec. 7: RAICHU in the upper lane, well ahead, facing the run (flipped) until the
        # 4 frames before the ram (t342-345), when it turns back toward PIKACHU and drops on him
        rx = 150 - max(0, v - 8) * 2.2 if v < 19 else 126
        ry = -12 + (max(0, v - 13) * 2.5 if v < 19 else 15)
        turn = 15 <= v < 19
        rs = raichu_front(0 if not turn else 1, flip=not turn)
        px, py = 20, 34
        if v >= 19:
            py += min(10, (v - 19) * 2)
            px -= min(12, (v - 19) * 2)
        for k in (2, 1):
            if not turn:
                put(view, ghost(rs, 0.4 / k), rx - 20 * k, ry + jit(1))
            put(view, ghost(pika_front(flip=True), 0.4 / k), px - 20 * k, py + jit(0))
        put(view, rs, rx, ry + jit(1))
        put(view, pika_front(flip=True), px, py + jit(0))
        put(view, dust(v // 2), px - 8, py + 48)
        if 19 <= v < 25:
            put(view, impact(), px + 44, py + 8)
        return frame(view)
    if u < 115:                                         # 4c PIKACHU's Quick Attack
        v = u - 76
        hit = 19
        rec = min(10, max(0, v - hit) * 2)
        view = tiled(highspeed('opponent'), v * 8, 0)
        shake = (3 if v % 2 else -3) if hit <= v < hit + 12 else 0   # AnimTask_ShakeMon
        put(view, raichu_front(0), R_HOME[0] + rec + shake, R_HOME[1] - rec // 2)
        if v < hit:
            trail(view, pika_back(), lambda x: dash(x, P_HOME, (R_HOME[0] - 36, R_HOME[1] + 20), hit), v)
        else:
            f = s_ease((v - hit) / 18.0)
            put(view, pika_back(), R_HOME[0] - 36 + (P_HOME[0] - R_HOME[0] + 36) * f, R_HOME[1] + 20 + (P_HOME[1] - R_HOME[1] - 20) * f)
        if hit <= v < hit + 6:
            put(view, impact(), R_HOME[0] + 16, R_HOME[1] + 20)
        return frame(view)
    v = u - 115                                         # 4d RAICHU's counter
    hit = 18
    view = tiled(highspeed('player'), -v * 8, 0)
    knock = min(16, max(0, v - hit) * 3)
    shake = (3 if v % 2 else -3) if hit <= v < hit + 12 else 0
    put(view, pika_back(), P_HOME[0] - knock + shake, P_HOME[1])
    if v >= hit:
        put(view, dust(v // 2), P_HOME[0] + 20 - knock, P_HOME[1] + 50)
    if v < hit:
        trail(view, raichu_front(1), lambda x: dash(x, R_HOME, (P_HOME[0] + 40, P_HOME[1] - 16), hit), v)
    else:
        f = s_ease((v - hit) / 18.0)
        put(view, raichu_front(0), P_HOME[0] + 40 + (R_HOME[0] - P_HOME[0] - 40) * f, P_HOME[1] - 16 + (R_HOME[1] - P_HOME[1] + 16) * f)
    if hit <= v < hit + 6:
        put(view, impact(), P_HOME[0] + 20, P_HOME[1] + 12)
    return frame(view)


def bolt(view, x0, y0, x1, y1, u):
    """ElectricBolt: SPARK pieces laid head to tail from (x0,y0) toward (x1,y1)."""
    n = int(math.dist((x0, y0), (x1, y1)) // 12)
    for k in range(n + 1):
        f = k / float(max(1, n))
        wob = 5 * math.sin(k * 2.3 + u)
        put(view, spark16(k + u // 2), x0 + (x1 - x0) * f - 8, y0 + (y1 - y0) * f - 8 + wob)


def s5_clash(t):
    """S5 THUNDERBOLT CLASH (bar 6, dense): side view over the Thunder clouds (plan B's
    verified C4 layer); charge, bolts meet at the middle, THUNDER strikes the knot, the knot
    is pushed toward PIKACHU and back."""
    u = t - BARS[6]
    view = blend(thunder_view(u * 2, u * 3), STORM, 9)
    shake = (1 if u % 2 else -1) if 38 <= u < 50 else 0
    pk_x = 8 + (8 if u >= 57 else 0)
    put(view, pika_front(flip=True), pk_x, 26)
    put(view, raichu_front(1 if u >= 10 else 0), 168, 22)
    if u < 19:
        for who, cx in ((0, pk_x + 32), (1, 200)):
            for k in range(3):
                a = u / 3.0 + k * 2.1 + who
                put(view, electricity(u + k), cx - 16 + 26 * math.cos(a), 40 - 16 + 18 * math.sin(a))
    knot = 120
    if u >= 38:
        knot = 120 - 20 * s_ease((u - 38) / 19.0) if u < 57 else 100 + 50 * s_ease((u - 57) / 19.0)
    if u >= 19:
        reach = min(1.0, (u - 19) / 19.0)
        bolt(view, pk_x + 44, 48, pk_x + 44 + (knot - pk_x - 44) * reach, 44, u)
        bolt(view, 196, 44, 196 + (knot - 196) * reach, 44, u + 1)
    if u >= 38:
        put(view, shock_ball(), knot - 16, 28)
        for k in range(2):
            put(view, electricity(u + k), knot - 16 + (k * 2 - 1) * 12, 28 + (k * 2 - 1) * 6)
        if u < 46:
            for k, y in enumerate((-36, -20, 12)):          # THUNDER's column onto the knot
                put(view, lightning(k + u // 2), knot - 16, 44 + y - 16)
    if u in (38, 39):
        view = blend(view, (255, 255, 255), 10)
    return frame(shaken(view, shake, 0) if shake else view)


def storm_view(u):
    """S5's sky kept for S6 (must-fix 3), the same storm blend, the slide doubled to
    4 and 6 px/frame (the art director's 4 px/frame, turned sideways with the layer)."""
    return blend(thunder_view(154 + u * 4, 231 + u * 6), STORM, 9)


# S6 Agility: PIKACHU hops between stops; each THUNDER lands on the oldest afterimage only
P_STOP1 = (88, -4)                          # 73 px up-right of P_HOME: clear of the first bolt
P_MID1 = (56, 14)                           # the one trace between (37 px from each end)
P_STOP2 = (108, 36)                         # 45 px from P_STOP1, down under RAICHU: clear of the second
P_MID2 = (98, 16)                           # trace of that hop (22 px from P_STOP1, 22 from P_STOP2)
P_HIT = (R_HOME[0] - 30, R_HOME[1] + 14)
STRIKES = (0, 19)                           # t519, t538 (beats 1 and 2 of bar 7)


def lerp(a, b, f):
    return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f


def s6_pika(u):
    """PIKACHU's place in S6 and its afterimages [(pos, struck?)], oldest first."""
    wob = (round(2 * math.sin(u / 2.0)), round(math.cos(u / 2.0)))   # Agility's small ellipse
    if u < 15:
        body = (P_STOP1[0] + wob[0], P_STOP1[1] + wob[1])
        ghosts = []
        if u < 1:
            ghosts.append((P_HOME, True))          # the first bolt's afterimage, white, then gone
        if u < 6:
            ghosts.append((P_MID1, False))
        return body, ghosts
    if u < 34:
        f = min(1.0, (u - 15) / 4.0)
        body = lerp(P_STOP1, P_STOP2, f)
        if u >= 19:
            body = (P_STOP2[0] + wob[0], P_STOP2[1] + wob[1])
        ghosts = []
        if u <= 19:
            ghosts.append((P_STOP1, u == 19))     # the oldest: the second bolt's target
        if 15 <= u < 24:
            ghosts.append((P_MID2, False))
        return body, ghosts
    if u < 38:
        f = (u - 34) / 4.0
        return lerp(P_STOP2, P_HIT, f * f), [(P_STOP2, False)]
    if u < 44:
        return P_HIT, []
    f = s_ease(min(1.0, (u - 44) / 12.0))
    return lerp(P_HIT, P_HOME, f), []


def s6_agility(t):
    """S6 AGILITY (bar 7, dense), over S5's storm sky (flow 4 px/frame): RAICHU's THUNDER
    lands twice, each time on PIKACHU's oldest afterimage, which flashes white one frame
    and is gone, while PIKACHU, 33+ px away, closes in (up-right, then toward RAICHU);
    the Quick Attack lands on beat 3 over the impact burst; RAICHU blinks white and
    faints on beat 4; white on bar 8."""
    u = t - BARS[7]
    if 38 <= u < 47:                                    # the final hit: the impact burst BG
        view = tiled(impact_bg(), 0, 24)
    else:
        view = storm_view(u)                            # continues S5's scroll phase
    ry = R_HOME[1] + (0 if u < 57 else (u - 57) * 5)   # the faint: straight down out of view
    r = raichu_front(1 if u < 30 else 0)
    if 47 <= u < 57 and (u - 47) % 4 < 2:
        r = blend(r, (255, 255, 255), 16)
    shake = (3 if u % 2 else -3) if 38 <= u < 50 else 0
    if ry < VIEW_H:
        put(view, r, R_HOME[0] + shake, ry)
    body, ghosts = s6_pika(u)
    for pos, struck in ghosts:
        g = ghost(pika_back(), 0.5)
        if struck:                                      # sprite-only white (rec. 11), then gone
            g = blend(pika_back(), (255, 255, 255), 16)
        put(view, g, *pos)
    put(view, pika_back(), *body)
    for s0, spot in zip(STRIKES, (P_HOME, P_STOP1)):
        if s0 <= u < s0 + 8:                            # THUNDER's column onto the old spot
            for k, y in enumerate((-40, -8, 24)):
                put(view, lightning(k + u), spot[0] + 16, spot[1] + y)
    if 38 <= u < 44:
        put(view, impact(), R_HOME[0] + 16, R_HOME[1] + 20)
    if u >= 57:
        for k in range(3):
            a = u / 3.0 + k * 2.1
            put(view, spark2(u // 3 + k), body[0] + 24 + 24 * math.cos(a), body[1] + 10 + 10 * math.sin(a))
    if u >= 70:
        view = blend(view, (255, 255, 255), min(16, (u - 69) * 3))
    view = shaken(view, shake, 0) if shake else view
    return frame(view)


PIKA_CHEEKS = [(33, 25), (17, 26)]        # red pixels of pikachu/front.png (not flipped)


def s7_victory(t):
    """S7 VICTORY (bar 8, rec. 10): FR/LG's own white (as F1340/F1376). PIKACHU front 1x
    in the middle, RED's back bottom-left; beat 2 RED raises his arm and PIKACHU's cheeks
    spark once; beat 3 one integer cut to 2x: PIKACHU's happy frame (Emerald anim_front 1);
    white into the title at bar 9 (t672 = F1378)."""
    u = t - BARS[8]
    view = Image.new('RGBA', (W, VIEW_H), (255, 255, 255, 255))
    lay = Image.new('RGBA', (W, VIEW_H))
    if u < 38:
        put(lay, pika_front(), 88, 14)
        put(lay, red_back(1 if u >= 19 else 0), 4, 40)
        if 19 <= u < 31:
            for k, (cx, cy) in enumerate(PIKA_CHEEKS):
                put(lay, spark2(u // 3 + k), 88 + cx - 8 + (6 if k == 0 else -6), 14 + cy - 8)
        if u < 8:
            lay = blend(lay, (255, 255, 255), 16 - u * 2)
    else:
        put(lay, scale2(pika_front(pose=1)), 56, -20)
    view.alpha_composite(lay)
    if u >= 66:
        view = blend(view, (255, 255, 255), min(16, (u - 65) * 2))
    return frame(view)


SHOTS = [  # (id, name, start, end, fn, key frames, vanilla FR/LG frames it is compared with)
    ('S1', 'gym', 0, 136, s1_gym, (10, 60, 85, 122), (720, 746)),
    ('S2', 'challenge', 136, 212, s2_battle, (150, 190, 200, 205, 211), (790, 820)),
    ('S3', 'faceoff', 212, 289, s3_faceoff, (226, 244, 255, 275), (860, 920, 950)),
    ('S4', 'dashes', 289, 442, s4_dashes, (300, 309, 335, 344, 347, 384, 422), (1000, 1120, 1160)),
    ('S5', 'thunderbolt', 442, 519, s5_clash, (455, 470, 481, 510), (1236, 1256)),
    ('S6', 'agility', 519, 595, s6_agility, (519, 523, 528, 538, 543, 547, 560, 566, 585), (1280, 1300)),
    ('S7', 'victory', 595, 672, s7_victory, (600, 620, 650), (1340, 1376)),
]


def label_sheet(rows, cols, scale, title):
    cw, ch = W * scale + 6, H * scale + 18
    sheet = Image.new('RGB', (cw * cols, ch * len(rows) + 20), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    d.text((4, 4), title, fill=(255, 255, 255))
    for r, row in enumerate(rows):
        for c, (lab, im) in enumerate(row):
            x, y = c * cw, 20 + r * ch
            d.text((x + 2, y + 2), lab, fill=(255, 255, 255))
            sheet.paste(im.resize((W * scale, H * scale), Image.NEAREST), (x, y + 16))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs/anim/drafts/storyboard-A'))
    ap.add_argument('--official', default=None, help='dir of vanilla FR/LG frames NNNN.png (qa-base dump)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    off = a.official or os.path.join(a.out, 'official')
    contact, compare = [], []
    n = 0
    for sid, name, t0, t1, fn, keys, orig in SHOTS:
        row = []
        for t in keys:
            n += 1
            im = fn(t).convert('RGB')
            im.save(os.path.join(a.out, 'k%02d_%s_%s_t%03d.png' % (n, sid, name, t)))
            row.append(('k%02d %s t%d F%d' % (n, sid, t, 706 + t), im))
        contact.append(row)
        crow = []
        for f in orig:
            p = os.path.join(off, '%04d.png' % f)
            if os.path.exists(p):
                crow.append(('FR/LG F%d' % f, Image.open(p).convert('RGB')))
        room = max(1, 6 - len(crow))
        idx = sorted({round(i * (len(row) - 1) / max(1, room - 1)) for i in range(room)}) if room > 1 else [0]
        pick = [row[i] for i in idx]
        compare.append(crow + pick)
    cols = max(len(r) for r in contact)
    for s, fn_ in ((1, 'contact.png'), (2, 'contact_x2.png')):
        label_sheet(contact, cols, s, 'Opening A storyboard rev. 2 (PIKACHU vs RAICHU, 672 frames): official graphics only. t = code frame from F706').save(os.path.join(a.out, fn_))
    for s, fn_ in ((1, 'compare.png'), (2, 'compare_x2.png')):
        label_sheet(compare, 6, s, 'Left: FR/LG opening beat (vanilla ROM, emulator). Right: the direction (a) shot in its place').save(os.path.join(a.out, fn_))
    print('wrote', a.out, n, 'keys')


if __name__ == '__main__':
    main()
