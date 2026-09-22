#!/usr/bin/env python3
"""Rebuild the JESSIE & JAMES trainer picture from FR/LG's TEAM ROCKET grunts.

FR/LG double battles show one picture for both trainers, so, like the Twins or the
Young Couple, both stand in one 64x64 frame: JAMES (the male grunt) on the left and
JESSIE (the female grunt) in front of him on the right, each moved 12 pixels
outwards so their faces clear each other. Their black uniforms become the white
ones, gloves and boots black; the red R stays. The caps come off and the hair is
put on from the old (Yellow based) picture, tools/data/jessie_james_yellow_pic.png:
JESSIE's long magenta hair, JAMES's lavender hair, moved onto the grunts' faces and
reshaded in two tones lit from the upper left. Bangs are drawn over the face, the
rest of the hair behind the body.
"""
import os
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
GRUNT_F = FR + '/graphics/trainers/front_pics/rocket_grunt_f_front_pic.png'
GRUNT_M = FR + '/graphics/trainers/front_pics/rocket_grunt_m_front_pic.png'
OLD = FR + '/tools/data/jessie_james_yellow_pic.png'
OUT_PIC = FR + '/graphics/trainers/front_pics/jessie_james_front_pic.png'
OUT_PAL = FR + '/graphics/trainers/palettes/jessie_james.pal'

PALETTE = [
    (115, 197, 164),  # 0 transparent
    (255, 222, 222),  # 1 skin light   (grunt)
    (230, 180, 164),  # 2 skin         (grunt)
    (197, 148, 139),  # 3 skin shadow  (grunt)
    (115, 90, 74),    # 4 brown lines  (grunt)
    (205, 205, 222),  # 5 white uniform shade
    (96, 88, 176),    # 6 lavender dark (JAMES)
    (160, 152, 232),  # 7 lavender      (JAMES)
    (164, 74, 65),    # 8 R dark        (grunt)
    (213, 98, 90),    # 9 R             (grunt)
    (240, 120, 176),  # 10 magenta      (JESSIE)
    (0, 0, 0),        # 11 outline
    (57, 57, 74),     # 12 gloves/boots dark (grunt)
    (82, 82, 106),    # 13 gloves/boots      (grunt)
    (176, 48, 104),   # 14 magenta dark (JESSIE)
    (255, 255, 255),  # 15 white
]
WHITE, SHADE, LAV_D, LAV, MAG, MAG_D, OUTLINE = 15, 5, 6, 7, 10, 14, 11

# grunt palette index -> new index
GRUNT_MAP = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 11: 11, 15: 15,
             13: WHITE, 12: SHADE, 7: WHITE,     # black uniform -> white
             14: 13, 6: 12, 5: 13,               # grey gloves and boots -> black
             8: 8, 9: 9, 10: 9}                  # the red R

# per character: the grunt, its shift, the rows of its cap, the hair color in the old
# picture, where the hair goes (offset from the old picture), the row that ends the bangs
CHARS = {
    'JAMES':  {'grunt': GRUNT_M, 'dx': -12, 'cap': (4, 13, 19, 36), 'old_hair': 5, 'hair_dx': -1, 'hair_dy': -2,
               'light': LAV, 'dark': LAV_D, 'bangs_until': 15, 'boots_from': 53},
    'JESSIE': {'grunt': GRUNT_F, 'dx': 12, 'cap': (4, 13, 25, 42), 'old_hair': 6, 'hair_dx': 4, 'hair_dy': -2,
               'light': MAG, 'dark': MAG_D, 'bangs_until': 15, 'boots_from': 46, 'red_hair_until': 22},
}


def grunt_body(ch):
    src = Image.open(ch['grunt'])
    body = {}
    y0, y1, x0, x1 = ch['cap']
    for y in range(64):
        for x in range(64):
            c = src.getpixel((x, y))
            if c == 0:
                continue
            if y0 <= y <= y1 and x0 <= x <= x1:
                continue                        # the cap comes off
            tx = x + ch['dx']
            if not 0 <= tx < 64:
                continue
            near = {src.getpixel(n) for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if 0 <= n[0] < 64 and 0 <= n[1] < 64}
            if y <= ch['cap'][1] + 3 and ch['cap'][2] <= x <= ch['cap'][3] and c in (12, 13, 7, 14):
                new = ch['dark'] if c in (12, 13) else ch['light']   # the cap's brim: hair now
            elif y >= ch['boots_from'] and c in (13, 12, 7):
                new = {13: 12, 12: 12, 7: 13}[c]            # black boots
            elif c == 7 and near & {14, 5, 6}:
                new = 13                                    # the light edge of a glove
            elif c in (8, 9, 10) and y <= ch.get('red_hair_until', -1):
                new = MAG_D if c == 8 else MAG              # the grunt's red hair under the cap
            else:
                new = GRUNT_MAP.get(c, c)
            body[(tx, y)] = new
    return body


def hair(ch, old):
    """The old picture's hair of this color plus its outline, moved and reshaded."""
    want = ch['old_hair']
    mask = {(x, y) for y in range(64) for x in range(64) if old.getpixel((x, y)) == want}
    outline = set()
    for (x, y) in mask:
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= n[0] < 64 and 0 <= n[1] < 64 and n not in mask and old.getpixel(n) in (1, 11):
                outline.add(n)
    out = {}
    for (x, y) in mask | outline:
        tx, ty = x + ch['hair_dx'], y + ch['hair_dy']
        if not (0 <= tx < 64 and 0 <= ty < 64):
            continue
        if (x, y) in outline:
            out[(tx, ty)] = OUTLINE
        else:
            lower_right = any(n in outline or old.getpixel(n) in (1, 11) for n in ((x + 1, y), (x, y + 1)) if 0 <= n[0] < 64 and 0 <= n[1] < 64)
            out[(tx, ty)] = ch['dark'] if lower_right else ch['light']
    return out


def main():
    old = Image.open(OLD)
    canvas = {}
    for name in ('JAMES', 'JESSIE'):          # JESSIE stands in front
        ch = CHARS[name]
        body, hr = grunt_body(ch), hair(ch, old)
        for p, c in hr.items():               # hair behind the body...
            canvas[p] = c
        for p, c in body.items():
            canvas[p] = c
        for p, c in hr.items():               # ...except the bangs, over the face
            if p[1] <= ch['bangs_until']:
                canvas[p] = c
        # close gaps between the hair and the head where the cap used to be
        y0, y1, x0, x1 = ch['cap']
        for y in range(y0, y1 + 4):
            row = [x + ch['dx'] for x in range(x0, x1 + 1)]
            filled = [x for x in row if (x, y) in canvas]
            if len(filled) < 2:
                continue
            for x in range(min(filled) + 1, max(filled)):
                if (x, y) not in canvas:
                    canvas[(x, y)] = ch['light']
    img = Image.new('P', (64, 64), 0)
    img.putpalette([v for c in PALETTE for v in c])
    for (x, y), c in canvas.items():
        img.putpixel((x, y), c)
    img.save(OUT_PIC)
    lines = ['JASC-PAL', '0100', '16'] + ['%d %d %d' % c for c in PALETTE]
    open(OUT_PAL, 'w', newline='\r\n').write('\n'.join(lines) + '\n')
    print(f'{OUT_PIC}: colors {sorted(set(img.getdata()))}')


if __name__ == '__main__':
    main()
