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


class Scaled(Figure):
    """A Figure whose shapes are given in 64x64 model units and drawn sc times larger
    (outlines stay 1 pixel: the shapes are scaled, not the drawing)."""

    def __init__(self, sc):
        Figure.__init__(self, S * sc, S * sc)
        self.sc = sc

    def ellipse(self, name, cx, cy, rx, ry, kind='Y', rot=0.0):
        k = self.sc
        return Figure.ellipse(self, name, cx * k, cy * k, rx * k, ry * k, kind, rot)

    def lens(self, name, x0, y0, x1, y1, width, kind='Y'):
        k = self.sc
        return Figure.lens(self, name, x0 * k, y0 * k, x1 * k, y1 * k, width * k, kind)

    def stroke(self, name, points, widths, kind='Y'):
        k = self.sc
        return Figure.stroke(self, name, [(x * k, y * k) for x, y in points], [w * k for w in widths], kind)

    def clip(self, name, keep):
        k = self.sc
        return Figure.clip(self, name, lambda x, y: keep(x / k, y / k))


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
    k = f.sc
    pts = f.lens(name, bx, by, tx, ty, width)
    length = math.hypot(tx - bx, ty - by) * k
    ux, uy = (tx - bx) * k / length, (ty - by) * k / length
    f.pixels(name + 'tip', [(x, y) for x, y in pts
                            if (x + 0.5 - bx * k) * ux + (y + 0.5 - by * k) * uy > length * 0.58], kind='K')


def blow_up(rows, k):
    return [''.join(ch * k for ch in r) for r in rows for _ in range(k)]


# Face stamps drawn for the 2x close-up (1 pixel lines, not blown up).
FACE2 = {
    'shut_near': ['KKKKKKKK', '......KK', '.......K'],
    'shut_far': ['KKKKKK', '.....K', '.....K'],
    'nose': ['KK'],
    'pout': ['.oooo.', 'o....o', 'o....o'],
    'cheek': ['..rrrrr..', '.rrrrrrr.', 'rpprrrrrr', 'rpprrrrrR', 'rrrrrrrRR',
              'rrrrrrRRR', '.rrrrRRR.', '..RRRRR..'],
}


def pose(d=-1.0, arms='side', eyes='open', mouth='w', ears='up', tail_mode='rest',
         lean=0, chin=0, squash=1.0, sc=1):
    """One frame of PIKACHU sitting, feet forward: 64x64, or (sc=2) 128x128 drawn
    twice as large with the same rules (the close-up; only the turned-away face
    with shut eyes and a pout is drawn at 2x).
    d: face turn, -1 three quarters left, 0 front, +1 three quarters right.
    arms: 'side', 'tucked' (pressed to the body), 'crossed'.
    eyes: 'open', 'half' (suspicious), 'squeeze' (> <), 'shut' (turned-away, content).
    mouth: 'w', 'flat', 'tight', 'pout'.
    ears: 'up', 'twitch', 'drag' (trailing a turn to the right), 'fling' (overshooting
    to the right), 'back' (face-side ear laid back).
    lean: body shift in model pixels (-1 leans toward the ball). chin: head raised."""
    f = Scaled(sc)
    W = S * sc
    hx, hy = 29, 25 - chin
    tail(f, tail_mode)
    bx = 30 + lean
    f.ellipse('body', bx, 44.5, 11, 10.5)
    f.ellipse('hips', bx, 51, 13.5, 6.5)
    f.merged('body', 'hips')
    f.ellipse('footL', 22 + lean, 58, 4, 2.8)
    f.ellipse('footR', 38 + lean, 58.5, 4, 2.8)
    if arms == 'side':
        f.ellipse('armL', bx - 11.5, 45, 2.6, 5, rot=0.55)
        f.ellipse('armR', bx + 11.5, 45.5, 2.6, 5, rot=-0.55)
    elif arms == 'tucked':
        f.ellipse('armL', bx - 9, 44, 2.6, 4.6, rot=0.2)
        f.ellipse('armR', bx + 9, 44, 2.6, 4.6, rot=-0.2)
    elif arms == 'crossed':
        # folded arms at chest height: only the far fist of the back arm shows past the
        # front arm, the near elbow rounds out of the body's silhouette
        f.ellipse('armBack', bx + 8.5, 39.8, 2, 2)
        f.ellipse('armFront', bx - 3, 40.8, 10.3, 2.9, rot=0.04)
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
    colors = dict(COLORS)
    colors['Y'] = dict(COLORS['Y'], shade=(4 * sc, 4 * sc))
    img = f.render(colors)
    owner = f.owner

    def at(x, y):
        return owner[y][x] if 0 <= x < W and 0 <= y < W else None

    def solid(x, y):
        return img[y][x] in (YELLOW, MID)
    # shade the head throws on the top of the body, deeper on the right
    for y in range(W):
        for x in range(W):
            if at(x, y) in ('body', 'hips') and solid(x, y):
                above = [at(x, y - k) for k in range(1, 3 * sc + 1)]
                if above[0] in HEAD_PARTS and x > (bx + 2) * sc:
                    img[y][x] = DARK
                elif any(a in HEAD_PARTS for a in above[:2 * sc]) or \
                        (x > bx * sc and any(a in HEAD_PARTS for a in above)):
                    img[y][x] = MID
    # shade under the arms (two rows under folded arms)
    for y in range(W):
        for x in range(W):
            if at(x, y) in ('body', 'hips', 'armBack') and solid(x, y):
                above = [at(x, y - k) for k in range(1, (2 if arms == 'crossed' else 1) * sc + 1)]
                if any(str(a).startswith('arm') and a != at(x, y) for a in above):
                    img[y][x] = DARK
    # the folded front arm: light on its upper edge, its brown line only underneath
    if arms == 'crossed':
        for y in range(W):
            for x in range(W):
                if at(x, y) == 'armFront' and img[y][x] == BROWN and at(x, y - 1) not in (None, 'armFront'):
                    img[y][x] = LIGHT
    # shade between the feet, under the hips
    for y in range(W):
        for x in range(W):
            if at(x, y) == 'hips' and solid(x, y) and y >= 54 * sc and (26 + lean) * sc <= x <= (34 + lean) * sc:
                img[y][x] = DARK
    # grey glint in the black of the ear tips (upper left, inside)
    for n in ('ear0tip', 'ear1tip'):
        pts = sorted((y, x) for y in range(W) for x in range(W) if at(x, y) == n)
        if pts:
            mid_y = pts[len(pts) // 2][0]
            row = [x for y, x in pts if y == mid_y]
            if len(row) >= 3:
                for k in range(sc * 2):
                    if mid_y + k < W and img[mid_y + k][row[0] + 1] == BLACK:
                        img[mid_y + k][row[0] + 1] = GREY

    def put(x, y, rows):
        """A face stamp placed at model coordinates."""
        stamp(img, round(x * sc), round(y * sc), rows, KEY)
    # light blobs: forehead (upper left of the head) and belly
    put(round(hx - 1.5 * d) - 8, hy - 8, blow_up(['.llll.', 'llllll', '.llll.'], sc))
    put(bx - 7, 38, blow_up(['.ll', 'lll', 'lll', '.l.'], sc))
    # face
    fx = hx + round(6 * d)
    ey = hy - 3 - (1 if chin else 0)
    near, far = (fx - 5, fx + 5) if d > 0 else (fx + 4, fx - 5)
    if d == 0:
        near, far = fx + 4, fx - 5
    nose = fx + (1 if d > 0 else -1 if d < 0 else 0)
    ny = hy + 1 - (1 if chin else 0)
    my = ny + 2
    cy = hy + 3 - (1 if chin else 0)
    near_cheek = ['.rrr.', 'prrrr', 'rrrrR', 'rrrRR', '.RRR.']
    if sc == 2:
        assert d > 0 and eyes == 'shut' and mouth == 'pout', 'the 2x face exists turned away only'
        put(near - 2, ey + 2, FACE2['shut_near'])
        put(far - 1, ey + 2, FACE2['shut_far'])
        put(nose, ny, FACE2['nose'])
        put(nose, my, FACE2['pout'])
        put(fx - 12, cy, FACE2['cheek'])
    else:
        if eyes == 'open':
            put(near - 1, ey, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'])
            if d < 0:
                put(far - 1, ey, ['.KK', 'KWK', 'KKK', 'KKK', '.g.'])
            elif d > 0:
                put(far - 1, ey, ['KK.', 'WKK', 'KKK', 'KKK', '.g.'])
            else:
                put(far - 1, ey, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'])
        elif eyes == 'half':                 # lids down: suspicious
            put(near - 1, ey + 1, ['oooo', 'KWKK', 'KKKK', '.Kg.'])
            put(far - 1, ey + 1, ['ooo', 'KWK', 'KKK', '.g.'] if d < 0 else ['ooo', 'WKK', 'KKK', '.g.'])
        elif eyes == 'squeeze':              # > <
            put(fx - 8, ey + 1, ['KK..', '..KK', 'KK..'])
            put(fx + 4, ey + 1, ['..KK', 'KK..', '..KK'])
        elif eyes == 'shut':                 # closed, lids curved down: "hmph"
            if d > 0:
                put(near - 2, ey + 2, ['KKKK', '...K'])
                put(far - 1, ey + 2, ['KKK', '..K'])
            else:
                put(near - 1, ey + 2, ['KKKK', 'K...'])
                put(far - 1, ey + 2, ['KKK', 'K..'])
        put(nose, ny, ['K'])
        if mouth == 'w':
            put(nose - 2, my, ['o.o.o', '.o.o.'])
        elif mouth == 'flat':
            put(nose - 1, my, ['ooo'])
        elif mouth == 'tight':
            put(nose - 1, my + 1, ['ooo'])
        elif mouth == 'pout':
            put(nose - 1 + (1 if d > 0 else 0), my, ['.oo.', 'o..o'])
        # cheeks: the near one whole
        if d > 0:
            put(fx - 12, cy, near_cheek)
        elif d < 0:
            put(fx + 7, cy, near_cheek)
        else:
            put(fx - 13, cy, near_cheek)
            put(fx + 8, cy, near_cheek)
    # the far cheek on the rim of the head
    far_side = 1 if d > 0 else -1 if d < 0 else 0
    if far_side:
        rows = ((DRED, RED), (DRED, RED), (DRED, DRED))
        for dy in range(3 * sc):
            outer, inner = rows[dy // sc]
            y = (cy + 1) * sc + dy
            xs = [x for x in range(W) if at(x, y) in HEAD_PARTS]
            if xs:
                x = max(xs) if far_side > 0 else min(xs)
                img[y][x] = outer
                for k in range(1, sc + 1):
                    img[y][x - far_side * k] = inner
    return img


def frames():
    """The scene 2 poses, in the order of pikachu.png."""
    return {
        'A': pose(-1, 'side', 'open', 'w', lean=-1),
        'A_twitch': pose(-1, 'side', 'open', 'w', ears='twitch', lean=-1),
        'A_sus': pose(-1, 'side', 'half', 'flat', lean=-1),
        'MID': pose(0, 'tucked', 'half', 'flat', ears='drag'),
        'B': pose(0.5, 'tucked', 'squeeze', 'tight', ears='drag', squash=0.93),
        'C_over': pose(1, 'tucked', 'shut', 'pout', ears='fling', tail_mode='lag', lean=1, chin=1),
        'C': pose(1, 'tucked', 'shut', 'pout', ears='back', lean=1, chin=1),
        'C_hmph': pose(1, 'tucked', 'shut', 'pout', ears='back', lean=1, chin=2),
        'C_flick': pose(1, 'tucked', 'shut', 'pout', ears='back', tail_mode='flick', lean=1, chin=1),
    }


def closeup_frames():
    """The 2x close-up (128x128, only the top shows in the letterbox): sulking, and
    the "hmph!" with the chin raised."""
    return {
        'CU': pose(1, 'tucked', 'shut', 'pout', ears='back', lean=1, chin=1, sc=2),
        'CU_hmph': pose(1, 'tucked', 'shut', 'pout', ears='back', lean=1, chin=2, sc=2),
    }


# ---------------------------------------------------------------- more views (scenes 4-6)
# Back, side (standing and a four-legged run cycle) and jump poses, with the same
# rules: selective outline, mass shading, the same palette, the same proportions
# (head 28 wide and 23 tall, body 22 wide, ears 17 long with black tips).

def _ear_glints(img, owner, W):
    for n in ('ear0tip', 'ear1tip'):
        pts = sorted((y, x) for y in range(W) for x in range(W) if owner[y][x] == n)
        if pts:
            mid_y = pts[len(pts) // 2][0]
            row = [x for y, x in pts if y == mid_y]
            if len(row) >= 3 and img[mid_y][row[0] + 1] == BLACK:
                img[mid_y][row[0] + 1] = GREY


def _render(f):
    colors = dict(COLORS)
    colors['Y'] = dict(COLORS['Y'], shade=(4, 4))
    img = f.render(colors)
    _ear_glints(img, f.owner, f.w)
    return img


def back_view(tail_mode='rest', ears='up'):
    """From behind: no face, the two brown stripes across the back, the tail rising
    from the small of the back (it covers part of the body), the black backs of the
    ear tips. For scene 4 (shielded, seen past RED) and scene 6 (the hill)."""
    f = Scaled(1)
    hx, hy = 31, 25
    f.ellipse('body', 31, 45, 11, 10.5)
    f.ellipse('hips', 31, 51, 13.5, 6.5)
    f.merged('body', 'hips')
    f.ellipse('footL', 23, 58.5, 4, 2.6)
    f.ellipse('footR', 39, 58.5, 4, 2.6)
    f.ellipse('armL', 19, 44.5, 2.6, 4.6, rot=0.35)
    f.ellipse('armR', 43, 44.5, 2.6, 4.6, rot=-0.35)
    tilt = {'up': 0.0, 'back': -0.15}[ears]
    for i, side in enumerate((-1, 1)):
        base = (hx + side * 8, hy - 7)
        ang = side * (0.55 + tilt)
        tip = (base[0] + math.sin(ang) * 17, base[1] - math.cos(ang) * 17)
        ear(f, 'ear%d' % i, base[0], base[1], tip[0], tip[1])
    f.ellipse('head', hx, hy, 14, 11.5)
    f.ellipse('jowl', hx, hy + 5, 15, 7.5)
    f.merged('head', 'jowl', 'body', 'hips', 'ear0', 'ear1')
    # the tail, from a brown root low in the middle of the back up to the right
    rot = {'rest': 0.0, 'flick': 0.12, 'lag': -0.12}[tail_mode]
    pts = [(29.5, 51.5), (36, 45), (33, 41), (42, 34), (38, 29), (50, 17)]
    ox, oy = pts[1]
    c, s = math.cos(rot), math.sin(rot)
    pts = pts[:2] + [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c) for x, y in pts[2:]]
    f.stroke('tail', pts, [4, 4.5, 5, 5, 8, 9])
    f.ellipse('tailroot', 29.5, 50.5, 2.3, 2.3, kind='B')
    img = _render(f)
    owner = f.owner
    # the tail: black where it lies over the body (no brown bar), its lit upper-left
    # side yellow, not all in shade
    for y in range(S):
        for x in range(S):
            if owner[y][x] != 'tail':
                continue
            if img[y][x] == BROWN and any(owner[y + dy][x + dx] not in (None, 'tail')
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                img[y][x] = BLACK
            elif y >= 48 and img[y][x] != BLACK:
                img[y][x] = BROWN
    for y in range(S):
        for x in range(S):
            if owner[y][x] == 'tail' and img[y][x] == MID and owner[y + 2][x + 2] == 'tail' \
                    and owner[y + 1][x + 1] == 'tail' and owner[y - 1][x] == 'tail':
                img[y][x] = YELLOW
    img[49][28] = DARK
    # two short, thick brown stripes low on the back, curving down at the ends
    for y0 in (40, 45):
        for x in range(22, 30):
            for dy in (0, 1):
                y = y0 + dy + (1 if x in (22, 29) else 0)
                if owner[y][x] in ('body', 'hips') and not f.edge[y][x]:
                    img[y][x] = BROWN
    stamp(img, hx - 9, hy - 8, ['.llll.', 'llllll', '.llll.'], KEY)
    return img


def side_view(eyes='open', mouth='w', ears='up', arms='front', lean=0):
    """Standing in profile, facing right: one eye, the cheek on the side of the face,
    the muzzle and the nose on the right, the tail rising behind on the left."""
    f = Scaled(1)
    hx, hy = 33, 25
    pts = [(24, 53), (18, 47), (22, 42), (13, 35), (18, 30), (6, 18)]
    f.stroke('tail', pts, [3, 4, 5, 6, 8, 9])
    f.stroke('tailroot', pts[:2] + [(20, 44.5)], [3, 4, 4], kind='B')
    f.clip('tailroot', lambda x, y: y >= 45)
    f.ellipse('footB', 27 + lean, 58.5, 4.5, 2.6)
    f.ellipse('body', 31 + lean, 45, 10, 10.5)
    f.ellipse('hips', 29 + lean, 51, 11, 6.5)
    f.merged('body', 'hips')
    f.ellipse('footF', 36 + lean, 59, 5, 2.6)
    tilt = {'up': 0.0, 'back': -0.45}[ears]
    ear(f, 'ear0', hx - 6, hy - 7, hx - 6 - 7 + tilt * 10, hy - 23 + abs(tilt) * 6)
    f.ellipse('head', hx, hy, 12.5, 11.5)
    f.ellipse('jowl', hx + 1, hy + 5, 13, 7.5)
    f.ellipse('muzzle', hx + 10, hy + 4, 5, 4.2)
    ear(f, 'ear1', hx - 1, hy - 8, hx - 1 + 3 + tilt * 12, hy - 25 + abs(tilt) * 7)
    f.merged('head', 'jowl', 'muzzle', 'body', 'hips', 'ear0', 'ear1')
    if arms == 'front':
        f.ellipse('arm', 38 + lean, 43, 2.6, 5, rot=-0.9)
    elif arms == 'up':
        f.ellipse('arm', 40 + lean, 37, 2.6, 5, rot=-2.3)
    img = _render(f)
    owner = f.owner
    for y in range(64):
        for x in range(64):
            if owner[y][x] in ('body', 'hips') and img[y][x] in (YELLOW, MID) and \
                    owner[y - 1][x] in HEAD_PARTS:
                img[y][x] = DARK if x > 30 else MID
    stamp(img, hx - 8, hy - 8, ['.llll.', 'llllll', '.llll.'], KEY)
    ex, ey = hx + 4, hy - 3
    if eyes == 'open':
        stamp(img, ex, ey, ['.KK', 'KWK', 'KKK', 'KKK', '.g.'], KEY)
    elif eyes == 'shut':
        stamp(img, ex, ey + 2, ['KKK', '..K'], KEY)
    elif eyes == 'fierce':                       # brow down: THUNDERBOLT
        stamp(img, ex - 1, ey, ['oo..', '.KKK', '.WKK', '.KKK', '..g.'], KEY)
    stamp(img, hx + 14, hy + 2, ['K'], KEY)      # nose, at the tip of the muzzle
    if mouth == 'w':
        stamp(img, hx + 10, hy + 5, ['o.o', '.o.'], KEY)
    elif mouth == 'open':
        stamp(img, hx + 9, hy + 5, ['oooo', 'omto', '.oo.'], KEY)
    stamp(img, hx + 1, hy + 3, ['.rrr.', 'prrrr', 'rrrrR', 'rrrRR', '.RRR.'], KEY)
    return img


# A four-legged bound, frame by frame: body drop (pixels down), body length change,
# back arch, head drop, tail swing (radians, + = tip up), ears laid further back, and
# the feet (x, y) of the near fore, far fore, near hind and far hind legs. The body
# goes 0, +1, +1, -2: it lands, gathers and springs, and is back where it began.
RUN = (
    # stretched: fore feet reaching, hind feet pushing off behind, long and low
    dict(dy=0, dl=0, arch=0, head=0, tail=0.00, ears=0,
         feet=((49, 59), (46, 58), (9, 58), (13, 59))),
    # the fore feet land under the chest; the hind feet swing in
    dict(dy=1, dl=-1, arch=0, head=1, tail=-0.06, ears=0,
         feet=((40, 60), (43, 59), (15, 57), (18, 58))),
    # gathered: four feet together under the belly, the back rounded, tail up
    dict(dy=1, dl=-4, arch=2, head=1, tail=0.14, ears=0,
         feet=((34, 60), (37, 60), (27, 60), (24, 59))),
    # the hind legs kick straight back, all four feet off the ground, tail down
    dict(dy=-2, dl=1, arch=0, head=0, tail=-0.14, ears=1,
         feet=((46, 56), (43, 57), (7, 57), (11, 58))),
)

# the far legs a step darker than the near ones
FAR_LEG = dict(base=MID, rim=BROWN, rim_dark=BLACK, line=BROWN, mid=DARK, shade=(3, 3))


def _leg(f, name, root, foot, w_root, w_foot, kind, bend):
    """A leg from its root in the body to the foot, bent at the middle by `bend`
    pixels (knee forward, +, or back, -), ending in a small oval paw."""
    (rx, ry), (fx, fy) = root, foot
    mx, my = (rx + fx) / 2 + bend, (ry + fy) / 2
    f.stroke(name, [(rx, ry), (mx, my), (fx, fy - 1)], [w_root, (w_root + w_foot) / 2, w_foot], kind=kind)
    f.ellipse(name + 'paw', fx + 0.5, fy - 1, 2.6, 1.8, kind=kind)
    f.merged(name, name + 'paw')


def run_frame(i):
    """A four-legged run to the right (the anime PIKACHU runs on all fours), one of
    four frames from RUN: stretch, fore-feet contact, gather, hind-leg kick."""
    k = RUN[i]
    f = Scaled(1)
    by = 47 + k['dy']
    half = 11.5 + k['dl'] / 2                      # half the body's length
    bx = 30 + k['dl'] / 2 + (1 if k['arch'] else 0)
    fore = (bx + half - 5, by + 3)                 # shoulder and hip, inside the body
    hind = (bx - half + 5, by + 2)
    # tail streaming back and up (behind everything), swinging against the body
    pts = [(bx - half + 6, by + 1), (bx - half, by - 4), (bx - half + 3, by - 8), (bx - half - 5, by - 13),
           (bx - half - 1, by - 17), (bx - half - 11, by - 26)]
    ox, oy = pts[1]
    c, s = math.cos(k['tail']), math.sin(k['tail'])
    pts = pts[:2] + [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c) for x, y in pts[2:]]
    f.stroke('tail', pts, [3, 4, 5, 6, 7, 8])
    f.stroke('tailroot', pts[:2] + [((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2)], [3, 4, 4], kind='B')
    nf, ff, nh, fh = k['feet']
    # far legs, behind the body and a step darker
    _leg(f, 'legFF', (fore[0] + 1, fore[1]), ff, 4, 3, 'F', 1 if ff[0] < fore[0] else -1)
    _leg(f, 'legFH', (hind[0] + 1, hind[1] + 1), fh, 5, 3, 'F', -2 if fh[0] < hind[0] else 2)
    f.ellipse('body', bx, by - k['arch'], half, 8 + k['arch'] / 2, rot=-0.08)
    f.ellipse('rump', bx - half + 7, by + 2 - k['arch'], 7.5, 7)
    f.merged('body', 'rump')
    # near legs: the fore leg slim, the hind leg a round haunch then the foot
    _leg(f, 'legNF', fore, nf, 4, 3.2, 'Y', 1 if nf[0] < fore[0] else -1)
    f.ellipse('haunch', hind[0], hind[1] + 1, 5.5, 6, rot=0.3)
    _leg(f, 'legNH', (hind[0] - 1, hind[1] + 3), nh, 4.5, 3.2, 'Y', -2 if nh[0] < hind[0] else 2)
    f.merged('haunch', 'legNH')
    hx, hy = bx + half + 4.5, by - 11 + k['head'] - k['arch']
    lay = k['ears']
    ear(f, 'ear0', hx - 7, hy - 5, hx - 23 - lay, hy - 13 + lay)
    f.ellipse('head', hx, hy, 11.5, 10)
    f.ellipse('muzzle', hx + 8.5, hy + 3, 4.5, 3.8)
    ear(f, 'ear1', hx - 3, hy - 7, hx - 19 - lay, hy - 17 + lay)
    f.merged('head', 'muzzle', 'body', 'rump', 'ear0', 'ear1')
    colors = dict(COLORS, F=FAR_LEG)
    img = f.render(colors)
    _ear_glints(img, f.owner, f.w)
    stamp(img, round(hx) - 7, round(hy) - 7, ['.lll.', 'lllll'], KEY)
    stamp(img, round(bx) - 6, round(by - k['arch']) - 6, ['.lll', 'llll'], KEY)
    hx, hy = round(hx), round(hy)
    stamp(img, hx + 3, hy - 3, ['.KK', 'KWK', 'KKK', '.g.'], KEY)
    stamp(img, hx + 12, hy + 1, ['K'], KEY)
    stamp(img, hx + 9, hy + 4, ['oo.', '..o'], KEY)
    stamp(img, hx - 1, hy + 2, ['.rrr.', 'prrrr', 'rrrrR', '.RRR.'], KEY)
    return img


def jump_frame(stage):
    """The THUNDERBOLT leap, facing the viewer: 'crouch' (squashed, ears back, about
    to spring), 'launch' (stretched up, arms raised), 'air' (spread in the air, tail
    up, cheeks lit), 'fall' (curled, coming down)."""
    f = Scaled(1)
    k = {'crouch': (1.07, 0.9, 4, -0.35), 'launch': (0.9, 1.12, -4, 0.1),
         'air': (1.0, 1.0, -2, 0.15), 'fall': (1.0, 0.95, 0, -0.2)}[stage]
    sx, sy, dy, ear_tilt = k
    hx, hy = 32, 24 + dy
    by = 45 + dy
    tail(f, 'flick' if stage in ('launch', 'air') else 'rest')
    if stage == 'launch':
        f.ellipse('armL', 20, by + 6, 2.6, 5, rot=0.7)
        f.ellipse('armR', 44, by + 6, 2.6, 5, rot=-0.7)
    f.ellipse('body', 32, by, 11 * sx, 10.5 * sy)
    f.ellipse('hips', 32, by + 6 * sy, 13 * sx, 6.5 * sy)
    f.merged('body', 'hips')
    if stage == 'crouch':                        # weight forward, fore paws on the ground
        f.ellipse('footL', 22, 59, 4.5, 2.5)
        f.ellipse('footR', 42, 59, 4.5, 2.5)
        f.ellipse('armL', 27, 57.5, 2.8, 3.2, rot=0.1)
        f.ellipse('armR', 37, 57.5, 2.8, 3.2, rot=-0.1)
    elif stage == 'launch':                      # toes still on the ground, arms swept back
        f.ellipse('footL', 28, 57.5, 3, 4, rot=0.15)
        f.ellipse('footR', 36, 57.5, 3, 4, rot=-0.15)
    elif stage == 'air':
        f.ellipse('footL', 20, by + 10, 3.2, 4, rot=0.8)
        f.ellipse('footR', 44, by + 10, 3.2, 4, rot=-0.8)
        f.ellipse('armL', 17, by - 3, 2.6, 5.2, rot=-1.1)
        f.ellipse('armR', 47, by - 3, 2.6, 5.2, rot=1.1)
    else:
        f.ellipse('footL', 26, by + 11, 3.5, 3, rot=0.3)
        f.ellipse('footR', 38, by + 11, 3.5, 3, rot=-0.3)
        f.ellipse('armL', 22, by + 1, 2.6, 4.5, rot=0.6)
        f.ellipse('armR', 42, by + 1, 2.6, 4.5, rot=-0.6)
    for i, side in enumerate((-1, 1)):
        base = (hx + side * 8, hy - 7)
        ang = side * (0.55 - ear_tilt)
        length = 17
        tip = (base[0] + math.sin(ang) * length, base[1] - math.cos(ang) * length)
        ear(f, 'ear%d' % i, base[0], base[1], tip[0], tip[1])
    f.ellipse('head', hx, hy, 14, 11.5)
    f.ellipse('jowl', hx, hy + 5, 15, 7.5)
    f.merged('head', 'jowl', 'body', 'hips', 'ear0', 'ear1')
    img = _render(f)
    stamp(img, hx - 9, hy - 8, ['.llll.', 'llllll', '.llll.'], KEY)
    if stage == 'crouch':                        # determined, brows down
        stamp(img, hx - 8, hy - 3, ['oo...', '.KKK.', '.WKK.', '.KKK.'], KEY)
        stamp(img, hx + 4, hy - 3, ['...oo', '.KKK.', '.WKK.', '.KKK.'], KEY)
        stamp(img, hx - 1, hy + 3, ['ooo'], KEY)
    else:
        stamp(img, hx - 8, hy - 3, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'], KEY)
        stamp(img, hx + 4, hy - 3, ['.KK.', 'KWKK', 'KKKK', 'KKKK', '.Kg.'], KEY)
        stamp(img, hx - 2, hy + 3, ['ooooo', 'omtmo', '.ooo.'], KEY)
    stamp(img, hx, hy + 1, ['K'], KEY)
    for cx in (hx - 14, hx + 9):
        stamp(img, cx, hy + 3, ['.rrr.', 'prrrr', 'rrrrR', 'rrrRR', '.RRR.'], KEY)
    return img


# Scene 5, first cut: PIKACHU at RED's scale (a quarter of his height) springing off
# his shoulder, seen from behind like him. Pixelled at 1x, not reduced from the 64x64
# model: the same shape language (black ear tips, a red cheek showing at each side of
# the head, the lightning tail with its brown root, two short stripes on the back).
# 32x32 sprites; (x, y) is where each stamp goes.
SMALL = {
    'crouch': [((5, 13), [          # squashed on the shoulder, ears laid back
        'KK................KK',
        'KKK..............KKK',
        '.oyyK..........oyyK.',
        '..oyyK........oyyK..',
        '...oyyyooooooyyyK...',
        '...oyyllyyyyyyyymK..',
        '..oyyllllyyyyyyymK..',
        '..oyyyllyyyyyyymmK..',
        '..ryyyyyyyyyyyymmr..',
        '..KmyyyyyyyyyyymmK..',
        '...KmmyyyyyyyymmK...',
        '..oyKKmmmmmmmmKKmK..',
        '.oyyyyyyyyyyyyymmK..',
        '.oyyoooyyyyyyymmmK..',
        '.oyyyyyyyyyyyymmmK..',
        '.oyyoooyyyyyyymmmK..',
        '.KmyyyyyyyyyyymmmmK.',
        'KddddKKKKKKKKKddddK.',
        '.KKKK.........KKKK..',
    ]), ((17, 18), [                # the tail, in front of the back, up to the right
        '.......oooK',
        '......oyyyK',
        '.....oyyymK',
        '....oyyymK.',
        '.....oymK..',
        '....oymK...',
        '...oymK....',
        '..oyyK.....',
        '...oyK.....',
        '..oyK......',
        '.ooK.......',
    ])],
    'leap': [((5, 2), [             # stretched up off the shoulder, arms up and out
        '...K.........K...',
        '...KK.......KK...',
        '...KK.......KK...',
        '...oyK.....oyK...',
        '...oyK.....oyK...',
        '...oyyK...oyyK...',
        '..oyyyoooooyyymK.',
        '..oyllyyyyyyyymK.',
        '.oyllllyyyyyyymK.',
        '.oyyllyyyyyyyymK.',
        '.ryyyyyyyyyyyymr.',
        '.KmyyyyyyyyyymmK.',
        'oK.KmmyyyyymmK.oK',
        'oyKoyyyyyyyyymKmK',
        '.oyyyyyyyyyyymmK.',
        '..oyyoooyyyymmK..',
        '..oyyyyyyyyymmK..',
        '..oyyoooyyyymmK..',
        '..oyyyyyyyyymmK..',
        '...KmyyyyyymmK...',
        '....KmmmmmmK.....',
        '....oyK..omK.....',
        '....oyK..omK.....',
        '....KdK..KdK.....',
    ]), ((13, 20), [                # the tail trailing below, flag last
        'ooK.....',
        '.omK....',
        '..omK...',
        '.oyyK...',
        '..oymK..',
        '...oyymK',
        '....oyymK',
        '.....KKKK',
    ])],
}


def small_frames():
    """The small PIKACHU's two poses as 32x32 frames."""
    out = {}
    for name, layers in SMALL.items():
        img = [[0] * 32 for _ in range(32)]
        for (x0, y0), rows in layers:
            for dy, r in enumerate(rows):
                for dx, ch in enumerate(r):
                    if ch != '.':
                        img[y0 + dy][x0 + dx] = KEY[ch]
        out[name] = img
    return out


def model_views():
    """Every view on the model sheet, by name."""
    out = {'front A': pose(-1, 'side', 'open', 'w', lean=-1),
           'front C': pose(1, 'tucked', 'shut', 'pout', ears='back', lean=1, chin=1),
           'back': back_view(), 'back, tail flick': back_view('flick'),
           'side': side_view(), 'side, ears back': side_view('open', 'open', 'back', 'up')}
    for i in range(len(RUN)):
        out['run %d' % i] = run_frame(i)
    for st in ('crouch', 'launch', 'air', 'fall'):
        out['jump: ' + st] = jump_frame(st)
    return out
