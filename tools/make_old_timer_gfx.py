#!/usr/bin/env python3
"""The OLD-TIMER in VIRIDIAN FOREST (Thunder Yellow v0.6.0) looks like he stepped
out of a Game Boy: the BUG CATCHER's field sprite and battle picture, recolored in
the four greens of the original Game Boy screen by brightness. Only palettes are
made; the pictures are the FR/LG ones.

Writes graphics/object_events/palettes/old_timer.pal (from npc_green.pal, the
BUG CATCHER's field palette) and graphics/trainers/palettes/old_timer.pal."""
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# darkest to lightest, 5-bit-friendly values of the DMG screen greens
GREENS = [(16, 57, 16), (49, 98, 49), (139, 172, 16), (156, 189, 16)]


def read_pal(path):
    lines = open(path).read().split('\n')
    return [tuple(int(v) for v in l.split()) for l in lines[3:3 + int(lines[2])]]


def write_pal(path, cols):
    with open(path, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n%d\n' % len(cols) + ''.join('%d %d %d\n' % c for c in cols))


def dmg(cols):
    out = [cols[0]]  # index 0 is transparent
    for r, g, b in cols[1:]:
        y = 0.299 * r + 0.587 * g + 0.114 * b
        out.append(GREENS[sum(y >= t for t in (70, 130, 200))])
    return out


write_pal(R + '/graphics/object_events/palettes/old_timer.pal', dmg(read_pal(R + '/graphics/object_events/palettes/npc_green.pal')))
write_pal(R + '/graphics/trainers/palettes/old_timer.pal', dmg(read_pal(R + '/graphics/trainers/palettes/bug_catcher.pal')))
print('ok')
