"""The opening's RED (the player, FR/LG design): a model for scenes 1, 4 and 5.

The FR/LG player as drawn in his trainer pictures (graphics/trainers/front_pics/
red_front_pic.png, back_pics/red_back_pic.png) and overworld sprite: red cap with a
white front and a red brim, brown hair (as in his FR/LG back picture), red vest with a white collar over a dark
shirt, blue jeans, red and white shoes, a yellow backpack. Colours are the front
picture's palette. Drawn with the opening's rules (tools/intro_opening_art.py):
black outline below and to the right, the material's dark colour on the lit
upper-left side, the lower-right crescent of each mass in shade.

He is built on a small rig: hip and shoulder points, limbs as two segments whose
angles (degrees from straight down, positive = forward) set the pose. That keeps the
run cycle's proportions identical from frame to frame.

side_run(i): four frames of running to the right (the passing and contact positions
of both legs); back_view(pose): standing, or hunched over PIKACHU held to his chest
(scene 4), seen from behind.
"""
import math

from intro_opening_art import Figure, stamp

PAL = [(0, 0, 0), (255, 230, 180), (230, 189, 156), (205, 148, 115), (123, 90, 82),
       (123, 189, 222), (82, 139, 180), (49, 106, 139), (24, 41, 82), (213, 213, 222),
       (255, 197, 90), (189, 156, 90), (255, 98, 90), (197, 65, 65), (255, 255, 255), (16, 16, 16)]
PAL[1] = (74, 49, 41)            # the hair's shade (the old skin light, never used)
HAIR_D, SKIN, SKIN_S, SKIN_O = 1, 2, 3, 4
JEAN_L, JEAN, JEAN_S, NAVY = 5, 6, 7, 8
GREYW, BAG, BAG_S, RED_L, RED, WHITE, BLACK = 9, 10, 11, 12, 13, 14, 15
S = 64

COLORS = {
    'S': dict(base=SKIN, rim=SKIN_O, rim_dark=BLACK, line=SKIN_O, mid=SKIN_S, shade=(2, 2)),
    'R': dict(base=RED_L, rim=RED, rim_dark=BLACK, line=RED, mid=RED, shade=(3, 3)),
    'J': dict(base=JEAN, rim=JEAN_S, rim_dark=NAVY, line=JEAN_S, mid=JEAN_S, shade=(2, 3)),
    'H': dict(base=SKIN_O, rim=HAIR_D, rim_dark=BLACK),               # brown hair
    'D': dict(base=NAVY, rim=BLACK, rim_dark=BLACK, line=BLACK),        # dark shirt
    'B': dict(base=BAG, rim=BAG_S, rim_dark=BLACK, line=BAG_S, mid=BAG_S, shade=(3, 3)),
    'W': dict(base=WHITE, rim=GREYW, rim_dark=BLACK, line=GREYW, mid=GREYW, shade=(2, 2)),
}
KEY = {'K': BLACK, 'W': WHITE, 's': SKIN_S, 'o': SKIN_O, 'h': SKIN_O, 'H': HAIR_D, 'n': NAVY, 'w': GREYW,
       'r': RED, 'R': RED_L}


def _end(x, y, length, deg):
    a = math.radians(deg)
    return x + length * math.sin(a), y + length * math.cos(a)


def _limb(f, name, x, y, a1, a2, l1, l2, w1, w2, kind, end=None):
    """Two segments from (x, y): upper at angle a1, lower at a2 (degrees from straight
    down, positive forward). Returns the far end."""
    kx, ky = _end(x, y, l1, a1)
    ex, ey = _end(kx, ky, l2, a2)
    f.stroke(name + '1', [(x, y), (kx, ky)], [w1, w1 * 0.9], kind=kind)
    f.stroke(name + '2', [(kx, ky), (ex, ey)], [w1 * 0.9, w2], kind=kind)
    f.merged(name + '1', name + '2')
    return ex, ey


# (near thigh, near shin, far thigh, far shin, near upper arm, near forearm,
#  far upper arm, far forearm, body bob, backpack lag)
# The legs spread (0, 2) are the moments in the air, so the body is up there; the
# passing frames (1, 3) are the landings, the body down and the standing knee bent.
# The backpack follows the body one pixel late.
RUN = ((32, 12, -34, -72, -42, -8, 42, 100, -2, 0),
       (12, -16, 16, -88, -14, 30, 14, 76, 0, -1),
       (-34, -72, 32, 12, 42, 100, -42, -8, -2, 0),
       (16, -88, 12, -16, 14, 76, -14, 30, 0, -1))

# The far arm and leg a step darker than the near ones, so the sides swap visibly.
FAR = {
    'SF': dict(base=SKIN_S, rim=SKIN_O, rim_dark=BLACK, line=SKIN_O, mid=SKIN_O, shade=(2, 2)),
    'JF': dict(base=JEAN_S, rim=NAVY, rim_dark=BLACK, line=NAVY, mid=NAVY, shade=(2, 3)),
    'RF': dict(base=RED, rim=BLACK, rim_dark=BLACK, line=BLACK),
}


def side_run(i):
    """Running to the right, frame i of 4."""
    nt, ns, ft, fs, nu, nf, fu, ff, bob, lag = RUN[i]
    f = Figure(S, S)
    hx, hy = 30, 38 + bob            # hip
    sx, sy = 33, 22 + bob            # shoulder (leaning into the run)
    # far limbs, behind the body, a step darker
    _limb(f, 'farArm', sx - 1, sy + 1, fu, ff, 8, 7, 4, 3.5, 'SF')
    fx, fy = _limb(f, 'farLeg', hx - 1, hy, ft, fs, 11, 11, 6, 5, 'JF')
    f.ellipse('farShoe', fx + 2, fy + 1, 4, 2.4, kind='RF', rot=math.radians(-fs) * 0.3)
    # backpack on the back, the torso (dark shirt, red vest), the head
    f.ellipse('bag', sx - 8, sy + 8 - lag, 6, 8, kind='B', rot=-0.15)
    f.ellipse('shirt', (hx + sx) / 2 + 1, (hy + sy) / 2, 6.5, 10, kind='D', rot=-0.15)
    f.ellipse('vest', (hx + sx) / 2, (hy + sy) / 2 - 0.5, 6, 9.5, kind='R', rot=-0.15)
    f.stroke('strap', [(sx - 3, sy - 2 - lag), (sx + 1, sy + 9)], [2, 2], kind='B')
    f.ellipse('hipsJ', hx, hy + 1, 5.5, 4, kind='J')
    nx, ny = _limb(f, 'nearLeg', hx + 1, hy, nt, ns, 11, 11, 6, 5, 'J')
    f.ellipse('nearShoe', nx + 2, ny + 1, 4.2, 2.5, kind='R', rot=math.radians(-ns) * 0.3)
    f.ellipse('head', sx + 3, sy - 8, 7, 7.5, kind='S')
    f.ellipse('hair', sx - 1, sy - 8, 5.5, 6, kind='H')
    f.clip('hair', lambda x, y: x <= sx + 1)       # the face is half the head
    f.ellipse('cap', sx + 3, sy - 12, 7.5, 5, kind='R')
    f.clip('cap', lambda x, y: y <= sy - 11)
    f.poly('brim', [(sx + 6, sy - 12), (sx + 14, sy - 11), (sx + 14, sy - 9.5), (sx + 5, sy - 9.5)], kind='R')
    f.ellipse('capfront', sx + 7, sy - 13.5, 3, 2.5, kind='W')
    f.clip('capfront', lambda x, y: y <= sy - 12)
    _limb(f, 'nearArm', sx + 1, sy + 1, nu, nf, 8, 7, 4.2, 3.6, 'S')
    f.ellipse('sleeve', sx + 1, sy + 2, 3, 3, kind='D')
    f.merged('head', 'hair')
    img = f.render(dict(COLORS, **FAR))
    # the brim two pixels thick (red over its black shadow line)
    stamp(img, sx + 8, sy - 11, ['rrr'], KEY)
    stamp(img, sx + 8, sy - 10, ['KKKK'], KEY)
    # face: eye and brow, the ear in the hair, the shadow of the brim
    ex, ey = round(sx + 6), round(sy - 9)
    stamp(img, ex, ey, ['K', 'K'], KEY)
    stamp(img, sx + 5, sy - 10, ['hhh'], KEY)
    stamp(img, sx, sy - 8, ['ss', 'so'], KEY)
    stamp(img, sx + 2, sy - 11, ['HHHHHH'], KEY)
    # the shoes' white toe caps
    for name, px, py in (('nearShoe', nx, ny), ('farShoe', fx, fy)):
        stamp(img, round(px + 3), round(py), ['W', 'W'], {'W': WHITE})
    return img


# The back of the head, hand-placed (FR/LG's back picture: brown hair under the cap,
# tufts over the neck; the cap's back strap across its opening). 16 wide, top row is
# the crown of the cap. '.' clears.
BACK_HEAD = [
    '.....ddddddK....',
    '...ddccccccccK..',
    '..dcccccccccccK.',
    '.dcccccccccccccK',
    '.dcccchhhhhcccrK',
    '.dccchhhHHhhccrK',
    '.drrrrrrrrrrrrrK',
    '..KhhhhhhhhhhHK.',
    '..KhhhHhhhhhHHK.',
    '..shhhHhhhHhHHs.',
    '..shhhhHhhHhHHs.',
    '..KhhhhHhhHHHHK.',
    '..KhhhhhhhhHHHK.',
    '...hKhhsshHKHK..',
    '...K.KssssK.K...',
    '......KssK......',
]


def _stamp_clear(img, x0, y0, rows, key, keep_below=None):
    for dy, r in enumerate(rows):
        y = y0 + dy
        if keep_below is not None and y >= keep_below:
            break
        for dx, ch in enumerate(r):
            if 0 <= y < S and 0 <= x0 + dx < S:
                img[y][x0 + dx] = 0 if ch == '.' else key[ch]


# PIKACHU inside RED's picture in scene 4, at RED's scale (about 16 pixels tall, so
# only the ears over his left shoulder and the tail tip beside his right side show).
# Its three colours take RED's slots 5, 9 and 14, which his back views do not use.
PIKA_Y, PIKA_M, PIKA_O = 5, 9, 14
SHIELD_PAL = list(PAL)
SHIELD_PAL[PIKA_Y], SHIELD_PAL[PIKA_M], SHIELD_PAL[PIKA_O] = (255, 238, 0), (238, 189, 0), (131, 82, 0)
PKEY = {'K': BLACK, 'y': PIKA_Y, 'm': PIKA_M, 'o': PIKA_O}
P_EARS = [          # the top of its head and two long ears (black tips) over his shoulder
    'K......K.',
    'KK.....KK',
    'oK....oK.',
    'oyK...oyK',
    'oyK...oyK',
    'oyyK.oyyK',
    '.oyyoyyymK',
    'oyyyyyyymK',
    'oyyyyyymmK',
    'oyyyyymmmK',
]
P_TAIL = [          # the lightning tail's last two segments, out past his right side
    '....oyK',
    '...oyyK',
    '..oyymK',
    '...oymK',
    '..oymK.',
    '.oymK..',
    '.omK...',
    '.oK....',
]


def back_view(pose='stand', pikachu=True):
    """From behind. 'stand': feet apart, arms down. 'shield' / 'shield-open': scene 4,
    crouched over PIKACHU on the ground (knees bent, back rounded, head bowed, about 46
    pixels tall); 'shield' has the arms round PIKACHU in front, 'shield-open' spreads
    them against the flock. PIKACHU's ears show over his left shoulder, its tail tip
    by his right side (pikachu=False: it has sprung out, scene 5)."""
    f = Figure(S, S)
    cx = 32
    if pose == 'stand':
        sy, hipy = 22, 38
        for side in (-1, 1):
            ex, ey = _limb(f, 'leg%d' % side, cx + side * 4, hipy, side * 6, side * 2, 11, 11, 6.5, 5.5, 'J')
            f.ellipse('shoe%d' % side, ex, ey + 1, 3.5, 2.5, kind='R')
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * 9, sy + 2, side * 12, side * 4, 8, 7, 4.2, 3.6, 'S')
        f.ellipse('shirt', cx, 31, 9.5, 10, kind='D')
        f.ellipse('vest', cx, 31, 9, 9.5, kind='R')
        f.ellipse('hipsJ', cx, hipy, 8, 4, kind='J')
        f.ellipse('bag', cx, 32, 7.5, 8.5, kind='B')
        f.stroke('strapL', [(cx - 6, sy), (cx - 5, sy + 7)], [2, 2], kind='B')
        f.stroke('strapR', [(cx + 6, sy), (cx + 5, sy + 7)], [2, 2], kind='B')
        img = f.render(COLORS)
        _stamp_clear(img, cx - 8, 5, BACK_HEAD, dict(KEY, h=SKIN_O, H=HAIR_D, s=SKIN_S, d=RED, c=RED_L))
        stamp(img, cx - 5, 30, ['sssssssssss'], {'s': BAG_S})
        stamp(img, cx - 5, 31, ['...KKKKK...'], {'K': BAG_S})
        return img
    # crouched: hips low between bent knees, the back a dome, the head bowed
    hipy, sy = 49, 30
    for side in (-1, 1):
        ex, ey = _limb(f, 'leg%d' % side, cx + side * 5, hipy, side * 58, side * 8, 7, 7, 6.5, 5.5, 'J')
        f.ellipse('shoe%d' % side, ex + side, ey + 1.5, 3.5, 2.3, kind='R')
    if pose == 'shield-open':          # arms out wide against the birds
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * 10, sy + 1, side * 105, side * 125, 8, 7, 4.2, 3.6, 'S')
    else:                              # upper arms only: the forearms hug PIKACHU in front
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * 10, sy + 1, side * 12, -side * 40, 7, 3, 4.4, 4, 'S')
    f.ellipse('shirt', cx, 39, 11, 10.5, kind='D')
    f.ellipse('vest', cx, 39, 10.5, 10, kind='R')
    f.ellipse('hipsJ', cx, hipy, 9, 4.5, kind='J')
    f.ellipse('bag', cx, 40, 8.5, 9, kind='B')
    f.stroke('strapL', [(cx - 7, sy - 1), (cx - 6, sy + 6)], [2, 2], kind='B')
    f.stroke('strapR', [(cx + 7, sy - 1), (cx + 6, sy + 6)], [2, 2], kind='B')
    img = f.render(COLORS)
    # the bowed head: the cap's crown and the hair above the shoulders
    _stamp_clear(img, cx - 8, 20, BACK_HEAD, dict(KEY, h=SKIN_O, H=HAIR_D, s=SKIN_S, d=RED, c=RED_L),
                 keep_below=30)
    stamp(img, cx - 6, 38, ['sssssssssssss'], {'s': BAG_S})
    stamp(img, cx - 6, 39, ['...KKKKKKK...'], {'K': BAG_S})
    if not pikachu:
        return img
    # small PIKACHU: ears behind the left shoulder, tail tip past the right side
    for y, r in enumerate(P_EARS):
        for x, ch in enumerate(r):
            px, py = 18 + x, 19 + y
            if ch != '.' and img[py][px] == 0:
                img[py][px] = PKEY[ch]
    tx = 44 if pose == 'shield' else 41
    for y, r in enumerate(P_TAIL):
        for x, ch in enumerate(r):
            px, py = tx + x, 38 + y
            if ch != '.' and img[py][px] == 0:
                img[py][px] = PKEY[ch]
    return img


def model_views():
    out = {}
    for i in range(len(RUN)):
        out['run %d' % i] = side_run(i)
    out['back'] = back_view('stand')
    out['back, shielding'] = back_view('shield')
    out['back, shielding, arms out'] = back_view('shield-open')
    return out
