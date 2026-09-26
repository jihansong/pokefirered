"""The opening's RED (the player, FR/LG design): a model for scenes 1, 4 and 5.

The FR/LG player as drawn in his trainer pictures (graphics/trainers/front_pics/
red_front_pic.png, back_pics/red_back_pic.png) and overworld sprite: red cap with a
white front and a red brim, black hair, red vest with a white collar over a dark
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
SKIN_L, SKIN, SKIN_S, SKIN_O = 1, 2, 3, 4
JEAN_L, JEAN, JEAN_S, NAVY = 5, 6, 7, 8
GREYW, BAG, BAG_S, RED_L, RED, WHITE, BLACK = 9, 10, 11, 12, 13, 14, 15
S = 64

COLORS = {
    'S': dict(base=SKIN, rim=SKIN_O, rim_dark=BLACK, line=SKIN_O, mid=SKIN_S, shade=(2, 2)),
    'R': dict(base=RED_L, rim=RED, rim_dark=BLACK, line=RED, mid=RED, shade=(3, 3)),
    'J': dict(base=JEAN, rim=JEAN_S, rim_dark=NAVY, line=JEAN_S, mid=JEAN_S, shade=(2, 3)),
    'H': dict(base=NAVY, rim=BLACK, rim_dark=BLACK),
    'D': dict(base=NAVY, rim=BLACK, rim_dark=BLACK, line=BLACK),        # dark shirt
    'B': dict(base=BAG, rim=BAG_S, rim_dark=BLACK, line=BAG_S, mid=BAG_S, shade=(3, 3)),
    'W': dict(base=WHITE, rim=GREYW, rim_dark=BLACK, line=GREYW, mid=GREYW, shade=(2, 2)),
}
KEY = {'K': BLACK, 'W': WHITE, 's': SKIN_S, 'o': SKIN_O, 'l': SKIN_L, 'n': NAVY, 'w': GREYW,
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
#  far upper arm, far forearm, body bob)
RUN = ((32, 12, -34, -72, -42, -8, 42, 100, 0),
       (4, -12, 16, -88, -14, 30, 14, 76, -2),
       (-34, -72, 32, 12, 42, 100, -42, -8, 0),
       (16, -88, 4, -12, 14, 76, -14, 30, -2))


def side_run(i):
    """Running to the right, frame i of 4."""
    nt, ns, ft, fs, nu, nf, fu, ff, bob = RUN[i]
    f = Figure(S, S)
    hx, hy = 30, 38 + bob            # hip
    sx, sy = 33, 22 + bob            # shoulder (leaning into the run)
    # far limbs, behind the body
    _limb(f, 'farArm', sx - 1, sy + 1, fu, ff, 8, 7, 4, 3.5, 'S')
    fx, fy = _limb(f, 'farLeg', hx - 1, hy, ft, fs, 11, 11, 6, 5, 'J')
    f.ellipse('farShoe', fx + 2, fy + 1, 4, 2.4, kind='R', rot=math.radians(-fs) * 0.3)
    # backpack on the back, the torso (dark shirt, red vest), the head
    f.ellipse('bag', sx - 8, sy + 8, 6, 8, kind='B', rot=-0.15)
    f.ellipse('shirt', (hx + sx) / 2 + 1, (hy + sy) / 2, 6.5, 10, kind='D', rot=-0.15)
    f.ellipse('vest', (hx + sx) / 2, (hy + sy) / 2 - 0.5, 6, 9.5, kind='R', rot=-0.15)
    f.stroke('strap', [(sx - 3, sy - 2), (sx + 1, sy + 9)], [2, 2], kind='B')
    f.ellipse('hipsJ', hx, hy + 1, 5.5, 4, kind='J')
    nx, ny = _limb(f, 'nearLeg', hx + 1, hy, nt, ns, 11, 11, 6, 5, 'J')
    f.ellipse('nearShoe', nx + 2, ny + 1, 4.2, 2.5, kind='R', rot=math.radians(-ns) * 0.3)
    f.ellipse('head', sx + 3, sy - 8, 7, 7.5, kind='S')
    f.ellipse('hair', sx - 1, sy - 8, 5.5, 6, kind='H')
    f.ellipse('cap', sx + 3, sy - 12, 7.5, 5, kind='R')
    f.clip('cap', lambda x, y: y <= sy - 11)
    f.poly('brim', [(sx + 6, sy - 12), (sx + 14, sy - 11), (sx + 14, sy - 9.5), (sx + 5, sy - 9.5)], kind='R')
    f.ellipse('capfront', sx + 7, sy - 13.5, 3, 2.5, kind='W')
    f.clip('capfront', lambda x, y: y <= sy - 12)
    _limb(f, 'nearArm', sx + 1, sy + 1, nu, nf, 8, 7, 4.2, 3.6, 'S')
    f.ellipse('sleeve', sx + 1, sy + 2, 3, 3, kind='D')
    f.merged('head', 'hair')
    img = f.render(COLORS)
    # face: eye, brow shadow under the brim, ear
    ex, ey = round(sx + 6), round(sy - 9)
    stamp(img, ex, ey, ['K', 'K'], KEY)
    stamp(img, round(sx + 1), round(sy - 8), ['oo', 'so'], KEY)
    stamp(img, round(sx + 3), round(sy - 11), ['nnnnnn'], KEY)
    # the shoes' white toe caps
    for name, px, py in (('nearShoe', nx, ny), ('farShoe', fx, fy)):
        stamp(img, round(px + 3), round(py), ['W', 'W'], {'W': WHITE})
    return img


def back_view(pose='stand'):
    """From behind. 'stand': feet apart, arms down. 'shield': hunched over PIKACHU,
    elbows out, holding it to his chest (scene 4); PIKACHU's ear tips show over his
    right shoulder, its tail beside his left arm."""
    f = Figure(S, S)
    hunch = 3 if pose == 'shield' else 0
    cx = 32
    sy = 22 + hunch
    for side in (-1, 1):
        lx = cx + side * 4
        ex, ey = _limb(f, 'leg%d' % side, lx, 38 + hunch // 2, side * 6, side * 2, 11, 11 - hunch // 2, 6.5, 5.5, 'J')
        f.ellipse('shoe%d' % side, ex, ey + 1, 3.5, 2.5, kind='R')
    if pose == 'shield':
        for side in (-1, 1):             # elbows out, forearms wrapped round in front
            _limb(f, 'arm%d' % side, cx + side * 9, sy + 2, side * 70, -side * 40, 8, 5, 4.2, 3.6, 'S')
        # PIKACHU held to his chest: its ears over his right shoulder, its tail
        f.stroke('pEar0', [(cx + 9, sy - 1), (cx + 14, sy - 10)], [3.5, 1.5], kind='Y')
        f.stroke('pEar1', [(cx + 12, sy), (cx + 19, sy - 6)], [3.5, 1.5], kind='Y')
        f.stroke('pTail', [(cx - 10, sy + 10), (cx - 16, sy + 4), (cx - 13, sy + 1), (cx - 19, sy - 5)],
                 [3, 4, 5, 6], kind='Y')
    else:
        for side in (-1, 1):
            _limb(f, 'arm%d' % side, cx + side * 9, sy + 2, side * 12, side * 4, 8, 7, 4.2, 3.6, 'S')
    f.ellipse('shirt', cx, 31 + hunch, 9.5, 10, kind='D')
    f.ellipse('vest', cx, 31 + hunch, 9, 9.5, kind='R')
    f.ellipse('hipsJ', cx, 38 + hunch // 2, 8, 4, kind='J')
    f.ellipse('bag', cx, 32 + hunch, 7.5, 8.5, kind='B')
    f.stroke('strapL', [(cx - 6, sy), (cx - 5, sy + 7)], [2, 2], kind='B')
    f.stroke('strapR', [(cx + 6, sy), (cx + 5, sy + 7)], [2, 2], kind='B')
    f.ellipse('head', cx, sy - 8 + hunch // 2, 7.5, 7.5, kind='S')
    f.ellipse('hair', cx, sy - 10 + hunch // 2, 7.5, 5, kind='H')     # under the cap, above the neck
    f.ellipse('cap', cx, sy - 12 + hunch // 2, 8, 5.5, kind='R')
    f.clip('cap', lambda x, y: y <= sy - 11 + hunch // 2)
    f.merged('head', 'hair')
    colors = dict(COLORS)
    colors['Y'] = dict(base=12, rim=13, rim_dark=BLACK)
    img = f.render(dict(COLORS, Y=dict(base=BAG, rim=BAG_S, rim_dark=BLACK)))
    # the cap's back strap, the backpack's flap and seam, the black ear tips
    cy = sy - 11 + hunch // 2
    stamp(img, cx - 2, cy - 1, ['wwww'], KEY)
    stamp(img, cx - 5, 30 + hunch, ['sssssssssss'], {'s': BAG_S})
    stamp(img, cx - 5, 31 + hunch, ['...KKKKK...'], {'K': BAG_S})
    if pose == 'shield':
        for (x, y) in ((cx + 14, sy - 10), (cx + 13, sy - 9), (cx + 19, sy - 6), (cx + 18, sy - 6)):
            if 0 <= x < S and 0 <= y < S and img[y][x]:
                img[y][x] = BLACK
    return img


def model_views():
    out = {}
    for i in range(len(RUN)):
        out['run %d' % i] = side_run(i)
    out['back'] = back_view('stand')
    out['back, shielding'] = back_view('shield')
    return out
