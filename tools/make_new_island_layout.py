#!/usr/bin/env python3
"""Builds data/layouts/NewIsland/map.bin: the old cloning lab on NEW ISLAND
(Thunder Yellow v0.5.0, TEAM ROCKET event 11).

The lab is the north-west corner of POKeMON MANSION B1F (two lab rooms), closed
off with the mansion's own outer-wall metatiles, and with the switch gate
between the rooms replaced by floor so the rooms connect."""
import os, struct
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = R + '/data/layouts/PokemonMansion_B1F/map.bin'
SW = 38
W, H = 26, 17
src = open(SRC, 'rb').read()
g = lambda x, y: struct.unpack_from('<H', src, (y * SW + x) * 2)[0]
out = [[0] * W for _ in range(H)]
for y in range(14):
    for x in range(W):
        out[y][x] = g(x, y)
# right outer wall (from the mansion's east wall, column 37)
out[0][25] = g(37, 0)
for y in range(1, 13):
    out[y][25] = g(37, 1)
# bottom outer wall (from the mansion's south wall, rows 31-34)
for x in range(1, 25):
    out[13][x] = g(2, 31) if out[13][x] == g(6, 13) else out[13][x]
    out[14][x] = g(2, 32)
    out[15][x] = g(2, 33)
    out[16][x] = g(2, 34)
out[13][0], out[14][0], out[15][0], out[16][0] = g(0, 31), g(0, 32), g(0, 33), g(0, 34)
out[13][25], out[14][25], out[15][25], out[16][25] = g(37, 31), g(37, 32), g(37, 33), g(37, 34)
for x in list(range(2, 12)) + [12]:
    out[13][x] = g(2, 31)
# open the gate between the two rooms: the dividing wall now ends above it
out[8][12] = g(12, 13)
for y in range(9, 13):
    out[y][12] = g(10, 11)
with open(R + '/data/layouts/NewIsland/map.bin', 'wb') as f:
    for row in out:
        f.write(b''.join(struct.pack('<H', v) for v in row))
