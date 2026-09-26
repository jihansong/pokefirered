#!/usr/bin/env python3
"""Draw and time scene 2 of the new opening: "the PIKACHU that hates POKe BALLS".

docs/anim/opening-storyboard.md 3.3, scene 2 (F842-917, 76 frames, bar 2 of
MUS_INTRO_FIGHT). Draft B, after the art direction review of draft A
(docs/team/art/v0.11.0-opening-scene2-A.md, -A-style.md).

In OAK's lab the camera trucks right while the professor's forearm (sleeve and hand
only) brings in a POKe BALL. PIKACHU watches, twitches an ear, narrows its eyes as the
ball comes close; on beat 2 the ball starts to open and PIKACHU snaps its head away
(a turning frame, a squeezed smear, an overshoot of ears and tail); sparks gather on
the ball, a bolt from its cheek hits the ball, the screen shakes, the ball pops out of
the hand in a puff, lands on the table on beat 3 and rolls off; PIKACHU sulks, lifts
its chin "hmph!" with a crackle on beat 4 and flicks its tail at the second crackle.

Everything is drawn by rule (tools/intro_opening_art.py, the PIKACHU model in
tools/intro_opening_pikachu.py); nothing is traced or copied from the anime.

- Background in two layers for parallax: the lab wall (window with morning light, a
  white metal shelf of books and a machine, FR/LG lab colours) on BG3 at half speed,
  the green-topped lab table (where FR/LG's starter balls lie) on BG2 at full speed.
- The picture is 240x96, inside the intro's letterbox (screen rows 32-127).
- choreography() gives every sprite's place and frame and the two layers' scroll for
  each of the 76 frames. The game plays that table back (src/data/intro_opening_scene2.h),
  so the previews and the game show the same thing.

Writes graphics/intro/opening/scene2/{bg.png,bg_back.bin,bg_front.bin,pikachu.png,
arm.png,ball.png,spark.png,bolt.png} and src/data/intro_opening_scene2.h. With
--preview DIR also the model sheets and a mock-up of every frame (DIR/mock/tNN.png).
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_opening_art import Figure, stamp, to_image, enlarge  # noqa: E402
import intro_opening_pikachu as pika  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = ROOT + '/graphics/intro/opening/scene2'
HEADER = ROOT + '/src/data/intro_opening_scene2.h'

PIKA_PAL = pika.PAL
PIKA_FRAMES = ('A', 'A_twitch', 'A_sus', 'MID', 'B', 'C_over', 'C', 'C_hmph', 'C_flick')

# ---------------------------------------------------------------- forearm, ball, smoke
# 1-8: the thrown POKe BALL's colours in the slots graphics/interface/ball/poke.png
# uses (its frames are used as they are). 9, 14, 15: OAK's lab coat (light grey body,
# blue-grey folds, grey lit rim; white is the highlight). 10-13: OAK's skin.
PROP_PAL = [(0, 0, 0), (131, 0, 0), (172, 0, 0), (213, 41, 41), (255, 156, 123), (255, 255, 255),
            (148, 148, 148), (65, 65, 65), (24, 24, 24), (213, 213, 222), (255, 222, 205),
            (238, 180, 148), (197, 139, 106), (106, 74, 74), (139, 156, 164), (115, 115, 115)]
P_WHITE, P_GREY, P_DGREY, P_BLACK, P_COAT = 5, 6, 7, 8, 9
P_SKIN_L, P_SKIN, P_SKIN_S, P_SKIN_O = 10, 11, 12, 13
P_FOLD, P_COAT_RIM = 14, 15
PROP_COLORS = {
    'C': dict(base=P_COAT, rim=P_COAT_RIM, rim_dark=P_BLACK, line=P_FOLD, mid=P_FOLD, shade=(0, 4)),
    'S': dict(base=P_SKIN, rim=P_SKIN_O, rim_dark=P_BLACK, line=P_SKIN_O, mid=P_SKIN_S, shade=(2, 2)),
}
BALL_PNG = ROOT + '/graphics/interface/ball/poke.png'
ARM_W, ARM_H = 128, 64          # two 64x64 sprites side by side
ARM_ANGLE = -0.58               # the forearm rises to the right
ARM_CUFF = (72, 26)             # middle of the cuff on the arm canvas


def _along(t, s):
    """Point t pixels along the forearm from the cuff and s pixels across it
    (positive s = the underside)."""
    c, sn = math.cos(ARM_ANGLE), math.sin(ARM_ANGLE)
    return (ARM_CUFF[0] + t * c - s * sn, ARM_CUFF[1] + t * sn + s * c)


def palm_centre():
    return _along(14, -1)


def ball_centre():
    """The ball's centre on the arm canvas while the hand holds it: above the palm."""
    px, py = palm_centre()
    return px + 1, py - 10


def ball_on_hand():
    """Corner of the 16x16 ball sprite while the hand holds it (the game's ball is 12
    pixels across, rows and columns 2-13 of its sprite)."""
    bx, by = ball_centre()
    return round(bx - 7.5), round(by - 7.5)


def arm(grip='hold'):
    """The professor's forearm reaching in from the lower left: a lab coat sleeve long
    enough to leave the picture, the cuff, and a hand in the FR/LG people style (one
    mitten of four fingers split by creases, a thumb joined to the palm).
    'hold': the fingers curl round the front of the ball, only its top half shows.
    'open': the hand springs open, fingers fanned up, thumb out to the side."""
    f = Figure(ARM_W, ARM_H)
    f.poly('sleeve', [_along(-130, -12), _along(-2, -11), _along(1, -8), _along(1, 8),
                      _along(-2, 11), _along(-130, 13)], kind='C')
    cx, cy = _along(0, 0)
    f.ellipse('cuff', cx, cy, 3, 10.5, kind='C', rot=ARM_ANGLE)
    f.poly('wrist', [_along(1, -5), _along(9, -5.5), _along(9, 5), _along(1, 5)], kind='S')
    px, py = palm_centre()
    f.ellipse('palm', px, py, 10, 5.5, kind='S', rot=ARM_ANGLE)
    f.merged('wrist', 'palm')
    bx, by = ball_centre()
    if grip == 'hold':
        f.ellipse('thumb', bx - 6, by + 4, 2.3, 4.5, kind='S', rot=0.5)
        for i in range(4):                       # fingers across the front of the ball
            f.ellipse('finger%d' % i, bx + 4.5 - i * 0.8, by + 0.5 + i * 2.2, 3.6, 1.7, kind='S', rot=-0.25)
    else:
        f.ellipse('thumb', bx - 6, by + 5, 2.2, 4.5, kind='S', rot=-0.5)
        for i, a in enumerate((-0.55, -0.2, 0.15, 0.5)):
            fx = px + 5 + math.sin(a) * 6
            fy = py - 5 - math.cos(a) * 6 + abs(a) * 3
            f.ellipse('finger%d' % i, fx, fy, 1.7, 4, kind='S', rot=a)
            f.merged('finger%d' % i, 'palm')
    img = f.render(PROP_COLORS)
    owner = f.owner
    # white highlight band along the lit (upper) side of the sleeve
    for y in range(ARM_H):
        for x in range(ARM_W):
            if owner[y][x] == 'sleeve' and img[y][x] == P_COAT:
                if any(y - k >= 0 and owner[y - k][x] is None for k in (2, 3)):
                    img[y][x] = P_WHITE
    # folds: a long one toward the elbow, a short one, one before the cuff (uneven)
    for t0, s0, s1 in ((-46, -7, 5), (-30, -1, 6), (-12, -4, 2)):
        for k in range(s0 * 2, s1 * 2 + 1):
            x, y = _along(t0 + abs(k) * 0.45, k * 0.5)
            x, y = int(x), int(y)
            if 0 <= x < ARM_W and 0 <= y < ARM_H and img[y][x] in (P_COAT, P_WHITE):
                img[y][x] = P_FOLD
    # the cuff's hem: a lighter band, a black line under it (wrist side)
    for y in range(ARM_H):
        for x in range(ARM_W):
            if owner[y][x] == 'cuff' and img[y][x] in (P_COAT, P_FOLD):
                img[y][x] = P_WHITE
            if owner[y][x] == 'cuff' and x + 1 < ARM_W and owner[y][x + 1] in ('wrist', 'palm') \
                    and img[y][x] not in (P_BLACK,):
                img[y][x] = P_BLACK
    return img


def ball_frames():
    """16x16: the game's thrown POKe BALL, the same turned 90/180/270 degrees
    (rolling), the game's 'opening' frame, then two frames of a small grey puff."""
    src = Image.open(BALL_PNG)
    still = src.crop((0, 0, 16, 16))
    opening = src.crop((0, 16, 16, 32))
    frames = [still, still.transpose(Image.ROTATE_270), still.transpose(Image.ROTATE_180),
              still.transpose(Image.ROTATE_90), opening]
    out = [[[fr.getpixel((x, y)) for x in range(16)] for y in range(16)] for fr in frames]
    for size in (3.5, 5.5):
        f = Figure(16, 16)
        for i, (dx, dy) in enumerate(((-2, 1), (2, 1), (0, -1.5))):
            f.ellipse('puff%d' % i, 8 + dx * size / 3.5, 8 + dy * size / 3.5, size * 0.6, size * 0.55, kind='C')
        f.merged('puff0', 'puff1', 'puff2')
        img = f.render({'C': dict(base=P_WHITE, rim=P_GREY, rim_dark=P_DGREY, mid=P_GREY, shade=(2, 2))})
        if size > 4:                             # the second puff thins out
            for y in range(16):
                for x in range(16):
                    if (x + y) % 3 == 0 and img[y][x] == P_WHITE:
                        img[y][x] = 0
        out.append(img)
    return out


BALL_ROLL = (0, 3, 2, 1)         # ball frames turning anticlockwise (rolling left)
BALL_OPENING, SMOKE_FIRST = 4, 5


# ---------------------------------------------------------------- sparks and bolt (PIKACHU palette)
SPARKS = (['................',
           '.......y........',
           '......yl........',
           '...y..yly...y...',
           '....y.ylly.y....',
           '.....yllllyy....',
           '..yyylllllly....',
           '....yllWWlly....',
           '....ylWWWllyyy..',
           '...yyllWllly....',
           '....ylllllly....',
           '....yy.llly.y...',
           '...y...yly...y..',
           '.......yl.......',
           '........y.......',
           '................'],
          ['................',
           '..y.........y...',
           '...y.......y....',
           '....y..l..y.....',
           '.....y.l.y......',
           '.......l........',
           '..yy..lWl..yy...',
           '....llWWWll.....',
           '..yy..lWl..yy...',
           '.......l........',
           '.....y.l.y......',
           '....y..l..y.....',
           '...y.......y....',
           '..y.........y...',
           '................',
           '................'])


def _rim(img, color):
    w, h = len(img[0]), len(img)
    rim = [(x, y) for y in range(h) for x in range(w) if img[y][x] == 0 and
           any(0 <= x + dx < w and 0 <= y + dy < h and img[y + dy][x + dx] not in (0, color)
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in rim:
        img[y][x] = color


CRACKLES = (['................',
             '................',
             '................',
             '................',
             '................',
             '....y...........',
             '.....y..y.......',
             '....y..y........',
             '.....yy..y......',
             '.......y.y......',
             '..y....lyy......',
             '...yy...ly......',
             '.....yyy.l......',
             '.........lW.....',
             '................',
             '................'],
            ['................',
             '................',
             '................',
             '................',
             '.......y........',
             '......y.........',
             '.......y........',
             '...y...y..y.....',
             '....y..y.y......',
             '.....y.yly......',
             '......yly.......',
             '..yyy..lly......',
             '.....yyyll......',
             '.........lW.....',
             '................',
             '................'])


def crackle_frames():
    """Two 16x16 frames of short zigzag strands going up and to the left from the
    lower right corner (the rim of a cheek): the cheek itself stays visible."""
    out = []
    for rows in CRACKLES:
        img = [[0] * 16 for _ in range(16)]
        stamp(img, 0, 0, rows, {'y': pika.SPARK, 'l': pika.SPARK_PALE, 'W': pika.WHITE}, clip=False)
        _rim(img, pika.SPARK_RIM)
        out.append(img)
    return out


def spark_frames():
    """Two 16x16 crackles like the game's battle sparks: white core, pale yellow,
    yellow, an orange rim (graphics/battle_anims/sprites/spark colours)."""
    out = []
    for rows in SPARKS:
        img = [[0] * 16 for _ in range(16)]
        stamp(img, 0, 0, rows, {'y': pika.SPARK, 'l': pika.SPARK_PALE, 'W': pika.WHITE}, clip=False)
        _rim(img, pika.SPARK_RIM)
        out.append(img)
    return out


BOLT_W, BOLT_H = 64, 32
# (main path from the cheek, right, to the ball, left; branches)
BOLTS = ((((61, 17), (52, 12), (45, 18), (35, 12), (26, 18), (16, 13), (4, 16)),
          (((45, 18), (41, 25)), ((26, 18), (22, 24)))),
         (((61, 17), (53, 22), (44, 14), (35, 20), (25, 12), (14, 18), (4, 15)),
          (((44, 14), (40, 7)), ((25, 12), (29, 6)))))


def _line(p, q):
    (x0, y0), (x1, y1) = p, q
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return {(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)}


def bolt_frames():
    """Two 64x32 frames of the zap from PIKACHU's cheek (right) to the ball (left):
    a 1 pixel white core, yellow round it, pale yellow at the bends, the orange rim,
    thinner toward the ball, two short forks."""
    out = []
    for path, forks in BOLTS:
        img = [[0] * BOLT_W for _ in range(BOLT_H)]
        core = set()
        for p, q in zip(path, path[1:]):
            core |= _line(p, q)
        fork = set()
        for p, q in forks:
            fork |= _line(p, q)
        for x, y in core:
            thick = 1 if x > 30 else 0
            for dx in range(-1, 2):
                for dy in range(-1 - thick, 2 + thick):
                    if 0 <= x + dx < BOLT_W and 0 <= y + dy < BOLT_H and img[y + dy][x + dx] == 0:
                        img[y + dy][x + dx] = pika.SPARK
        for x, y in fork:
            img[y][x] = pika.SPARK
        for x, y in path[1:-1]:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                img[y + dy][x + dx] = pika.SPARK_PALE
        for x, y in core:
            img[y][x] = pika.WHITE
        _rim(img, pika.SPARK_RIM)
        out.append(img)
    return out


# ---------------------------------------------------------------- the lab, two layers
VIEW_W, VIEW_H, VIEW_Y = 240, 96, 32      # the letterboxed picture: screen rows 32-127
MAP_W = 256                                # one 32x32 tile screen, wraps horizontally
# From FR/LG's lab tiles (gTileset_Lab / gTileset_Building palettes).
BG_PAL = [(0, 0, 0), (238, 238, 205), (222, 222, 180), (197, 197, 148), (255, 255, 255),
          (189, 197, 213), (139, 131, 148), (82, 82, 106), (205, 82, 65), (82, 148, 197),
          (222, 205, 106), (205, 230, 246), (156, 205, 139), (139, 197, 139), (106, 172, 115),
          (180, 172, 180)]
BG_PAL_BANK = 2                  # BG palette the tilemaps point at (src/intro_opening.c)
W_LIGHT, W_BASE, W_SHADE, S_WHITE, S_FACE, S_EDGE, S_DARK = 1, 2, 3, 4, 5, 6, 7
B_RED, B_BLUE, B_YELLOW, GLASS = 8, 9, 10, 11
T_LIGHT, T_BASE, T_SHADE, T_EDGE = 12, 13, 14, 15
DESK_TOP = 68                    # first row of the table, in picture rows
SHELF_X = 218                    # shelf's left edge on the back layer (x 212 on screen at the end)
CAM_END = 12                     # the camera trucks right this far over t 0-19
PIKA_WORLD = (156, 46)           # PIKACHU sprite corner, front layer coordinates
BALL_REST = (112, 78)            # ball centre while the hand holds it out (front layer)


def back_layer():
    """Wall with a window and its patch of morning light, a white metal lab shelf with
    books and a machine on the right. Soft: no outlines except the shelf's bottoms."""
    img = [[W_BASE] * MAP_W for _ in range(VIEW_H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(VIEW_H, y1)):
            for x in range(max(0, x0), min(MAP_W, x1)):
                img[y][x] = c
    # light from the window falling on the wall (a slanted patch, down and right)
    for y in range(8, 50):
        x0 = 30 + (y - 8) // 2
        rect(x0 + 50, y, x0 + 84, y + 1, W_LIGHT)
    # window: white frame, pale glass, a cross bar, a sill
    rect(22, 4, 76, 44, S_WHITE)
    rect(25, 7, 73, 41, GLASS)
    rect(48, 7, 50, 41, S_WHITE)
    rect(25, 23, 73, 25, S_WHITE)
    for k in range(10):                          # two shine streaks on the glass
        rect(29 + k, 36 - k * 2, 30 + k, 38 - k * 2, S_WHITE)
        rect(54 + k, 37 - k * 2, 55 + k, 38 - k * 2, S_WHITE)
    rect(20, 44, 78, 46, S_FACE)
    rect(20, 46, 78, 47, S_EDGE)
    # panelling
    rect(0, 52, MAP_W, 53, W_SHADE)
    rect(0, 53, MAP_W, DESK_TOP, W_SHADE)
    rect(0, 53, MAP_W, 54, W_BASE)
    for x in range(12, SHELF_X, 44):
        rect(x, 57, x + 32, 58, W_BASE)
        rect(x, 58, x + 1, 66, W_BASE)
    rect(0, DESK_TOP, MAP_W, VIEW_H, T_BASE)        # under the table (never seen)
    # shelf: white metal, grey faces, dark bottoms, short saturated books, one machine
    rect(SHELF_X, 0, MAP_W, DESK_TOP, S_WHITE)
    rect(SHELF_X, 0, SHELF_X + 2, DESK_TOP, S_FACE)
    widths = (4, 5, 3, 4, 5, 4, 3, 5, 4, 4)
    books = (B_RED, B_BLUE, B_YELLOW, B_BLUE, B_RED, B_YELLOW, B_BLUE, T_BASE)
    for r, (top, bottom) in enumerate(((4, 20), (24, 40), (44, 62))):
        rect(SHELF_X + 3, top, MAP_W, bottom, S_FACE)
        x, i = SHELF_X + 4, r * 3
        while x < MAP_W - 2:
            if r == 1 and x > SHELF_X + 30:          # the machine: a grey box with lights
                rect(x, top + 3, x + 24, bottom, S_EDGE)
                rect(x + 1, top + 4, x + 23, bottom - 1, S_FACE)
                rect(x + 3, top + 6, x + 12, top + 11, S_DARK)
                rect(x + 4, top + 7, x + 11, top + 10, GLASS)
                for k, c in enumerate((B_RED, B_BLUE, T_BASE)):
                    rect(x + 15 + k * 3, top + 7, x + 17 + k * 3, top + 9, c)
                rect(x + 3, bottom - 4, x + 21, bottom - 3, S_EDGE)
                x += 26
                continue
            w = widths[i % len(widths)]
            c = books[(i * 3 + r) % len(books)]
            h = bottom - top - 3 - (i * 7 + r * 5) % 3
            rect(x, bottom - h, x + w, bottom, c)
            rect(x + w - 1, bottom - h, x + w, bottom, S_EDGE)
            x += w + (1 if i % 4 == 3 else 0)
            i += 1
        rect(SHELF_X + 3, bottom, MAP_W, bottom + 1, S_DARK)
    return img


def front_layer():
    """The lab table: a green top with a lit back edge, a white front rim, PIKACHU's
    shadow. Everything above the table is clear (the back layer shows through)."""
    img = [[0] * MAP_W for _ in range(VIEW_H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(VIEW_H, y1)):
            for x in range(max(0, x0), min(MAP_W, x1)):
                img[y][x] = c
    rect(0, DESK_TOP, MAP_W, DESK_TOP + 1, T_SHADE)
    rect(0, DESK_TOP + 1, MAP_W, DESK_TOP + 3, T_LIGHT)
    rect(0, DESK_TOP + 3, MAP_W, VIEW_H - 7, T_BASE)
    for y, x0, x1 in ((75, 10, 70), (80, 96, 150), (85, 20, 60), (78, 200, 250), (86, 170, 226)):
        rect(x0, y, x1, y + 1, T_LIGHT)
    rect(0, VIEW_H - 7, MAP_W, VIEW_H - 6, T_SHADE)
    rect(0, VIEW_H - 6, MAP_W, VIEW_H - 4, S_WHITE)
    rect(0, VIEW_H - 4, MAP_W, VIEW_H, T_EDGE)
    sx, sy = PIKA_WORLD[0] + 30, PIKA_WORLD[1] + 60 - VIEW_Y
    for y in range(VIEW_H):
        for x in range(MAP_W):
            if ((x + 0.5 - sx) / 18) ** 2 + ((y + 0.5 - sy) / 3) ** 2 <= 1 and img[y][x] in (T_BASE, T_LIGHT):
                img[y][x] = T_SHADE
    return img


# ---------------------------------------------------------------- the close-up background
def closeup_layer():
    """The close-up's backdrop: wide diagonal bands of pale sky and white (they scroll
    slowly sideways so the picture never stands still). 32 pixel period, so the
    256 pixel map wraps without a seam."""
    return [[GLASS if ((x + y) // 16) % 2 else S_WHITE for x in range(MAP_W)] for y in range(VIEW_H)]


# ---------------------------------------------------------------- choreography
FRAMES = 76                      # F842-917 = bar 2 of MUS_INTRO_FIGHT (19.15 frames a beat)
TRACKS = ('pikachu', 'sleeve', 'hand', 'ball', 'smoke', 'spark_cheek', 'spark_ball', 'bolt',
          'bust0', 'bust1', 'bust2', 'bust3')
BUST_TRACKS = TRACKS[-4:]        # the 2x close-up, 128x128 as four 64x64 quarters
HIDE, FRONT = 1, 2               # key flags: not drawn / drawn in front of the arm
HAND_HOLD, HAND_OPEN = 1, 2      # frames of arm.png (0 is the sleeve half)
BURST, CRACKLE = 0, 2            # first frames of the two effects in spark.png
T_SNAP, T_POP = 19, 24           # beat 2: the ball opens and PIKACHU turns; the ball is hit
T_CU = 48                        # half a beat before beat 4: cut to the close-up
T_HMPH, T_CRACKLE2 = 57, 66      # beat 4: "hmph!"; the second crackle
DESK_Y = 112                     # ball centre on the table (screen row, in front of the arm)
CHEEK_WORLD = (170, 60)          # crackle sprite corner at PIKACHU's near cheek (poses C)
BUST_AT = (58, 30)               # close-up corner on screen at the cut
BUST_CHEEK = (37, 40)            # crackle corner relative to the close-up's corner
SHAKE = {23: 1, 24: -1, 25: 1}   # the hit: screen shake, 1 pixel, no change of brightness
LAYOUT_LAB, LAYOUT_CLOSEUP = 0, 1


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_in(p):
    return p ** 3


def lerp(a, b, p):
    return a + (b - a) * p


def camera(t):
    """Camera x (front layer scroll) at frame t: a slow truck right while the arm
    comes in, from the ball in the middle to PIKACHU on the right third."""
    return round(CAM_END * ease_out(min(1, (t + 1) / 20)))


def ball_path():
    """Ball centre (front layer) and frame for each frame from the pop: knocked up and
    to the left, first bounce on the table on beat 3 (left of the sleeve), a second
    smaller one, then it rolls toward the left edge."""
    x, y = BALL_REST[0] + 4, BALL_REST[1] - 2
    vx, vy, g = -3.6, -4.0, 0.85
    out, spin, bounces = {}, 0.0, 0
    for t in range(T_POP, FRAMES):
        out[t] = (x, y, BALL_ROLL[int(spin) % 4], bounces)
        x += vx
        vy += g
        y += vy
        if y >= DESK_Y and vy > 0:
            y = DESK_Y
            bounces += 1
            if bounces < 3:
                vy, vx = -vy * 0.45, vx * 0.85
            else:
                vy = g = 0.0
        spin += abs(vx) / 4.5
    return out


def pikachu_track(t):
    """Frame name and y offset for PIKACHU at frame t (wide shot)."""
    breathe = -1 if (t // 8) % 2 else 0
    if t < 8 or 11 <= t < 14:
        return 'A', breathe
    if t < 11:
        return 'A_twitch', breathe
    if t < T_SNAP:
        return 'A_sus', 0
    if t == T_SNAP:
        return 'MID', -1
    if t < T_SNAP + 3:
        return 'B', -2
    if t < 25:
        return 'C_over', -1
    if 38 <= t < 41:
        return 'C_flick', 0                      # the tail slaps as the ball lands
    return 'C', breathe if t >= 28 else 0


def bust_track(t):
    """Close-up frame (0 sulk, 1 "hmph") and offset: a slow push in, breathing, the
    chin raised on beat 4."""
    push = (t - T_CU) // 7                       # 0..3: the camera creeps closer
    breathe = -1 if ((t - T_CU) // 8) % 2 else 0
    if T_HMPH <= t < T_HMPH + 5:
        return 1, -push, -2 - push // 2
    return 0, -push, breathe - push // 2


def choreography():
    """keys[t][track] = (x, y, frame, flags) on screen; scroll[t] = (back x, back y,
    front x, front y) for BG3 and BG2; layout[t] = which backgrounds show."""
    bx, by = ball_on_hand()
    ax0, ay0 = BALL_REST[0] - bx - 8, BALL_REST[1] - by - 8    # arm corner at rest
    path = ball_path()
    keys, scroll, layout = [], [], []
    hidden = (0, 0, 0, HIDE)
    for t in range(FRAMES):
        k = {}
        if t >= T_CU:
            # the close-up: PIKACHU's head and chest twice as large, bands behind
            layout.append(LAYOUT_CLOSEUP)
            scroll.append(((t - T_CU) // 2, 0, 0, 0))
            for tr in TRACKS:
                k[tr] = hidden
            frame, dx, dy = bust_track(t)
            x0, y0 = BUST_AT[0] + dx, BUST_AT[1] + dy
            for q, tr in enumerate(BUST_TRACKS):
                k[tr] = (x0 + (q % 2) * 64, y0 + (q // 2) * 64, frame, 0)
            for t0, n in ((T_HMPH, 5), (T_CRACKLE2, 5)):
                if t0 <= t < t0 + n:
                    lift = -2 if frame == 1 else 0
                    k['spark_cheek'] = (x0 + BUST_CHEEK[0], y0 + BUST_CHEEK[1] + lift,
                                        CRACKLE + (t - t0) // 2 % 2, 0)
            keys.append(k)
            continue
        layout.append(LAYOUT_LAB)
        cam = camera(t)
        sx = SHAKE.get(t, 0)
        bump = 1 if path.get(t, (0, 0, 0, 0))[3] == 1 and path.get(t - 1, (0, 0, 0, 0))[3] == 0 else 0
        scroll.append((cam // 2 - sx, 0, cam - sx, bump))

        def screen(wx, wy):
            return round(wx - cam + sx), round(wy)
        name, dy = pikachu_track(t)
        k['pikachu'] = screen(PIKA_WORLD[0], PIKA_WORLD[1] + dy) + (PIKA_FRAMES.index(name), 0)
        # the arm: in from the lower left, a nudge ("here"), a flinch when the ball is
        # knocked away, then it withdraws
        if t < 14:
            p = ease_out((t + 1) / 14)
            dx, dy = lerp(-70, 0, p), lerp(42, 0, p)
        elif t < T_SNAP:
            p = min(1, (t - 13) / 4)
            dx, dy = lerp(0, 4, p), lerp(0, -2, p)
        elif t < T_POP:
            dx, dy = 4, -2
        elif t < T_POP + 5:
            p = ease_out((t - T_POP + 1) / 5)
            dx, dy = lerp(4, -4, p), lerp(-2, 3, p)
        else:
            p = ease_in(min(1, (t - T_POP - 4) / 11))
            dx, dy = lerp(-4, -90, p), lerp(3, 64, p)
        gone = HIDE if t >= T_POP + 15 else 0
        ax, ay = screen(ax0 + dx, ay0 + dy)
        k['sleeve'] = (ax, ay, 0, gone)
        k['hand'] = (ax + 64, ay, HAND_HOLD if t < T_POP else HAND_OPEN, gone)
        # the ball: in the hand (behind the fingers), opening from the snap, then flying
        if t < T_POP:
            k['ball'] = (ax + bx, ay + by, BALL_OPENING if t >= T_SNAP else 0, 0)
        else:
            x, y, frame, _ = path[t]
            px, py = screen(x - 7.5, y - 7.5)
            k['ball'] = (px, py, frame, FRONT | (HIDE if px < -16 else 0))
        # a puff where the ball was hit
        if T_POP <= t < T_POP + 4:
            hx, hy = screen(ax0 + 4 + bx, ay0 - 2 + by)
            k['smoke'] = (hx, hy - (t - T_POP), SMOKE_FIRST + (t - T_POP) // 2, FRONT)
        else:
            k['smoke'] = hidden
        # sparks: on the ball first (the warning), then the hit
        k['spark_ball'] = hidden
        if T_SNAP + 1 <= t < T_SNAP + 3:
            k['spark_ball'] = (k['ball'][0], k['ball'][1], BURST + (t - T_SNAP) % 2, FRONT)
        elif T_POP <= t < T_POP + 4:
            k['spark_ball'] = (k['ball'][0], k['ball'][1], BURST + (t - T_POP + 1) // 2 % 2, FRONT)
        # crackle off the cheek while the bolt flies
        k['spark_cheek'] = hidden
        if 22 <= t < 28:
            cx, cy = screen(*CHEEK_WORLD)
            k['spark_cheek'] = (cx, cy, CRACKLE + (t - 22) // 2 % 2, 0)
        # the bolt, cheek to ball, four frames
        if 22 <= t < 26:
            bxs, bys = screen(BALL_REST[0] + 3, BALL_REST[1] - 18)
            k['bolt'] = (bxs, bys, t % 2, FRONT)
        else:
            k['bolt'] = hidden
        for tr in BUST_TRACKS:
            k[tr] = hidden
        keys.append(k)
    return keys, scroll, layout


# ---------------------------------------------------------------- output
def bust_quarters():
    """The close-up frames cut into four 64x64 quarters: quarters[q] = [sulk, hmph]."""
    cu = pika.closeup_frames()
    frames = [cu['CU'], cu['CU_hmph']]
    return [[[row[(q % 2) * 64:(q % 2) * 64 + 64] for row in f[(q // 2) * 64:(q // 2) * 64 + 64]]
             for f in frames] for q in range(4)]


def art():
    """Every sprite frame, by track (frame numbers as in the key table)."""
    poses = pika.frames()
    hold, opened = arm('hold'), arm('open')
    sleeve = [r[:64] for r in hold]
    balls = ball_frames()
    sparks = spark_frames() + crackle_frames()
    out = {'pikachu': ([poses[n] for n in PIKA_FRAMES], PIKA_PAL),
           'sleeve': ([sleeve], PROP_PAL),
           'hand': ([sleeve, [r[64:] for r in hold], [r[64:] for r in opened]], PROP_PAL),
           'ball': (balls, PROP_PAL),
           'smoke': (balls, PROP_PAL),
           'spark_cheek': (sparks, PIKA_PAL),
           'spark_ball': (sparks, PIKA_PAL),
           'bolt': (bolt_frames(), PIKA_PAL)}
    for q, frames in enumerate(bust_quarters()):
        out[BUST_TRACKS[q]] = (frames, PIKA_PAL)
    return out


def mask_of(im):
    return Image.frombytes('L', im.size, bytes(255 if v else 0 for v in im.getdata()))


def render_frame(k, sc, lay, layers, sheets):
    """The 240x160 screen for one frame of the table, the way the game draws it:
    BG3 (back), BG2 (front, colour 0 clear), then the sprites back to front."""
    back, front, closeup = layers
    screen = Image.new('RGB', (240, 160), (0, 0, 0))
    bx, by, fx, fy = sc
    shown = ((closeup, bx, by),) if lay == LAYOUT_CLOSEUP else ((back, bx, by), (front, fx, fy))
    for layer, lx, ly in shown:
        for y in range(VIEW_H):
            for x in range(240):
                v = layer[y + ly][(x + lx) % MAP_W] if 0 <= y + ly < VIEW_H else 0
                if v:
                    screen.putpixel((x, y + VIEW_Y), BG_PAL[v])

    def put(track):
        x, y, frame, flags = k[track]
        if flags & HIDE:
            return
        frames, pal = sheets[track]
        im = to_image(frames[frame], pal)
        screen.paste(im.convert('RGB'), (x, y), mask_of(im))
    front_ball = k['ball'][3] & FRONT
    order = list(BUST_TRACKS) + ['pikachu'] + ([] if front_ball else ['ball']) + ['sleeve', 'hand'] + \
        (['ball'] if front_ball else []) + ['smoke', 'bolt', 'spark_ball', 'spark_cheek']
    for track in order:
        put(track)
    black = Image.new('RGB', (240, VIEW_Y), (0, 0, 0))
    screen.paste(black, (0, 0))
    screen.paste(black, (0, VIEW_Y + VIEW_H))
    return screen


def strip(frames, pal):
    """Frames stacked top to bottom: the 1D OBJ tile order the game loads."""
    rows = [r for f in frames for r in f]
    return to_image(rows, pal)


def tiles_and_maps(layers, bank):
    """Cut the layers (256x96 each) into one shared set of 8x8 tiles (flipped copies
    reused; tile 0 empty) and one 32x32 tilemap per layer, rows 4-15 holding the
    picture (screen rows 32-127)."""
    def flip(t, h, v):
        return tuple(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))
    uniq = [tuple([0] * 64)]
    index = {uniq[0]: 0}
    maps = []
    for img in layers:
        entries = [0] * (32 * 32)
        for ty in range(VIEW_H // 8):
            for tx in range(MAP_W // 8):
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
                entries[(ty + VIEW_Y // 8) * 32 + tx] = entry | (bank << 12)
        maps.append(entries)
    per_row = 16
    rows = (len(uniq) + per_row - 1) // per_row
    sheet = [[0] * (per_row * 8) for _ in range(rows * 8)]
    for i, t in enumerate(uniq):
        r, c = divmod(i, per_row)
        for k, v in enumerate(t):
            sheet[r * 8 + k // 8][c * 8 + k % 8] = v
    return sheet, maps, len(uniq)


def write_header(keys, scroll, layout, path):
    lines = ['// Generated by tools/make_intro_opening_scene2.py. Do not edit: change the',
             '// choreography there and run it again.',
             '// Scene 2 of the opening, one row per frame (set up at F842-917, seen at',
             '// F843-918): for each sprite track {x, y, frame, flags}, x and y the corner',
             '// of the sprite on screen; the scroll of the back (BG3) and front (BG2)',
             '// layers; which backgrounds show (0 the lab, 1 the close-up).',
             '',
             '#define SCENE2_FRAMES %d' % FRAMES,
             '',
             'enum {']
    lines += ['    SCENE2_TRACK_%s,' % t.upper() for t in TRACKS]
    lines += ['    SCENE2_TRACK_COUNT', '};', '',
              'static const struct OpeningKey sScene2_Keys[SCENE2_FRAMES][SCENE2_TRACK_COUNT] = {']
    for t, k in enumerate(keys):
        lines.append('    [%d] = {%s},' % (t, ', '.join('{%d, %d, %d, %d}' % k[tr] for tr in TRACKS)))
    lines += ['};', '', 'static const struct OpeningScroll sScene2_Scroll[SCENE2_FRAMES] = {']
    for t, s in enumerate(scroll):
        lines.append('    [%d] = {%d, %d, %d, %d},' % ((t,) + s))
    lines += ['};', '', 'static const u8 sScene2_Layout[SCENE2_FRAMES] = {']
    for i in range(0, FRAMES, 19):
        lines.append('    ' + ', '.join(str(v) for v in layout[i:i + 19]) + ',')
    lines += ['};', '']
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None, help='also write mock-ups of every frame here')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sheets = art()
    layers = (back_layer(), front_layer(), closeup_layer())
    tiles, maps, n = tiles_and_maps(layers, BG_PAL_BANK)
    to_image(tiles, BG_PAL).save(OUT + '/bg.png')
    for name, m in zip(('bg_back', 'bg_front', 'bg_closeup'), maps):
        with open(OUT + '/%s.bin' % name, 'wb') as f:
            f.write(struct.pack('<%dH' % len(m), *m))
    strip(sheets['pikachu'][0], PIKA_PAL).save(OUT + '/pikachu.png')
    strip(sheets['hand'][0], PROP_PAL).save(OUT + '/arm.png')
    strip(sheets['ball'][0], PROP_PAL).save(OUT + '/ball.png')
    strip(sheets['spark_cheek'][0], PIKA_PAL).save(OUT + '/spark.png')
    strip(sheets['bolt'][0], PIKA_PAL).save(OUT + '/bolt.png')
    strip([f for q in bust_quarters() for f in q], PIKA_PAL).save(OUT + '/closeup.png')
    keys, scroll, layout = choreography()
    write_header(keys, scroll, layout, HEADER)
    print('scene 2: %d background tiles, %d frames' % (n, len(keys)))
    if a.preview:
        os.makedirs(a.preview + '/mock', exist_ok=True)
        for t in range(FRAMES):
            render_frame(keys[t], scroll[t], layout[t], layers, sheets).save('%s/mock/t%02d.png' % (a.preview, t))


if __name__ == '__main__':
    main()
