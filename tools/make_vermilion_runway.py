#!/usr/bin/env python3
"""Lay out the Vermilion City airport grounds: terminal, runway, aprons, fences.

v0.5 layout (about twice the v0.3.0 grounds; the map stays 48x40):

- the terminal is eight blocks wide again (x=31..38, y=9..12), as it was
  before v0.3.0 narrowed it to six; the door and its warp stay at (35,12);
- the forest north of the airport is cut back to its top two rows, and the
  forest east of it to its last two columns (x=46..47);
- the runway (x=42..45, y=3..12) runs north with its centre line on the left
  edge of column 44 (src/airport_flyover.c flies along it);
- a taxiway one block wide (x=41) runs along the runway's west side from the
  north apron (x=31..41, y=2..5) down to the gate apron beside the terminal
  (x=39..41, y=10..12), with yellow lines to the parking stands;
- the lawn north of the terminal is the fenced viewing spot (x=30..39,
  y=7..8). From its east end (x=39) the camera shows the whole runway and
  every parked plane.

Everything in the airport's rectangle (x=30..47, y=0..13) is written from the
tables below, so running it twice is a no-op. Run tools/make_runway_tiles.py
first: it adds the runway metatiles used here.
"""
import json, os, struct, sys

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.dont_write_bytecode = True
sys.path.insert(0, FR + '/tools')
import make_runway_tiles as runway  # noqa: E402

LAYOUT = 'LAYOUT_VERMILION_CITY'
MT = {name: runway.SECONDARY_TILE_BASE + runway.FIRST_METATILE + i
      for i, (name, _) in enumerate(runway.METATILES)}

# blocks the city already has: (metatile, collision, elevation)
GRASS = (1, 0, 3)
FENCE_H, FENCE_V, FENCE_TOP, FENCE_END = 231, 244, 239, 247
SIGN_POST = 2                       # the city sign on the forecourt fence, (33,6)
# forest: plain trees alternate by column (even, odd) and by row (even, odd);
# the row along the forest's bottom edge and the column along its left edge
# have their own blocks
TREE = {0: (28, 29), 1: (20, 21)}
TREE_BOTTOM = (36, 37)
TREE_LEFT = {0: 30, 1: 22}

# the terminal, eight blocks wide (its own metatiles; 831 is the second copy
# of the right-hand window column's bottom block)
TERMINAL = [
    [808, 809, 809, 810, 811, 812, 812, 813],
    [814, 815, 815, 816, 817, 818, 818, 819],
    [820, 821, 821, 822, 823, 824, 824, 825],
    [826, 827, 828, 829, 830, 831, 831, 832],
]
TERMINAL_X, TERMINAL_Y = 31, 9
DOOR_X, DOOR_Y = 35, 12

X0, X1, Y0, Y1 = 30, 47, 0, 13     # the rectangle this tool owns
RUNWAY_X, RUNWAY_Y0, RUNWAY_Y1 = 42, 3, 12
ATTRS = FR + '/data/tilesets/secondary/vermilion_city/metatile_attributes.bin'


def tree(x, y, bottom=False, left=False):
    if bottom:
        return (TREE_BOTTOM[x % 2], 1, 0)
    if left:
        return (TREE_LEFT[y % 2], 1, 0)
    return (TREE[y % 2][x % 2], 1, 0)


def airside(name):
    return (MT[name], 1, 0)


def fence(block, elevation=0):
    return (block, 1, elevation)


def plan():
    """The airport's blocks as {(x, y): (metatile, collision, elevation)}."""
    g = {}
    # forest: two rows along the top, two columns down the east side
    for x in range(X0, X1 + 1):
        g[(x, 0)] = tree(x, 0)
        g[(x, 1)] = tree(x, 1, bottom=x < 46)
    for y in range(2, Y1 + 1):
        g[(46, y)] = tree(46, y, left=True)
        g[(47, y)] = tree(47, y)
    # grass everywhere else to begin with; all of the airside is out of bounds
    for y in range(2, Y1 + 1):
        for x in range(X0, 46):
            g[(x, y)] = (GRASS[0], 1, 0)

    # the runway
    rows = {3: ['CORNER_TL', 'EDGE_T', 'EDGE_T', 'CORNER_TR'],
            4: ['EDGE_L', 'THRESHOLD', 'THRESHOLD', 'EDGE_R'],
            5: ['EDGE_L', 'NUM_0', 'NUM_1', 'EDGE_R'],
            11: ['EDGE_L', 'THRESHOLD', 'THRESHOLD', 'EDGE_R'],
            12: ['CORNER_BL', 'EDGE_B', 'EDGE_B', 'CORNER_BR']}
    for y in range(RUNWAY_Y0, RUNWAY_Y1 + 1):
        row = rows.get(y) or ['EDGE_L', 'ASPHALT', 'DASH' if y % 2 == 0 else 'ASPHALT', 'EDGE_R']
        for dx, name in enumerate(row):
            g[(RUNWAY_X + dx, y)] = airside(name)

    # the north apron, x=31..41, y=2..5, with the stand line along the top of
    # row 5 that its two remote stands are on
    for x in range(31, 42):
        for y in range(2, 6):
            left, right, top, bottom = x == 31, x == 41, y == 2, y == 5
            if top:
                name = 'CORNER_TL' if left else 'CORNER_TR' if right else 'EDGE_T'
            elif right:
                name = 'TAXI_T_R' if bottom else 'EDGE_RP'
            elif bottom:
                name = 'CORNER_BL' if left else 'TAXI_H_B'
            else:
                name = 'EDGE_LP' if left else 'ASPHALT'
            g[(x, y)] = airside(name)
    # the taxiway down the runway's west side, one block wide
    for y in range(6, 10):
        g[(41, y)] = airside('TAXI_V_1W')
    # the gate apron beside the terminal, x=39..41, y=10..12, with a nose-in
    # stand facing the terminal on the top of row 11
    gate = {10: ['CORNER_TL', 'EDGE_T', 'TAXI_V_R'],
            11: ['EDGE_LP', 'TAXI_H', 'TAXI_T_R'],
            12: ['CORNER_BL', 'EDGE_B', 'TAXI_END_BR']}
    for y, row in gate.items():
        for dx, name in enumerate(row):
            g[(39 + dx, y)] = airside(name)

    # the terminal
    for dy, row in enumerate(TERMINAL):
        for dx, block in enumerate(row):
            x, y = TERMINAL_X + dx, TERMINAL_Y + dy
            g[(x, y)] = (block, 0 if (x, y) == (DOOR_X, DOOR_Y) else 1, 0)
    # the lawn beside it and in front of it
    for y in range(9, 14):
        g[(30, y)] = GRASS
    for x in range(31, 39):
        g[(x, 13)] = GRASS

    # The viewing spot: the lawn north of the terminal, fenced off from the
    # airside by the forecourt fence along y=6, which turns south at x=40 and
    # back west along y=9 to the terminal roof.
    for x in range(30, 40):
        g[(x, 6)] = fence(SIGN_POST if x == 33 else FENCE_H)
        g[(x, 7)] = GRASS
        g[(x, 8)] = GRASS
    g[(40, 6)] = fence(FENCE_TOP)
    g[(40, 7)] = fence(FENCE_V, 3)
    g[(40, 8)] = fence(FENCE_V, 3)
    g[(40, 9)] = fence(FENCE_END, 3)
    g[(39, 9)] = fence(FENCE_H, 3)
    # the airside's south fence, meeting the fence that runs on down to y=15
    for x in range(39, 46):
        g[(x, 13)] = fence(FENCE_V if x == 41 else FENCE_H, 3)
    return g


def main():
    lay = next(l for l in json.load(open(FR + '/data/layouts/layouts.json'))['layouts']
               if l.get('id') == LAYOUT)
    w, h = lay['width'], lay['height']
    path = FR + '/' + lay['blockdata_filepath']
    blocks = list(struct.unpack('<%dH' % (w * h), open(path, 'rb').read()))
    for (x, y), (block, collision, elevation) in plan().items():
        assert X0 <= x <= X1 and Y0 <= y <= Y1
        blocks[y * w + x] = (block & 0x3FF) | (collision << 10) | (elevation << 12)
    open(path, 'wb').write(struct.pack('<%dH' % (w * h), *blocks))
    # The terminal's blocks were copied from the POKeMON MART building and kept its
    # MB_POKEMART_SIGN behavior, so reading the terminal wall printed the mart's
    # sign text. Only the terminal uses these blocks, so clear them to MB_NORMAL.
    attrs = bytearray(open(ATTRS, 'rb').read())
    for block in {b for row in TERMINAL for b in row}:
        attrs[(block - 640) * 4] = 0
    open(ATTRS, 'wb').write(attrs)
    print(f'{LAYOUT}: terminal 8x4 at x={TERMINAL_X}..{TERMINAL_X + 7}, runway x={RUNWAY_X}..'
          f'{RUNWAY_X + 3} y={RUNWAY_Y0}..{RUNWAY_Y1}, airside x=31..45 y=2..12')


if __name__ == '__main__':
    main()
