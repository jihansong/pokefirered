#!/usr/bin/env python3
"""The silent TRAINER on the snowbound summit (Thunder Yellow v0.6.0): the FR/LG
RED field sprite and battle picture with his red jacket and cap dyed charcoal and
his jeans near-black, so he never looks like the player. Only palettes are made.

Writes graphics/object_events/palettes/summit_trainer.pal (from player.pal) and
graphics/trainers/palettes/summit_trainer.pal (from red.pal)."""
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FIELD = {11: (98, 98, 115), 12: (65, 65, 82), 8: (41, 41, 49), 6: (32, 32, 41), 7: (74, 74, 90)}
BATTLE = {12: (106, 106, 123), 13: (65, 65, 82), 5: (90, 98, 115), 6: (57, 65, 82), 7: (41, 49, 57), 8: (24, 24, 33)}


def read_pal(p):
    l = open(p).read().split('\n')
    return [tuple(int(v) for v in x.split()) for x in l[3:3 + int(l[2])]]


def write_pal(p, cols):
    with open(p, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n%d\n' % len(cols) + ''.join('%d %d %d\n' % c for c in cols))


for src, ch, dst in [('graphics/object_events/palettes/player.pal', FIELD, 'graphics/object_events/palettes/summit_trainer.pal'),
                     ('graphics/trainers/palettes/red.pal', BATTLE, 'graphics/trainers/palettes/summit_trainer.pal')]:
    cols = read_pal(f'{R}/{src}')
    for i, c in ch.items():
        cols[i] = c
    write_pal(f'{R}/{dst}', cols)
print('ok')
