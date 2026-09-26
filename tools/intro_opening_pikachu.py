"""The opening's PIKACHU model: one rule-built figure, many poses (scenes 2, 4, 5, 6).

Proportions follow FR/LG's front sprite (graphics/pokemon/pikachu/front.png) and the
title screen PIKACHU, a little rounder (the anime's first season, only slightly):
the head is as tall as body and feet together, there is no neck (the jowls overlap
the top of the body), long ears with black tips over about a third of their length,
a flag-shaped lightning tail that is widest at its last segment, brown at the root.

Colours are graphics/pokemon/pikachu/normal.pal. Slots 7-9, empty in that palette,
hold the spark colours (orange, yellow, pale yellow) the opening's electric effects
use, so sparks and bolts share PIKACHU's palette.

Drawing rules (tools/intro_opening_art.py): black outline below and to the right,
brown on the lit upper-left side and between parts; the lower-right crescent of each
mass in shade; a light blob on the forehead and the belly; dark shade under the jaw
and the arms; a grey glint in the ear tips and under each eye.

pose(...) builds one 64x64 frame. Its parameters are the things a pose changes:
where the face turns (d), the arms, the eyes, the mouth, the ears, the tail, a lean of
the body and how far the chin is raised.
"""
import math

from intro_opening_art import Figure, stamp

PAL = [(0, 0, 0), (255, 255, 255), (255, 255, 123), (255, 238, 0), (238, 189, 0),
       (197, 139, 0), (131, 82, 0), (255, 139, 0), (255, 213, 57), (255, 255, 90),
       (255, 74, 74), (230, 0, 0), (180, 0, 0), (106, 106, 106), (16, 16, 16), (0, 0, 0)]
CLEAR, WHITE, LIGHT, YELLOW, MID, DARK, BROWN = 0, 1, 2, 3, 4, 5, 6
SPARK_RIM, SPARK, SPARK_PALE = 7, 8, 9
PINK, RED, DRED, GREY, BLACK = 10, 11, 12, 13, 14

COLORS = {
    'Y': dict(base=YELLOW, rim=BROWN, rim_dark=BLACK, line=BROWN, mid=MID, shade=(4, 4),
              no_line_over=('K',)),
    'K': dict(base=BLACK, rim=BLACK),
    'B': dict(base=BROWN, rim=BROWN, rim_dark=BLACK, line=BLACK),
}
KEY = {'K': BLACK, 'W': WHITE, 'g': GREY, 'o': BROWN, 'd': DARK, 'm': MID, 'l': LIGHT,
       'y': YELLOW, 'r': RED, 'R': DRED, 'p': PINK, 't': PINK}
S = 64
HEAD_PARTS = ('head', 'jowl', 'muzzle', 'ear0', 'ear1')


def tail(f, mode):
    """Lightning tail behind the body, rising to the right: thin brown root, a middle
    segment, and the widest flag at the end. mode 'rest', 'lag' (swung left, still
    following a turn) or 'flick' (whipped up to the right)."""
    pts = [(38, 57), (45, 49), (42, 43), (50, 35), (46, 30), (57, 18)]
    widths = [3, 4, 5, 6, 8, 9]
    rot = {'rest': 0.0, 'lag': -0.16, 'flick': 0.09}[mode]
    ox, oy = pts[1]
    c, s = math.cos(rot), math.sin(rot)
    pts = pts[:2] + [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c) for x, y in pts[2:]]
    f.stroke('tail', pts, widths)
    f.stroke('tailroot', pts[:2] + [((pts[1][0] + pts[2][0]) / 2 - 1, (pts[1][1] + pts[2][1]) / 2)],
             widths[:2] + [4], kind='B')
    f.clip('tailroot', lambda x, y: y >= 47)
    return pts


def ear(f, name, bx, by, tx, ty, width=8):
    """An ear from its root (bx, by) inside the head to the pointed tip (tx, ty); the
    far 35 percent black."""
    pts = f.lens(name, bx, by, tx, ty, width)
    length = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / length, (ty - by) / length
    f.pixels(name + 'tip', [(x, y) for x, y in pts
                            if (x + 0.5 - bx) * ux + (y + 0.5 - by) * uy > length * 0.58], kind='K')


def pose(d=-1.0, arms='side', eyes='open', mouth='w', ears='up', tail_mode='rest',
         lean=0, chin=0, squash=1.0):
    """One 64x64 frame of PIKACHU sitting, feet forward.
    d: face turn, -1 three quarters left, 0 front, +1 three quarters right.
    arms: 'side', 'tucked' (pressed to the body), 'crossed'.
    eyes: 'open', 'half' (suspicious), 'squeeze' (> <), 'shut' (turned-away, content).
    mouth: 'w', 'flat', 'tight', 'pout'.
    ears: 'up', 'twitch', 'drag' (trailing a turn to the right), 'fling' (overshooting
    to the right), 'back' (face-side ear laid back).
    lean: body shift in pixels (-1 leans toward the ball). chin: head raised in pixels."""
    f = Figure(S, S)
    hx, hy = 29, 25 - chin
    tail(f, tail_mode)
    bx = 30 + lean
    f.ellipse('body', bx, 44.5, 11, 10.5)
    f.ellipse('hips', bx, 51, 13.5, 6.5)
    f.merged('body', 'hips')
    f.ellipse('footL', 22 + lean, 58, 4.5, 2.5)
    f.ellipse('footR', 38 + lean, 58.5, 4.5, 2.5)
    if arms == 'side':
        f.ellipse('armL', bx - 11.5, 45, 2.6, 5, rot=0.55)
        f.ellipse('armR', bx + 11.5, 45.5, 2.6, 5, rot=-0.55)
    elif arms == 'tucked':
        f.ellipse('armL', bx - 9, 44, 2.6, 4.6, rot=0.2)
        f.ellipse('armR', bx + 9, 44, 2.6, 4.6, rot=-0.2)
    elif arms == 'crossed':
        f.ellipse('armBack', bx + 5, 45, 8, 3, rot=-0.10)
        f.ellipse('armFront', bx - 4, 42.5, 8.5, 3, rot=0.10)
    # ears (roots hidden in the head)
    tilt = {'up': 0.0, 'twitch': 0.08, 'drag': -0.35, 'fling': 0.32, 'back': 0.18}[ears]
    spread = 1.0 if ears != 'twitch' else 1.12
    for i, side in enumerate((-1, 1)):
        base = (hx + side * 8 + 1.5 * d, hy - 7)
        ang = side * 0.55 * spread + tilt + 0.1 * d
        if ears == 'back' and side == 1:
            ang += 0.25
        length = 17 - max(0, chin - 1)      # keep the tips inside the sprite
        tip = (base[0] + math.sin(ang) * length, base[1] - math.cos(ang) * length)
        ear(f, 'ear%d' % i, base[0], base[1], tip[0], tip[1])
    f.ellipse('head', hx - 1.5 * d, hy, 14 * squash, 11.5)
    f.ellipse('jowl', hx - 0.5 * d, hy + 5, 15 * squash, 7.5)
    if d:
        f.ellipse('muzzle', hx + 11 * d, hy + 4 - (1 if chin else 0), 4.5, 4)
    names = ('head', 'jowl', 'muzzle', 'body', 'hips', 'ear0', 'ear1')
    f.merged(*names)
    img = f.render(COLORS)
    owner = f.owner

    def at(x, y):
        return owner[y][x] if 0 <= x < S and 0 <= y < S else None

    def solid(x, y):
        return img[y][x] in (YELLOW, MID)
    # shade the head throws on the top of the body, deeper on the right
    for y in range(S):
        for x in range(S):
            if at(x, y) in ('body', 'hips') and solid(x, y):
                if at(x, y - 1) in HEAD_PARTS and x > bx + 2:
                    img[y][x] = DARK
                elif at(x, y - 1) in HEAD_PARTS or at(x, y - 2) in HEAD_PARTS or \
                        (x > bx and at(x, y - 3) in HEAD_PARTS):
                    img[y][x] = MID
    # shade under the arms
    for y in range(S):
        for x in range(S):
            if at(x, y) in ('body', 'hips', 'armBack') and solid(x, y) and \
                    str(at(x, y - 1)).startswith('arm') and at(x, y - 1) != at(x, y):
                img[y][x] = DARK
    # shade between the feet, under the hips
    for y in range(S):
        for x in range(S):
            if at(x, y) == 'hips' and solid(x, y) and y >= 54 and 26 + lean <= x <= 34 + lean:
                img[y][x] = DARK
    # grey glint in the black of the ear tips (upper left, inside)
    for n in ('ear0tip', 'ear1tip'):
        pts = sorted((y, x) for y in range(S) for x in range(S) if at(x, y) == n)
        if pts:
            mid_y = pts[len(pts) // 2][0]
            row = [x for y, x in pts if y == mid_y]
            if len(row) >= 3:
                img[mid_y][row[0] + 1] = GREY
                if mid_y + 1 < S and img[mid_y + 1][row[0] + 1] == BLACK:
                    img[mid_y + 1][row[0] + 1] = GREY
    # light blobs: forehead (upper left of the head) and belly
    stamp(img, round(hx - 1.5 * d) - 8, hy - 8, ['.llll.', 'llllll', '.llll.'], KEY)
    stamp(img, bx - 7, 38, ['.ll', 'lll', 'lll', '.l.'], KEY)
    # face
    fx = hx + round(6 * d)
    ey = hy - 3 - (1 if chin else 0)
    near, far = (fx - 5, fx + 5) if d > 0 else (fx + 4, fx - 5)
    if d == 0:
        near, far = fx + 4, fx - 5
    if eyes == 'open':
        stamp(img, near - 1, ey, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'], KEY)
        if d < 0:
            stamp(img, far - 1, ey, ['.KK', 'KWK', 'KKK', 'KKK', '.g.'], KEY)
        elif d > 0:
            stamp(img, far - 1, ey, ['KK.', 'WKK', 'KKK', 'KKK', '.g.'], KEY)
        else:
            stamp(img, far - 1, ey, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'], KEY)
    elif eyes == 'half':                 # lids down: suspicious
        stamp(img, near - 1, ey + 1, ['oooo', 'KWKK', 'KKKK', '.Kg.'], KEY)
        stamp(img, far - 1, ey + 1, ['ooo', 'KWK', 'KKK', '.g.'] if d < 0 else ['ooo', 'WKK', 'KKK', '.g.'], KEY)
    elif eyes == 'squeeze':              # > <
        stamp(img, fx - 8, ey + 1, ['KK..', '..KK', 'KK..'], KEY)
        stamp(img, fx + 4, ey + 1, ['..KK', 'KK..', '..KK'], KEY)
    elif eyes == 'shut':                 # closed, lids curved down: "hmph"
        if d > 0:
            stamp(img, near - 2, ey + 2, ['KKKK', '...K'], KEY)
            stamp(img, far - 1, ey + 2, ['KKK', '..K'], KEY)
        else:
            stamp(img, near - 1, ey + 2, ['KKKK', 'K...'], KEY)
            stamp(img, far - 1, ey + 2, ['KKK', 'K..'], KEY)
    nose = fx + (1 if d > 0 else -1 if d < 0 else 0)
    ny = hy + 1 - (1 if chin else 0)
    stamp(img, nose, ny, ['K'], KEY)
    my = ny + 2
    if mouth == 'w':
        stamp(img, nose - 2, my, ['o.o.o', '.o.o.'], KEY)
    elif mouth == 'flat':
        stamp(img, nose - 1, my, ['ooo'], KEY)
    elif mouth == 'tight':
        stamp(img, nose - 1, my + 1, ['ooo'], KEY)
    elif mouth == 'pout':
        stamp(img, nose - 1 + (1 if d > 0 else 0), my, ['.oo.', 'o..o'], KEY)
    # cheeks: the near one whole, the far one on the rim of the head
    cy = hy + 3 - (1 if chin else 0)
    near_cheek = ['.rrr.', 'prrrr', 'rrrrR', 'rrrRR', '.RRR.']
    if d > 0:
        stamp(img, fx - 12, cy, near_cheek, KEY)
        far_side = 1
    elif d < 0:
        stamp(img, fx + 7, cy, near_cheek, KEY)
        far_side = -1
    else:
        stamp(img, fx - 13, cy, near_cheek, KEY)
        stamp(img, fx + 8, cy, near_cheek, KEY)
        far_side = 0
    if far_side:
        for dy, (outer, inner) in enumerate(((DRED, RED), (DRED, RED), (DRED, DRED))):
            y = cy + 1 + dy
            xs = [x for x in range(S) if at(x, y) in HEAD_PARTS]
            if xs:
                x = max(xs) if far_side > 0 else min(xs)
                img[y][x] = outer
                img[y][x - far_side] = inner
    return img


def frames():
    """The scene 2 poses, in the order of pikachu.png."""
    return {
        'A': pose(-1, 'side', 'open', 'w', lean=-1),
        'A_twitch': pose(-1, 'side', 'open', 'w', ears='twitch', lean=-1),
        'A_sus': pose(-1, 'side', 'half', 'flat', lean=-1),
        'MID': pose(0, 'tucked', 'half', 'flat', ears='drag'),
        'B': pose(0.5, 'tucked', 'squeeze', 'tight', ears='drag', squash=0.93),
        'C_over': pose(1, 'crossed', 'shut', 'pout', ears='fling', tail_mode='lag', lean=1, chin=1),
        'C': pose(1, 'crossed', 'shut', 'pout', ears='back', lean=1, chin=1),
        'C_hmph': pose(1, 'crossed', 'shut', 'pout', ears='back', lean=1, chin=2),
        'C_flick': pose(1, 'crossed', 'shut', 'pout', ears='back', tail_mode='flick', lean=1, chin=1),
    }
