#!/usr/bin/env python3
"""Draw and time scene 2 of the new opening: "the PIKACHU that hates POKe BALLS".

docs/anim/opening-storyboard.md 3.3, scene 2 (F842-917, 76 frames, bar 2 of
MUS_INTRO_FIGHT): in OAK's lab the professor's forearm (sleeve and hand only, no face)
holds out a POKe BALL; the ball starts to open and PIKACHU snaps its head away on
beat 2; a spark from its cheek knocks the ball out of the hand; the ball bounces on the
desk (beat 3) and rolls off; PIKACHU sulks, cheeks crackling (beat 4).

Everything is drawn by rule here (tools/intro_opening_art.py). Nothing is traced or
copied from the anime:

- PIKACHU is built in the palette of its FR/LG front sprite
  (graphics/pokemon/pikachu/normal.pal) with FR/LG's coloured outlines and upper-left
  light, proportioned after the front sprite, the partner PIKACHU and the title screen
  PIKACHU. Poses: A looks at the ball, B the snap (a squeezed smear frame), C turned
  away, arms folded, "hmph". This is the model for the PIKACHU of the later scenes.
- The forearm, ball and sparks share one palette: the thrown POKe BALL's colours in
  the slots graphics/interface/ball/poke.png uses (its frames are used as they are),
  a white lab coat with grey shading, FR/LG overworld skin tones, spark yellows.
- The lab is a soft wall and bookshelf without outlines and a wooden desk, so the
  sprites read in front of it. The picture is 240x96: the intro keeps FR/LG's
  letterbox (the GAME FREAK scene opens it and the original fight kept it).

The timing lives here too: choreography() gives every sprite's position and frame for
each of the 76 frames. The game plays that table back (src/data/intro_opening_scene2.h),
so the previews and the game agree.

Writes graphics/intro/opening/scene2/{bg.png,bg.bin,pikachu.png,arm.png,props.png}
and src/data/intro_opening_scene2.h. With --preview DIR it also writes the model
sheets and a mock-up of every frame (DIR/mock/tNN.png, as the game should draw it).
"""
import argparse
import math
import os
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intro_opening_art import Figure, stamp, to_image, enlarge, flat_palette  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = ROOT + '/graphics/intro/opening/scene2'
HEADER = ROOT + '/src/data/intro_opening_scene2.h'

# ---------------------------------------------------------------- PIKACHU
# 1-6 and 10-14 are graphics/pokemon/pikachu/normal.pal
PIKA_PAL = [(0, 0, 0), (255, 255, 255), (255, 255, 123), (255, 238, 0), (238, 189, 0),
            (197, 139, 0), (131, 82, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (255, 74, 74), (230, 0, 0), (180, 0, 0), (106, 106, 106), (16, 16, 16), (0, 0, 0)]
CLEAR, WHITE, LIGHT, YELLOW, MID, DARK, BROWN = 0, 1, 2, 3, 4, 5, 6
PINK, RED, DRED, GREY, BLACK = 10, 11, 12, 13, 14

PIKA_COLORS = {
    'Y': dict(base=YELLOW, rim=BROWN, line=DARK, light=LIGHT, mid=MID, no_line_over=('K',)),
    'K': dict(base=BLACK, rim=BLACK),
    'B': dict(base=DARK, rim=BROWN, line=BROWN),        # the brown root of the tail
}
KEY = {'K': BLACK, 'W': WHITE, 'o': BROWN, 'r': RED, 'R': DRED, 'p': PINK, 'm': DRED, 't': PINK}
PS = 64


def ear(f, name, ex, ey, rot, length=10.5, width=3.5):
    """An ear: a long ellipse around (ex, ey) tilted by rot, its far end black."""
    pts = f.ellipse(name, ex, ey, width, length, rot=rot)
    ux, uy = math.sin(rot), -math.cos(rot)
    f.pixels(name + 'tip', [(x, y) for x, y in pts
                            if (x + 0.5 - ex) * ux + (y + 0.5 - ey) * uy > length * 0.3], kind='K')


def cheek(img, x, y, w):
    rows = {5: ['.rrr.', 'prrrr', 'rrrrR', '.rRR.'],
            3: ['.r.', 'prR', 'rR.']}[w]
    stamp(img, x, y, rows, KEY)


def pikachu(d, arms, eyes, mouth, hx=29, hy=24, squash=1.0):
    """PIKACHU sitting on the desk, feet forward, tail rising behind on the right.
    d: where the face turns, -1 three quarters left, 0 front, 1 three quarters right."""
    stamp.rims = (BROWN,)
    f = Figure(PS, PS)
    f.poly('tail', [(37, 52), (45, 46), (42, 42), (52, 35), (48, 31), (58, 20), (63, 24),
                    (57, 33), (60, 36), (51, 44), (54, 47), (42, 57)])
    f.poly('tailroot', [(37, 52), (44, 47), (47, 51), (42, 57)], kind='B')
    f.ellipse('body', 30, 45, 12.5, 11)
    f.ellipse('hips', 30, 52.5, 14, 6.5)
    f.merged('body', 'hips')
    f.ellipse('footL', 21, 58.5, 5, 3)
    f.ellipse('footR', 37.5, 59, 5, 3)
    if arms == 'side':
        f.ellipse('armL', 19, 45, 2.6, 5, rot=0.6)
        f.ellipse('armR', 41, 45, 2.6, 5, rot=-0.6)
    elif arms == 'up':                           # startled, paws up
        f.ellipse('armL', 19, 40, 2.6, 4.8, rot=1.0)
        f.ellipse('armR', 41, 40, 2.6, 4.8, rot=-1.0)
    elif arms == 'crossed':
        f.ellipse('armR', 32.5, 42.5, 7, 2.6, rot=0.42)
        f.ellipse('armL', 27.5, 42.5, 7, 2.6, rot=-0.42)
    tilt = 0.12 * d
    ear(f, 'ear0', hx - 10.5 + 1.5 * d, hy - 13.5, -0.50 + tilt)
    ear(f, 'ear1', hx + 10.5 + 1.5 * d, hy - 13.5, 0.50 + tilt)
    for n in ('ear0', 'ear1'):
        f.clip(n, lambda x, y: y < hy - 5)      # the roots stay hidden in the head
    f.ellipse('head', hx - 1.5 * d, hy, 13.5 * squash, 10.5)
    f.ellipse('jowl', hx - 0.5 * d, hy + 4, 14.5 * squash, 7.2)
    if d:
        f.ellipse('muzzle', hx + 11 * d, hy + 4, 4.5, 4)
    for a in ('head', 'jowl', 'muzzle'):
        for b in ('body', 'hips', 'head', 'jowl', 'muzzle'):
            if a != b:
                f.merge.add(frozenset((a, b)))
    img = f.render(PIKA_COLORS)
    fx = hx + round(6 * d)                       # middle of the face
    near, far = (fx - 6, fx + 5) if d > 0 else (fx + 5, fx - 6)
    if eyes == 'open':                           # black, a white glint up and to the left
        stamp(img, near - 1, hy - 2, ['.KK.', 'KWKK', 'KKKK', '.KK.'], KEY)
        if d:
            rows = ['.KK', 'KWK', 'KKK', '.KK'] if d < 0 else ['KK.', 'KWK', 'KKK', 'KK.']
            stamp(img, far - (1 if d > 0 else 0), hy - 2, rows, KEY)
        else:
            stamp(img, far - 1, hy - 2, ['.KK.', 'KWKK', 'KKKK', '.KK.'], KEY)
    elif eyes == 'squeeze':                      # > <
        stamp(img, fx - 8, hy - 2, ['KK..', '..KK', 'KK..'], KEY)
        stamp(img, fx + 4, hy - 2, ['..KK', 'KK..', '..KK'], KEY)
    elif eyes == 'shut':
        stamp(img, near - 2, hy - 1, ['K...', '.KKK'] if d > 0 else ['...K', 'KKK.'], KEY)
        stamp(img, far - 1, hy - 1, ['K..', '.KK'] if d > 0 else ['..K', 'KK.'], KEY)
    nose = fx + (d > 0) - (d < 0)
    stamp(img, nose, hy + 2, ['K'], KEY)
    if mouth == 'smile':
        stamp(img, nose - 3, hy + 4, ['o..o..o', '.oo.oo.'], KEY)
    elif mouth == 'open':
        stamp(img, nose - 2, hy + 4, ['ooooo', 'omtmo', '.ooo.'], KEY)
    elif mouth == 'pout':
        stamp(img, nose - 2 + d, hy + 4, ['.ooo.', 'o...o'], KEY)
    # cheeks: the near one whole, the far one cut off by the rim of the head
    cy = hy + 3
    if d < 0:
        cheek(img, fx + 8, cy, 5)
        cheek(img, fx - 13, cy, 3)
    elif d > 0:
        cheek(img, fx - 12, cy, 5)
        cheek(img, fx + 11, cy, 3)
    else:
        cheek(img, fx - 14, cy, 5)
        cheek(img, fx + 10, cy, 5)
    return img


def pikachu_poses():
    return {
        'A': pikachu(-1, 'side', 'open', 'smile'),                  # looks at the ball
        'B': pikachu(0, 'up', 'squeeze', 'open', squash=0.9),       # the snap: a squeezed smear
        'C': pikachu(1, 'crossed', 'shut', 'pout'),                 # turned away, "hmph"
    }


# ---------------------------------------------------------------- forearm, ball, sparks
PROP_PAL = [(0, 0, 0), (131, 0, 0), (172, 0, 0), (213, 41, 41), (255, 156, 123), (255, 255, 255),
            (148, 148, 148), (65, 65, 65), (24, 24, 24), (213, 213, 230), (255, 222, 189),
            (246, 189, 148), (222, 148, 115), (148, 82, 65), (255, 230, 57), (255, 255, 172)]
P_WHITE, P_GREY, P_DGREY, P_BLACK, P_COAT = 5, 6, 7, 8, 9
P_SKIN_L, P_SKIN, P_SKIN_S, P_SKIN_O = 10, 11, 12, 13
P_SPARK, P_SPARK_L = 14, 15
PROP_COLORS = {
    'C': dict(base=P_WHITE, rim=P_DGREY, line=P_GREY, light=P_WHITE, mid=P_COAT),
    'S': dict(base=P_SKIN, rim=P_SKIN_O, line=P_SKIN_S, light=P_SKIN_L, mid=P_SKIN_S),
}
BALL_PNG = ROOT + '/graphics/interface/ball/poke.png'
ARM_W, ARM_H = 128, 64          # two 64x64 sprites side by side
ARM_ANGLE = -0.58               # the forearm rises to the right
ARM_CUFF = (74, 24)             # middle of the cuff on the arm canvas


def _along(t, s):
    """Point t pixels along the forearm from the cuff and s pixels across it
    (positive s = the underside)."""
    c, sn = math.cos(ARM_ANGLE), math.sin(ARM_ANGLE)
    return (ARM_CUFF[0] + t * c - s * sn, ARM_CUFF[1] + t * sn + s * c)


def ball_centre():
    """Where the ball's centre sits on the arm canvas while the hand holds it:
    straight above the palm."""
    px, py = _along(12, -1)
    return px, py - 10


def ball_on_hand():
    """Corner of the 16x16 ball sprite while the hand holds it (the game's ball is
    12 pixels across, rows and columns 2-13 of its sprite)."""
    bx, by = ball_centre()
    return round(bx - 7.5), round(by - 7.5)


def arm(grip='hold'):
    """The professor's forearm reaching in from the lower left in a white lab coat
    sleeve (long enough to leave the picture), a cuff and the hand, palm up.
    'hold': fingers and thumb cup the ball (the hand is drawn over the ball);
    'open': the hand springs open when the spark knocks the ball away."""
    stamp.rims = ()
    f = Figure(ARM_W, ARM_H)
    f.poly('sleeve', [_along(-130, -12), _along(-2, -11), _along(1, -8), _along(1, 8),
                      _along(-2, 11), _along(-130, 13)], kind='C')
    cx, cy = _along(0, 0)
    f.ellipse('cuff', cx, cy, 3, 10.5, kind='C', rot=ARM_ANGLE)
    f.poly('wrist', [_along(1, -4.5), _along(8, -5), _along(8, 4), _along(1, 4.5)], kind='S')
    px, py = _along(12, -1)
    f.ellipse('palm', px, py, 8.5, 4.5, kind='S', rot=ARM_ANGLE)
    bx, by = ball_centre()
    if grip == 'hold':
        f.ellipse('fingers', bx + 5.5, by + 3, 2.8, 5.5, kind='S', rot=-0.3)
        f.ellipse('thumb', bx - 5.5, by + 4, 2.2, 4.2, kind='S', rot=0.5)
    else:
        f.ellipse('fingers', bx + 7, by + 2, 2.6, 6, kind='S', rot=0.6)
        f.ellipse('thumb', bx - 6.5, by + 4.5, 2.2, 4.5, kind='S', rot=-0.6)
    f.merged('wrist', 'palm')
    img = f.render(PROP_COLORS)
    # soft folds across the sleeve
    for t, s0, s1 in ((-40, -9, 1), (-33, -4, 6), (-12, 2, 9), (-6, -9, -3)):
        for k in range(s0 * 2, s1 * 2 + 1):
            x, y = _along(t + k * 0.35, k * 0.5)
            if 0 <= int(x) < ARM_W and 0 <= int(y) < ARM_H and img[int(y)][int(x)] == P_WHITE:
                img[int(y)][int(x)] = P_COAT
    # the curled fingers seen from the back: a crease between each
    if grip == 'hold':
        for dy in (-2, 0, 2):
            for dx in (0, 1):
                x, y = round(bx + 5 + dx), round(by + 2 + dy)
                if img[y][x] in (P_SKIN, P_SKIN_L):
                    img[y][x] = P_SKIN_S
    return img


def ball_frames():
    """16x16: the game's thrown POKe BALL, the same turned 90/180/270 degrees
    (rolling), and the game's 'opening' frame."""
    src = Image.open(BALL_PNG)
    still = src.crop((0, 0, 16, 16))
    opening = src.crop((0, 16, 16, 32))
    frames = [still, still.transpose(Image.ROTATE_270), still.transpose(Image.ROTATE_180),
              still.transpose(Image.ROTATE_90), opening]
    return [[[fr.getpixel((x, y)) for x in range(16)] for y in range(16)] for fr in frames]


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


def spark_frames():
    """Two 16x16 crackles: a white core, pale yellow, a yellow zigzag, and a dark
    orange rim so they read on PIKACHU's yellow as well as on the shelves."""
    out = []
    for rows in SPARKS:
        img = [[0] * 16 for _ in range(16)]
        stamp(img, 0, 0, rows, {'y': P_SPARK, 'l': P_SPARK_L, 'W': P_WHITE}, clip=False)
        rim = [(x, y) for y in range(16) for x in range(16) if img[y][x] == 0 and
               any(0 <= x + dx < 16 and 0 <= y + dy < 16 and img[y + dy][x + dx]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in rim:
            img[y][x] = P_SKIN_O
        out.append(img)
    return out


BOLT_W, BOLT_H = 64, 32
BOLT_PATHS = (((61, 17), (50, 12), (44, 19), (33, 13), (25, 20), (15, 14), (3, 17)),
              ((61, 17), (52, 21), (43, 13), (35, 20), (24, 12), (14, 19), (3, 16)))


def bolt_frames():
    """Two 64x32 frames of the zap from PIKACHU's cheek (right end) to the ball (left
    end): a jagged white line inside pale yellow, yellow and the dark orange rim."""
    out = []
    for path in BOLT_PATHS:
        img = [[0] * BOLT_W for _ in range(BOLT_H)]
        core = set()
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(n + 1):
                core.add((round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)))

        def grow(pts):
            return pts | {(x + dx, y + dy) for x, y in pts for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if 0 <= x + dx < BOLT_W and 0 <= y + dy < BOLT_H}
        pale = grow(core)
        yellow = grow(pale)
        rim = grow(yellow)
        for pts, c in ((rim, P_SKIN_O), (yellow, P_SPARK), (pale, P_SPARK_L), (core, P_WHITE)):
            for x, y in pts:
                img[y][x] = c
        out.append(img)
    return out


# ---------------------------------------------------------------- the lab
VIEW_W, VIEW_H, VIEW_Y = 240, 96, 32      # the letterboxed picture: screen rows 32-127
BG_PAL = [(0, 0, 0), (238, 228, 196), (214, 200, 164), (186, 170, 136), (112, 78, 56),
          (146, 104, 72), (176, 132, 92), (120, 150, 148), (96, 122, 124), (170, 114, 104),
          (140, 92, 86), (184, 166, 110), (230, 172, 106), (205, 142, 80), (160, 104, 60),
          (112, 70, 42)]
BG_PAL_BANK = 2                  # BG palette the tilemap points at (src/intro_opening.c)
W_LIGHT, W_MID, W_DARK, WOOD_D, WOOD_M, WOOD_L = 1, 2, 3, 4, 5, 6
BOOKS = ((7, 8), (9, 10), (11, 3), (6, 5), (7, 8), (11, 3), (9, 10))
DESK_L, DESK, DESK_D, DESK_E = 12, 13, 14, 15
DESK_TOP = 68                    # first row of the desk, in picture rows
SHELF_X = 124
PIKA_POS = (144, 46)             # PIKACHU sprite corner on screen
BALL_REST = (100, 78)            # ball centre on screen while the hand holds it out


def arm_rest():
    """Arm sprite corner on screen when it holds the ball out."""
    bx, by = ball_on_hand()
    return BALL_REST[0] - bx - 8, BALL_REST[1] - by - 8


def background():
    """Soft, outline-free lab wall with a bookshelf, and the desk PIKACHU sits on."""
    img = [[W_LIGHT] * VIEW_W for _ in range(VIEW_H)]

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(VIEW_H, y1)):
            for x in range(max(0, x0), min(VIEW_W, x1)):
                img[y][x] = c
    # wall: faint panel seams, a rail and the lower panelling
    for x in range(8, SHELF_X, 38):
        rect(x, 0, x + 1, 50, W_MID)
    rect(0, 50, SHELF_X, 51, W_MID)
    rect(0, 51, SHELF_X, 53, W_DARK)
    rect(0, 53, SHELF_X, DESK_TOP, W_MID)
    for x in range(20, SHELF_X, 38):
        rect(x, 57, x + 26, 58, W_DARK)
        rect(x, 58, x + 1, 66, W_DARK)
    # bookshelf: posts, boards, rows of books of varying height
    rect(SHELF_X - 4, 0, VIEW_W, DESK_TOP, WOOD_D)
    rect(SHELF_X - 4, 0, SHELF_X - 2, DESK_TOP, WOOD_M)
    widths = (5, 6, 4, 7, 5, 5, 6, 4, 6, 5, 7, 4, 5, 6)
    for r, (top, bottom) in enumerate(((4, 21), (26, 43), (48, 65))):
        x, i = SHELF_X + 1, r * 3
        while x < VIEW_W:
            w = widths[i % len(widths)]
            c, dark = BOOKS[(i * 3 + r) % len(BOOKS)]
            h = bottom - top - (i * 7 + r * 5) % 5
            if (i + r) % 9 == 5:                     # a gap, then a leaning book
                for k in range(w + 2):
                    rect(x + k, bottom - (k * (h - 2)) // (w + 2) - 3, x + k + 1, bottom,
                         c if k < w + 1 else dark)
                x += w + 5
            else:
                rect(x, bottom - h, x + w, bottom, c)
                rect(x + w - 1, bottom - h, x + w, bottom, dark)
                rect(x, bottom - h + 3, x + w - 1, bottom - h + 4, dark)
                x += w
            i += 1
        rect(SHELF_X - 2, bottom, VIEW_W, bottom + 3, WOOD_M)
        rect(SHELF_X - 2, bottom, VIEW_W, bottom + 1, WOOD_L)
    rect(SHELF_X - 2, 0, VIEW_W, 2, WOOD_M)
    # desk: a dark back edge, a lit strip, the top with a little grain, the front edge
    rect(0, DESK_TOP, VIEW_W, DESK_TOP + 1, DESK_E)
    rect(0, DESK_TOP + 1, VIEW_W, DESK_TOP + 3, DESK_L)
    rect(0, DESK_TOP + 3, VIEW_W, VIEW_H - 6, DESK)
    for y, x0, x1 in ((74, 6, 60), (79, 90, 150), (84, 20, 70), (77, 180, 236), (86, 160, 210)):
        rect(x0, y, x1, y + 1, DESK_D)
    rect(0, VIEW_H - 6, VIEW_W, VIEW_H - 5, DESK_L)
    rect(0, VIEW_H - 5, VIEW_W, VIEW_H, DESK_D)
    # PIKACHU's shadow on the desk
    sx, sy = PIKA_POS[0] + 30, PIKA_POS[1] + 61 - VIEW_Y
    for y in range(VIEW_H):
        for x in range(VIEW_W):
            if ((x + 0.5 - sx) / 19) ** 2 + ((y + 0.5 - sy) / 3.2) ** 2 <= 1 and img[y][x] in (DESK, DESK_L):
                img[y][x] = DESK_D
    return img


# ---------------------------------------------------------------- choreography
FRAMES = 76                      # F842-917 = bar 2 of MUS_INTRO_FIGHT (19.15 frames a beat)
TRACKS = ('pikachu', 'sleeve', 'hand', 'ball', 'spark_cheek', 'spark_ball', 'bolt')
HIDE, FRONT = 1, 2               # key flags: not drawn / drawn in front of the arm
POSE = {'A': 0, 'B': 1, 'C': 2}
HAND_HOLD, HAND_OPEN = 1, 2      # frames of arm.png (0 is the sleeve half)
BALL_ROLL = (0, 3, 2, 1)         # ball frames turning anticlockwise (rolling left)
BALL_OPENING = 4
SPARK_FIRST = 5                  # the sparks follow the five ball frames in props.png
T_SNAP, T_POP = 19, 23           # beat 2: the ball opens, PIKACHU turns away; the spark
CHEEK = (152, 66)                # spark sprite corner at PIKACHU's near cheek (pose C)
DESK_Y = 112                     # ball centre on the desk (in front of the arm)
SPARK_TIMES = ((T_POP, 6), (57, 5), (66, 5))   # beat 2 (the pop), beat 4, once more
BOLT_AT = (100, 60)              # bolt sprite corner: from the cheek (right) to the ball (left)


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_in(p):
    return p ** 3


def lerp(a, b, p):
    return a + (b - a) * p


def ball_path():
    """Ball centre and frame for each frame from the pop: knocked up and to the left,
    two bounces on the desk (the first on beat 3), then it rolls off the left edge."""
    x, y = BALL_REST[0] + 4, BALL_REST[1] - 2
    vx, vy, g = -3.0, -4.0, 0.85
    out, spin, bounces = {}, 0.0, 0
    for t in range(T_POP, FRAMES):
        out[t] = (x, y, BALL_ROLL[int(spin) % 4])
        x += vx
        vy += g
        y += vy
        if y >= DESK_Y and vy > 0:
            y = DESK_Y
            bounces += 1
            if bounces < 3:
                vy, vx = -vy * 0.45, vx * 0.85
            else:                                # rolling
                vy = g = 0.0
        spin += abs(vx) / 4.5            # a quarter turn every ~9 pixels
    return out


def choreography():
    """keys[t][track] = (x, y, frame, flags), x and y the sprite's corner on screen."""
    ax0, ay0 = arm_rest()
    path = ball_path()
    keys = []
    for t in range(FRAMES):
        k = {}
        # PIKACHU looks at the ball; on beat 2 it snaps away (smear frame, 2 pixel
        # flinch) and sulks; a 1 pixel hop each time its cheeks crackle
        if t < T_SNAP:
            pose, dy = 'A', 0
        elif t < T_SNAP + 3:
            pose, dy = 'B', -2
        else:
            pose, dy = 'C', 0
        if any(t0 <= t < t0 + 2 for t0, _ in SPARK_TIMES[1:]):
            dy = -1
        k['pikachu'] = (PIKA_POS[0], PIKA_POS[1] + dy, POSE[pose], 0)
        # the arm: in from the lower left, a small nudge ("here"), a flinch when the
        # ball is knocked away, then it withdraws
        if t < 14:
            p = ease_out((t + 1) / 14)
            dx, dy = lerp(-70, 0, p), lerp(46, 0, p)
        elif t < T_SNAP:
            p = min(1, (t - 13) / 4)
            dx, dy = lerp(0, 4, p), lerp(0, -2, p)
        elif t < T_POP:
            dx, dy = 4, -2
        elif t < T_POP + 5:
            p = ease_out((t - T_POP + 1) / 5)
            dx, dy = lerp(4, -4, p), lerp(-2, 3, p)
        elif t < 34:
            dx, dy = -4, 3
        else:
            p = ease_in(min(1, (t - 33) / 16))
            dx, dy = lerp(-4, -84, p), lerp(3, 60, p)
        hidden = HIDE if t >= 50 else 0
        ax, ay = round(ax0 + dx), round(ay0 + dy)
        k['sleeve'] = (ax, ay, 0, hidden)
        k['hand'] = (ax + 64, ay, HAND_HOLD if t < T_POP else HAND_OPEN, hidden)
        # the ball: in the hand (behind the fingers), opening at the snap, then flying
        if t < T_POP:
            bx, by = ball_on_hand()
            k['ball'] = (ax + bx, ay + by, BALL_OPENING if t >= T_SNAP else 0, 0)
        else:
            x, y, frame = path[t]
            k['ball'] = (round(x - 7.5), round(y - 7.5), frame, FRONT | (HIDE if x < -8 else 0))
        k['spark_cheek'] = (0, 0, 0, HIDE)
        for t0, n in SPARK_TIMES:
            if t0 <= t < t0 + n:
                k['spark_cheek'] = (CHEEK[0], CHEEK[1], (t - t0) // 2 % 2, 0)
        if T_POP <= t < T_POP + 5:
            k['spark_ball'] = (k['ball'][0], k['ball'][1], (t - T_POP + 1) // 2 % 2, FRONT)
        else:
            k['spark_ball'] = (0, 0, 0, HIDE)
        # the zap itself, cheek to ball, on the two frames before the ball flies
        if T_POP - 1 <= t <= T_POP:
            k['bolt'] = (BOLT_AT[0], BOLT_AT[1], t - (T_POP - 1), FRONT)
        else:
            k['bolt'] = (0, 0, 0, HIDE)
        keys.append(k)
    return keys


# ---------------------------------------------------------------- output
def art():
    """Every sprite frame, by track (frame numbers as in the key table)."""
    poses = pikachu_poses()
    hold, opened = arm('hold'), arm('open')
    sleeve = [r[:64] for r in hold]
    sparks = spark_frames()
    return {'pikachu': ([poses['A'], poses['B'], poses['C']], PIKA_PAL),
            'sleeve': ([sleeve], PROP_PAL),
            'hand': ([sleeve, [r[64:] for r in hold], [r[64:] for r in opened]], PROP_PAL),
            'ball': (ball_frames(), PROP_PAL),
            'spark_cheek': (sparks, PROP_PAL),
            'spark_ball': (sparks, PROP_PAL),
            'bolt': (bolt_frames(), PROP_PAL)}


def mask_of(im):
    return Image.frombytes('L', im.size, bytes(255 if v else 0 for v in im.getdata()))


def render_frame(k, bg, sheets):
    """The 240x160 screen for one key table entry, the way the game draws it."""
    screen = Image.new('RGB', (240, 160), (0, 0, 0))
    screen.paste(bg, (0, VIEW_Y))

    def put(track):
        x, y, frame, flags = k[track]
        if flags & HIDE:
            return
        frames, pal = sheets[track]
        im = to_image(frames[frame], pal)
        screen.paste(im.convert('RGB'), (x, y), mask_of(im))
    front = k['ball'][3] & FRONT
    order = ['pikachu'] + ([] if front else ['ball']) + ['sleeve', 'hand'] + \
            (['ball'] if front else []) + ['bolt', 'spark_ball', 'spark_cheek']
    for track in order:                          # back to front
        put(track)
    black = Image.new('RGB', (240, VIEW_Y), (0, 0, 0))
    screen.paste(black, (0, 0))
    screen.paste(black, (0, VIEW_Y + VIEW_H))
    return screen


def strip(frames, pal):
    """Frames stacked top to bottom: the 1D OBJ tile order the game loads."""
    w, h = len(frames[0][0]), len(frames[0])
    rows = [r for f in frames for r in f]
    im = to_image(rows, pal)
    assert im.size == (w, h * len(frames))
    return im


def tiles_and_map(img, bank):
    """Cut a 240x96 picture into 8x8 tiles (flipped copies reused) and a 32x32 tilemap
    whose rows 4-15 hold it (screen rows 32-127); tile 0 is left empty."""
    def flip(t, h, v):
        return tuple(t[(7 - y if v else y) * 8 + (7 - x if h else x)] for y in range(8) for x in range(8))
    uniq = [tuple([0] * 64)]
    index = {uniq[0]: 0}
    entries = [0] * (32 * 32)
    for ty in range(VIEW_H // 8):
        for tx in range(VIEW_W // 8):
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
    per_row = 16
    rows = (len(uniq) + per_row - 1) // per_row
    sheet = [[0] * (per_row * 8) for _ in range(rows * 8)]
    for i, t in enumerate(uniq):
        r, c = divmod(i, per_row)
        for k, v in enumerate(t):
            sheet[r * 8 + k // 8][c * 8 + k % 8] = v
    return sheet, entries, len(uniq)


def write_header(keys, path):
    lines = ['// Generated by tools/make_intro_opening_scene2.py. Do not edit: change the',
             '// choreography there and run it again.',
             '// Scene 2 of the opening, one row per frame (F842-917): for each sprite',
             '// track {x, y, frame, flags}, x and y the corner of the sprite on screen.',
             '',
             '#define SCENE2_FRAMES %d' % FRAMES,
             '',
             'enum {']
    lines += ['    SCENE2_TRACK_%s,' % t.upper() for t in TRACKS]
    lines += ['    SCENE2_TRACK_COUNT', '};', '',
              'static const struct OpeningKey sScene2_Keys[SCENE2_FRAMES][SCENE2_TRACK_COUNT] = {']
    for t, k in enumerate(keys):
        cells = ', '.join('{%d, %d, %d, %d}' % k[tr] for tr in TRACKS)
        lines.append('    [%d] = {%s},' % (t, cells))
    lines += ['};', '']
    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', default=None, help='also write model sheets and mock-ups here')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sheets = art()
    bg = background()
    tiles, entries, n = tiles_and_map(bg, BG_PAL_BANK)
    to_image(tiles, BG_PAL).save(OUT + '/bg.png')
    with open(OUT + '/bg.bin', 'wb') as f:
        f.write(struct.pack('<%dH' % len(entries), *entries))
    strip(sheets['pikachu'][0], PIKA_PAL).save(OUT + '/pikachu.png')
    strip(sheets['hand'][0], PROP_PAL).save(OUT + '/arm.png')
    strip(ball_frames() + spark_frames(), PROP_PAL).save(OUT + '/props.png')
    strip(bolt_frames(), PROP_PAL).save(OUT + '/bolt.png')
    keys = choreography()
    write_header(keys, HEADER)
    print('scene 2: %d background tiles, %d frames' % (n, len(keys)))
    if a.preview:
        os.makedirs(a.preview + '/mock', exist_ok=True)
        bg_rgb = to_image(bg, BG_PAL).convert('RGB')
        for t, k in enumerate(keys):
            render_frame(k, bg_rgb, sheets).save('%s/mock/t%02d.png' % (a.preview, t))
        model = Image.new('RGB', (3 * 64 * 4 + 32, 64 * 4 + 16), (150, 190, 230))
        for i, p in enumerate(sheets['pikachu'][0]):
            im = to_image(p, PIKA_PAL)
            big = enlarge(im, 4)
            model.paste(big, (8 + i * (64 * 4 + 8), 8), mask_of(im).resize(big.size))
        model.save(a.preview + '/pikachu_model.png')
        props = [arm('hold'), arm('open')]
        pw = sum(len(p[0]) * 3 + 8 for p in props) + 8 + 7 * (16 * 3 + 8)
        sheet = Image.new('RGB', (pw, 64 * 3 + 16), (150, 190, 230))
        x = 8
        for p in props + ball_frames() + spark_frames():
            im = to_image(p, PROP_PAL)
            big = enlarge(im, 3)
            sheet.paste(big, (x, 8), mask_of(im).resize(big.size))
            x += big.size[0] + 8
        sheet.save(a.preview + '/props_model.png')


if __name__ == '__main__':
    main()
