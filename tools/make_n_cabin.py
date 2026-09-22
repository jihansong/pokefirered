#!/usr/bin/env python3
"""N's cabin on SIX ISLAND's WATER PATH (Thunder Yellow v0.6.0): copies the
exterior of the WATER PATH's second house (blocks x=10..14, y=16..19) into the
empty south-east nook (x=16..20, y=20..23), with its door at (17,23).
Safe to run more than once."""
import os, struct
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BIN = R + '/data/layouts/SixIsland_WaterPath/map.bin'
W = 24
b = bytearray(open(BIN, 'rb').read())
get = lambda x, y: struct.unpack_from('<H', b, (y * W + x) * 2)[0]
block = [[get(x, y) for x in range(10, 15)] for y in range(16, 20)]
for j in range(4):
    for i in range(5):
        struct.pack_into('<H', b, ((20 + j) * W + 16 + i) * 2, block[j][i])
open(BIN, 'wb').write(b)
print('ok')
