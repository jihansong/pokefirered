#!/usr/bin/env python3
"""N, the young man who hears POKéMON (Thunder Yellow v0.6.0): the FR/LG
COOLTRAINER's field sprite and battle picture with new colors - pale green hair,
a white shirt and khaki trousers. Only palettes are made; the pictures are the
FR/LG ones.

Writes graphics/object_events/palettes/n.pal and graphics/trainers/palettes/n.pal
(and, with --preview DIR, recolored PNGs to look at)."""
import os, sys
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HAIR = [(206, 239, 198), (148, 206, 156), (82, 139, 98)]
FIELD = {8: HAIR[0], 9: HAIR[1], 10: (74, 106, 82), 11: (246, 246, 246), 12: (189, 189, 205), 13: (98, 82, 57)}
BATTLE = {8: HAIR[0], 9: HAIR[1], 10: HAIR[2], 11: (238, 238, 238), 12: (197, 172, 123), 13: (131, 106, 65)}


def recolor(png, changes):
    im = Image.open(png)
    pal = im.getpalette()[:48]
    cols = [tuple(pal[i * 3:i * 3 + 3]) for i in range(16)]
    for i, c in changes.items():
        cols[i] = c
    return im, cols


def write_pal(path, cols):
    with open(path, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n16\n' + ''.join('%d %d %d\n' % c for c in cols))


jobs = [('graphics/object_events/pics/people/cooltrainer_m.png', FIELD, 'graphics/object_events/palettes/n.pal'),
        ('graphics/trainers/front_pics/cool_trainer_m_front_pic.png', BATTLE, 'graphics/trainers/palettes/n.pal')]
for png, ch, out in jobs:
    im, cols = recolor(f'{R}/{png}', ch)
    write_pal(f'{R}/{out}', cols)
    if '--preview' in sys.argv:
        d = sys.argv[sys.argv.index('--preview') + 1]
        im = im.copy()
        im.putpalette([v for c in cols for v in c])
        im.convert('RGB').resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(d, out.replace('/', '_') + '.png'))
print('ok')
