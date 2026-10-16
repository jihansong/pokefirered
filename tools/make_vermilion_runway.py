#!/usr/bin/env python3
"""Lay out the Vermilion City airport grounds: terminal, runway, aprons, fences.

The map stays 48x40; the terminal is now twice its former map height:

- the terminal is 8x8 blocks (x=31..38, y=5..12), up from 8x4;
  the door and its warp stay at (35,12), with the door pixels centred there;
- the forest north of the airport is cut back to its top row, and the
  forest east of it to its last two columns (x=46..47);
- the runway (x=42..45, y=3..12) runs north with its centre line on the left
  edge of column 44 (src/airport_flyover.c flies along it);
- a taxiway one block wide (x=41) runs along the runway's west side from the
  north apron (x=31..41, y=1..2) down to the gate apron beside the terminal
  (x=39..41, y=10..12), with yellow lines to the parking stands;
- the lawn north of the terminal is the fenced viewing spot (x=30..39,
  y=4, continuing down x=39 to y=8). From its east end (x=39) the camera shows the whole runway and
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
TERMINAL_BASE = [
    [808, 809, 809, 810, 811, 861, 812, 813],
    [814, 815, 815, 816, 817, 860, 818, 819],
    [820, 821, 821, 822, 823, 859, 824, 825],
    [826, 827, 828, 829, 830, 831, 831, 832],
]
# Four glazed facade bands add actual building height below the normal roof.
# All window/beam/side-wall tiles are reused from the terminal's existing art.
WALL_LEFT, WALL_RIGHT = 857, 858
TERMINAL = TERMINAL_BASE[:3] + [
    [WALL_LEFT, 831, 831, 831, 831, 831, 831, WALL_RIGHT]
] * 4 + TERMINAL_BASE[3:]
TERMINAL_X, TERMINAL_Y = 31, 5
DOOR_X, DOOR_Y = 35, 12

X0, X1, Y0, Y1 = 30, 47, 0, 13     # the rectangle this tool owns
RUNWAY_X, RUNWAY_Y0, RUNWAY_Y1 = 42, 3, 12
ATTRS = FR + '/data/tilesets/secondary/vermilion_city/metatile_attributes.bin'
MB_WARP_DOOR = 0x69


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
    # One row at the north leaves space for the taller terminal and its walkway.
    for x in range(X0, X1 + 1):
        g[(x, 0)] = tree(x, 0)
        g[(x, 1)] = tree(x, 1, bottom=True) if x >= 46 else (GRASS[0], 1, 0)
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

    # The two remote stands move north with the reduced apron (y=1..2).
    for x in range(31, 42):
        for y in range(1, 3):
            left, right, top, bottom = x == 31, x == 41, y == 1, y == 2
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
    for y in range(3, 10):
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
    for y in range(4, 14):
        g[(30, y)] = GRASS
    for x in range(31, 39):
        g[(x, 13)] = GRASS

    # A continuous public walkway runs around the north of the taller roof
    # and down its east side to the existing (39,7..8) viewing position.
    for x in range(30, 40):
        g[(x, 3)] = fence(SIGN_POST if x == 33 else FENCE_H)
        g[(x, 4)] = GRASS
    g[(40, 3)] = fence(FENCE_TOP)
    for y in range(4, 9):
        g[(40, y)] = fence(FENCE_V, 3)
    for y in range(5, 9):
        g[(39, y)] = GRASS
    g[(40, 9)] = fence(FENCE_END, 3)
    g[(39, 9)] = fence(FENCE_H, 3)
    # the airside's south fence, meeting the fence that runs on down to y=15
    for x in range(39, 46):
        g[(x, 13)] = fence(FENCE_V if x == 41 else FENCE_H, 3)
    return g


def align_terminal_tiles():
    """Reuse source tile references; no PNG or palette pixels are changed."""
    path = FR + '/data/tilesets/secondary/vermilion_city/metatiles.bin'
    mt = bytearray(open(path, 'rb').read())
    at = bytearray(open(ATTRS, 'rb').read())
    source = {809: [639, 639, 639, 639, 45249, 45249, 45265, 45265], 810: [639, 639, 639, 639, 45250, 45251, 45265, 45266], 811: [639, 639, 639, 639, 46275, 46274, 46290, 46289], 812: [639, 639, 639, 639, 46273, 46273, 46289, 46289], 815: [639, 639, 639, 639, 45265, 45265, 45265, 45265], 816: [639, 45266, 639, 45266, 45265, 45266, 45265, 45299], 817: [46290, 639, 46290, 639, 46290, 46289, 46323, 46289], 818: [639, 639, 639, 639, 46289, 46289, 46289, 46289], 821: [639, 639, 639, 639, 12529, 12529, 12545, 12545], 822: [12530, 12530, 12545, 12546, 12561, 12547, 12579, 12563], 823: [13554, 13554, 12545, 12545, 13571, 13585, 13587, 13603], 824: [639, 639, 639, 639, 13553, 13553, 13570, 13570], 829: [639, 12580, 639, 12581, 12562, 0, 12578, 0], 830: [13604, 639, 13605, 639, 0, 12562, 0, 12578]}
    def put(block, entries, behavior=0):
        index = block - 640
        if len(mt) < (index + 1) * 16:
            mt.extend(bytes((index + 1) * 16 - len(mt)))
            at.extend(bytes((index + 1) * 4 - len(at)))
        mt[index * 16:(index + 1) * 16] = struct.pack('<8H', *entries)
        at[index * 4:(index + 1) * 4] = struct.pack('<I', behavior)
    # Each half of the old door was in a different map cell, straddling x=35.
    # The single live warp's centre is 8px to the right; put the whole door in it.
    put(829, [639] * 4 + [source[829][4], source[829][4], source[829][6], source[829][6]])
    put(830, [source[829][1], source[830][0], source[829][3], source[830][2]] + [0] * 4, MB_WARP_DOOR)
    # Move the sign and its roof seam together. Right-hand parts need private
    # metatiles because the original right-hand window/roof blocks are reused.
    for plain, left_id, centre_id, right_id, output in (
            (809, 810, 811, 812, 861),
            (815, 816, 817, 818, 860),
            (821, 822, 823, 824, 859)):
        shifted = {left_id: [], centre_id: [], output: []}
        for layer in (0, 1):
            off = layer * 4
            left, centre, right = [source[i][off:off + 4] for i in (left_id, centre_id, right_id)]
            shifted[left_id] += [source[plain][off + 1], left[0], source[plain][off + 3], left[2]]
            shifted[centre_id] += [left[1], centre[0], left[3], centre[2]]
            shifted[output] += [centre[1], right[1], centre[3], right[3]]
        for block, entries in shifted.items():
            put(block, entries)
        put(right_id, source[right_id])
    # Straight shaded side strips reuse existing roof-side tiles in the wall
    # palette; glass panes and horizontal sills come from the original facade.
    put(WALL_LEFT, [639] * 4 + [0x30e0, 0x3512, 0x30e0, 0x3122])
    put(WALL_RIGHT, [639] * 4 + [0x3512, 0x34e0, 0x3122, 0x34e0])
    open(path, 'wb').write(mt)
    open(ATTRS, 'wb').write(at)


def main():
    align_terminal_tiles()
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
    # The terminal's blocks came from the MART, whose sign behavior made the wall
    # print the mart's line, so they are cleared. The two blocks the entrance sits
    # on keep MB_WARP_DOOR, or the door stops being a door.
    door = {TERMINAL[DOOR_Y - TERMINAL_Y][DOOR_X - TERMINAL_X]}
    for block in {b for row in TERMINAL for b in row}:
        attrs[(block - 640) * 4] = MB_WARP_DOOR if block in door else 0
    open(ATTRS, 'wb').write(attrs)
    print(f'{LAYOUT}: terminal 8x8 at x={TERMINAL_X}..{TERMINAL_X + 7}, runway x={RUNWAY_X}..'
          f'{RUNWAY_X + 3} y={RUNWAY_Y0}..{RUNWAY_Y1}, airside x=31..45 y=1..12')


if __name__ == '__main__':
    main()
