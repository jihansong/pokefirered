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

side_run(i, carry): four frames of running to the right (the passing and contact
positions of both legs), with carry the small PIKACHU in his arms; back_view(pose):
standing, bending (two in-betweens) and hunched over PIKACHU held to his chest
(scene 4), seen from behind.
"""
import math

from intro_opening_art import Figure, stamp

PAL = [(0, 0, 0), (255, 230, 180), (230, 189, 156), (205, 148, 115), (123, 90, 82),
       (123, 189, 222), (82, 139, 180), (49, 106, 139), (24, 41, 82), (213, 213, 222),
       (255, 197, 90), (189, 156, 90), (255, 98, 90), (197, 65, 65), (255, 255, 255), (16, 16, 16)]
PAL[1] = (74, 49, 41)            # the hair's shade (the old skin light, never used)
PAL[5] = (255, 238, 0)           # PIKACHU's yellow (the jeans' light, never used)
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


# PIKACHU inside RED's picture in scene 4, at RED's scale (about 16 pixels tall, so
# only its head and ears over his left shoulder and the tail tip beside his right side
# show). Its colours are the same slots in every RED picture of scene 4 (run, back,
# crouch), so it does not change colour between them: slot 5 (PIKACHU's yellow, the
# jeans' light, which RED never uses), the backpack's orange as its shade, the skin's
# outline brown as its outline.
PIKA_Y, PIKA_M, PIKA_O = 5, BAG, SKIN_O
SHIELD_PAL = list(PAL)
PKEY = {'K': BLACK, 'y': PIKA_Y, 'm': PIKA_M, 'o': PIKA_O}

# The small PIKACHU carried in his arms on the run (art review of 4-5 draft A, change
# 2): curled against his chest, facing forward, eyes shut, its ears up in a V in
# front of his chin, the tail's flag hanging out under his arms. At his scale, pixelled at 1x,
# in the colours above (PKEY) and his red for its cheek.
CARRY = [          # origin (sx + 4, sy - 7): the ears stand in a V in front of his face
    '......K....K..',
    '.....KK...KK..',
    '.....KK...KK..',
    '.....oyK.oyK..',
    '.....oyK.oyyK.',
    '....oyyooyyyK.',
    '...oyyyyyyyyyK',
    '..oyyyyyyyyyyK',
    '..oyyyyyyyKKyK',
    '..oyyyyyrryyyK',
    '...oyyyyrrymK.',
    '...KmyyyyymmK.',
    '..oyyyyyyyymK.',
    '..oyyyyyyyymK.',
    '...KmmmmmmmK..',
]
CARRY_TAIL = [          # the flag, out under his arms and back past his hip
    '..oyyK',
    '.oyymK',
    '..oymK',
    '.oymK.',
    'oymK..',
]
CKEY = dict(PKEY, r=RED)
# PIKACHU rides a pixel behind RED's bob (half a beat late): offset per run frame
CARRY_LAG = (1, 0, 1, 0)


def side_run(i, carry=False):
    """Running to the right, frame i of 4. carry: holding the small PIKACHU to his
    chest in both arms (the arms stop swinging)."""
    nt, ns, ft, fs, nu, nf, fu, ff, bob, lag = RUN[i]
    if carry:
        nu, nf, fu, ff = 30, 95, 36, 92
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
    if carry:
        # PIKACHU in front of his chest: a placeholder part so the near arm draws its
        # line over it; the pixels are stamped after the render
        pl = CARRY_LAG[i]
        f.pixels('pika', [(sx + 4 + x, sy - 7 + pl + y) for y, r in enumerate(CARRY) for x, ch in enumerate(r)
                          if ch != '.'], kind='D')
    _limb(f, 'nearArm', sx + 1, sy + 1, nu, nf, 8, 7, 4.2, 3.6, 'S')
    f.ellipse('sleeve', sx + 1, sy + 2, 3, 3, kind='D')
    f.merged('head', 'hair')
    img = f.render(dict(COLORS, **FAR))
    if carry:
        for y, r in enumerate(CARRY):
            for x, ch in enumerate(r):
                px, py = sx + 4 + x, sy - 7 + pl + y
                if ch != '.' and f.owner[py][px] == 'pika':
                    img[py][px] = CKEY[ch]
        for y, r in enumerate(CARRY_TAIL):
            for x, ch in enumerate(r):
                px, py = sx + 1 + x, sy + 7 + pl + y
                if ch != '.' and f.owner[py][px] not in ('nearArm1', 'nearArm2', 'sleeve'):
                    img[py][px] = CKEY[ch]
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


P_EARS = [          # the top of its head over his left shoulder (art review R1): a round
    '.K.............',  # dome, 6 wide and 2 high, between two ears splayed in a V; the
    '.KKK...........',  # outer ear leans out about 30 degrees, the inner one stands
    '..KKK.......K..',  # nearly straight and tucks 1 pixel behind RED's head. Yellow ears
    '..KKK......KK..',  # with black tips (not black strokes), no notch between them:
    '...oyK.....KK..',  # one head and two ears, not a crown
    '...oyyK...oyK..',
    '....oyK.oooyK..',
    '....oyyoyyyymK.',
    '...oyyyyyyyymK.',
    '...oyyyyyyyymmK',
    '..oyyyyyyyyymmK',
    '..oyyyyyyyymmmK',
    '..oyyyyyyyymmmK',
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


def _mix(a, b, c):
    return a + (b - a) * c


# How far he has crouched, per back view: 0 standing, 1 crouched over PIKACHU.
# 'bend1' and 'bend2' are the in-betweens of scene 4 (art review of 4-5 draft A,
# change 1(b)): he goes down in one move, PIKACHU held to his chest all the way.
CROUCH = {'stand': 0.0, 'bend1': 1 / 3, 'bend2': 2 / 3, 'shield': 1.0, 'shield-open': 1.0}


def back_view(pose='stand', pikachu=True):
    """From behind. 'stand': feet apart; with pikachu, his arms bent round the small
    PIKACHU held to his chest (its ears over his left shoulder, its tail tip by his
    right side), without, arms down. 'bend1', 'bend2': going down into the crouch,
    knees bending, head bowing, arms still round PIKACHU. 'shield' / 'shield-open':
    scene 4, crouched over PIKACHU (knees bent, back rounded, head bowed, about 46
    pixels tall); 'shield' has the arms round PIKACHU in front, 'shield-open' spreads
    them against the flock (pikachu=False: it has sprung out, scene 5).
    Every pose stands on the same ground line (the soles at y 60-62)."""
    f = Figure(S, S)
    cx = 32
    c = CROUCH[pose]
    hipy = _mix(38, 49, c)
    sy = round(_mix(22, 30, c))
    # legs: the thighs swing out and forward (shorter seen from behind), feet planted
    for side in (-1, 1):
        ex, ey = _limb(f, 'leg%d' % side, cx + side * _mix(4, 5, c), hipy, side * _mix(6, 58, c),
                       side * _mix(2, 8, c), _mix(11, 7, c), _mix(11, 7, c), 6.5, 5.5, 'J')
        f.ellipse('shoe%d' % side, ex + side * c, ey + _mix(1, 1.5, c), 3.5, _mix(2.5, 2.3, c), kind='R')
    if pose == 'shield-open':          # arms out wide against the birds
        for side in (-1, 1):
            # elbows a little bent, the forearms raised, open hands like shields
            hx, hy = _limb(f, 'arm%d' % side, cx + side * 10, sy + 1, side * 98, side * 142, 8, 6, 4.2, 3.6, 'S')
            f.ellipse('hand%d' % side, hx + side * 0.5, hy - 0.5, 2.2, 2.6, kind='S')
    elif pose == 'stand' and not pikachu:
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * 9, sy + 2, side * 12, side * 4, 8, 7, 4.2, 3.6, 'S')
    else:                              # upper arms only: the forearms hug PIKACHU in front
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * _mix(9, 10, c), sy + _mix(2, 1, c), side * 12, -side * 40,
                  _mix(8, 7, c), 3, _mix(4.2, 4.4, c), 4, 'S')
    by = _mix(31, 39, c)
    f.ellipse('shirt', cx, by, _mix(9.5, 11, c), _mix(10, 10.5, c), kind='D')
    f.ellipse('vest', cx, by, _mix(9, 10.5, c), _mix(9.5, 10, c), kind='R')
    f.ellipse('hipsJ', cx, hipy, _mix(8, 9, c), _mix(4, 4.5, c), kind='J')
    f.ellipse('bag', cx, by + 1, _mix(7.5, 8.5, c), _mix(8.5, 9, c), kind='B')
    f.stroke('strapL', [(cx - _mix(6, 7, c), sy - c), (cx - _mix(5, 6, c), sy + _mix(7, 6, c))], [2, 2], kind='B')
    f.stroke('strapR', [(cx + _mix(6, 7, c), sy - c), (cx + _mix(5, 6, c), sy + _mix(7, 6, c))], [2, 2], kind='B')
    img = f.render(COLORS)
    # the head bows as he goes down: its top drops, less of it shows over the shoulders
    head_y = round(_mix(5, 20, c))
    rows = round(_mix(16, 10, c))
    _stamp_clear(img, cx - 8, head_y, BACK_HEAD, dict(KEY, h=SKIN_O, H=HAIR_D, s=SKIN_S, d=RED, c=RED_L),
                 keep_below=head_y + rows)
    bag_y = round(by) - 1
    half = round(_mix(5, 6, c))
    stamp(img, cx - half, bag_y, ['s' * (2 * half + 1)], {'s': BAG_S})
    stamp(img, cx - half, bag_y + 1, ['...' + 'K' * (2 * half - 5) + '...'], {'K': BAG_S})
    if not pikachu:
        return img
    # small PIKACHU: ears behind the left shoulder, tail tip past the right side
    for y, r in enumerate(P_EARS):
        for x, ch in enumerate(r):
            px, py = 12 + x, sy - 12 + y
            if ch != '.' and img[py][px] == 0:
                img[py][px] = PKEY[ch]
    tx = {'shield-open': 41}.get(pose, round(_mix(45, 44, c)))
    for y, r in enumerate(P_TAIL):
        for x, ch in enumerate(r):
            px, py = tx + x, sy + 8 + y
            if ch != '.' and img[py][px] == 0:
                img[py][px] = PKEY[ch]
    return img


def model_views():
    out = {}
    for i in range(len(RUN)):
        out['run %d' % i] = side_run(i)
    for i in range(len(RUN)):
        out['run carrying %d' % i] = side_run(i, carry=True)
    out['back'] = back_view('stand', pikachu=False)
    out['back, holding'] = back_view('stand')
    out['back, bend 1'] = back_view('bend1')
    out['back, bend 2'] = back_view('bend2')
    out['back, shielding'] = back_view('shield')
    out['back, shielding, arms out'] = back_view('shield-open')
    return out
