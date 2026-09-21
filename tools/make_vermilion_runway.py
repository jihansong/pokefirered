#!/usr/bin/env python3
"""Lay out the Vermilion City airport grounds: terminal, runway, apron, fence.

The terminal loses its two duplicated window columns (8x4 -> 6x4 blocks, the
"AIRPORT" sign and the door stay where they are), and the strip that frees up
plus the lawn east of it becomes the airside: a runway running north, a
taxiway and an apron with room for two parked planes, fenced off from the
forecourt.

Everything is written from the table below, so running it twice is a no-op.
Run tools/make_runway_tiles.py first: it adds the metatiles used here.
"""
import json, os, struct

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
LAYOUT = 'LAYOUT_VERMILION_CITY'

# blocks the city already has
GRASS, FENCE_H = 1, 231
# the terminal, from left to right, top to bottom (its own metatiles)
TERMINAL = [
    [808, 809, 810, 811, 812, 813],
    [814, 815, 816, 817, 818, 819],
    [820, 821, 822, 823, 824, 825],
    [826, 827, 828, 829, 830, 832],
]
DOOR_X, DOOR_Y = 35, 12

# the runway metatiles tools/make_runway_tiles.py appends
ASPHALT, DASH, STRIPE_L, STRIPE_R, THRESHOLD, TAXI, NUM_0, NUM_1 = range(833, 841)
EDGE_L, EDGE_R, EDGE_T, EDGE_B = range(841, 845)
CORNER_TL, CORNER_TR, CORNER_BL, CORNER_BR = range(845, 849)
EDGE_LP, EDGE_RP = 849, 850          # apron edges, without the runway stripe

# the airside, x = 37..40
AIRSIDE_X = 37
AIRSIDE = {
    1:  [CORNER_TL, EDGE_T,    EDGE_T,    CORNER_TR],
    2:  [EDGE_L,    THRESHOLD, THRESHOLD, EDGE_R],
    3:  [EDGE_L,    NUM_0,     NUM_1,     EDGE_R],
    4:  [EDGE_L,    ASPHALT,   DASH,      EDGE_R],
    5:  [EDGE_L,    ASPHALT,   ASPHALT,   EDGE_R],
    6:  [EDGE_L,    ASPHALT,   DASH,      EDGE_R],
    7:  [EDGE_L,    ASPHALT,   ASPHALT,   EDGE_R],
    8:  [EDGE_L,    ASPHALT,   DASH,      EDGE_R],
    9:  [EDGE_LP,   TAXI,      ASPHALT,   EDGE_RP],
    10: [EDGE_LP,   TAXI,      ASPHALT,   EDGE_RP],
    11: [EDGE_LP,   TAXI,      ASPHALT,   EDGE_RP],
    12: [CORNER_BL, EDGE_B,    EDGE_B,    CORNER_BR],
    13: [FENCE_H,   FENCE_H,   FENCE_H,   FENCE_H],
}


def main():
    lay = next(l for l in json.load(open(FR + '/data/layouts/layouts.json'))['layouts']
               if l.get('id') == LAYOUT)
    w, h = lay['width'], lay['height']
    path = FR + '/' + lay['blockdata_filepath']
    blocks = list(struct.unpack('<%dH' % (w * h), open(path, 'rb').read()))

    def put(x, y, block, collision=1, elevation=None):
        old = blocks[y * w + x]
        if elevation is None:
            elevation = (old >> 12) & 0xF
        blocks[y * w + x] = (block & 0x3FF) | (collision << 10) | (elevation << 12)

    # the terminal, six blocks wide now
    for dy, row in enumerate(TERMINAL):
        y = 9 + dy
        for dx, block in enumerate(row):
            x = 31 + dx
            put(x, y, block, 0 if (x, y) == (DOOR_X, DOOR_Y) else 1)

    # the lawn the two dropped columns leave behind is paved over below,
    # so only the rows outside the airside need clearing
    for y in range(9, 13):
        for x in range(AIRSIDE_X, AIRSIDE_X + 4):
            if y not in AIRSIDE:
                put(x, y, GRASS, 0)

    for y, row in AIRSIDE.items():
        for dx, block in enumerate(row):
            put(AIRSIDE_X + dx, y, block, 1)

    # the forecourt fence used to run along y=6; it now ends where the runway starts
    open(path, 'wb').write(struct.pack('<%dH' % (w * h), *blocks))
    print(f'{LAYOUT}: terminal 6x4, airside x={AIRSIDE_X}..{AIRSIDE_X + 3} y=1..13')


if __name__ == '__main__':
    main()
