#!/usr/bin/env python3
"""Draw the airport runway tiles into the Vermilion City secondary tileset.

Adds the asphalt, the runway markings and the grass edges as new 8x8 tiles at
the end of data/tilesets/secondary/vermilion_city/tiles.png, fills the unused
secondary palette 7 with the asphalt colours, and appends the metatiles that
the city layout uses for the runway, the taxiway and the apron.

Run it again after changing the art: it always rewrites the same tiles,
palette and metatiles, so the tileset stays the same size.
"""
import os, struct
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TS = FR + '/data/tilesets/secondary/vermilion_city'
FIRST_TILE = 144          # tiles 0..143 are the city's own art
PAL = 7                   # the one secondary palette slot the city leaves unused
FIRST_METATILE = 193      # metatiles 0..192 are the city's own
SECONDARY_TILE_BASE = 640 # a secondary tile id as the metatiles see it

# Palette 7. Greys follow FR/LG's road shading (123,123,131 is the game's own
# mid grey), the white and yellow are the paint.
COLOURS = [
    (  0,   0,   0),  # 0 transparent (top layer) / unused
    ( 74,  74,  82),  # 1 seam
    ( 98,  98, 106),  # 2 asphalt dark
    (123, 123, 131),  # 3 asphalt mid
    (148, 148, 156),  # 4 asphalt light
    (172, 172, 180),  # 5 asphalt highlight
    (238, 238, 238),  # 6 paint white
    (197, 197, 205),  # 7 paint shadow
    (246, 213,  74),  # 8 paint yellow
    (197, 164,  41),  # 9 paint yellow shadow
    ( 57,  57,  66),  # 10 edge against the grass
    (  0,   0,   0),  # 11..15 spare
    (  0,   0,   0),
    (  0,   0,   0),
    (  0,   0,   0),
    (  0,   0,   0),
]
LEGEND = {'.': 0, 'd': 1, 'a': 2, 'b': 3, 'c': 4, 'h': 5,
          'w': 6, 'v': 7, 'y': 8, 'z': 9, 'k': 10}

TILES = {}
TILES['ASPH1'] = [
    'bbabbbbc',
    'bbbbcbbb',
    'abbbbbba',
    'bbbcbbbb',
    'bbbbbbab',
    'cbbabbbb',
    'bbbbbbbc',
    'babbbbbb',
]
TILES['ASPH2'] = [
    'bbbbabbb',
    'cbbbbbab',
    'bbabbcbb',
    'bbbbbbbb',
    'abbbcbbb',
    'bbbbbbba',
    'bcbabbbb',
    'bbbbbbcb',
]
# grass on the left, asphalt from the third column on (x flipped for the right)
TILES['EDGE_V'] = [
    '..kbbbba',
    '.kabbbbb',
    '..kbbbcb',
    '.kbbbabb',
    '..kbbbbb',
    '.kabbcbb',
    '..kbbbbb',
    '.kbbbbbc',
]
# grass on top, asphalt from the third row down (y flipped for the bottom)
TILES['EDGE_H'] = [
    '........',
    '.k.kk.k.',
    'kkkkkkkk',
    'bbabbbbc',
    'bbbbcbbb',
    'abbbbbba',
    'bbbcbbbb',
    'bbbbbbab',
]
TILES['CORNER'] = [
    '........',
    '....k.k.',
    '..kkkkkk',
    '.kbbbbbc',
    '..kbbcbb',
    '.kbabbbb',
    '..kbbbbb',
    '.kbbbcbb',
]
# white runway side stripe, two pixels in from the shoulder
TILES['STRIPE_V'] = [
    'bwwbbbbc',
    'bwwbbcbb',
    'awwbbbbb',
    'bwwbbbab',
    'bwwbcbbb',
    'cwwbbbbb',
    'bwwabbbc',
    'bwwbbbbb',
]
# centre line: the paint sits on the tile's left edge, i.e. the middle of the runway
TILES['DASH'] = [
    'wwbbbabb',
    'wwbbbbbc',
    'wwabbbbb',
    'wwbbcbbb',
    'wwbbbbba',
    'wwbcbbbb',
    'wwbbbbbb',
    'wwbbabcb',
]
# threshold bars: one white bar every eight pixels across the runway
TILES['THRESH'] = [
    'bwwwbbba',
    'bwwwbbbb',
    'awwwbcbb',
    'bwwwbbbb',
    'bwwwabbb',
    'cwwwbbbb',
    'bwwwbbbc',
    'bwwwbbbb',
]
# taxiway guide line
TILES['TAXI'] = [
    'bbbyybbc',
    'bbbyybbb',
    'abbyybba',
    'bbbyycbb',
    'bbbyybbb',
    'cbbyybbb',
    'bbbyybbc',
    'babyybbb',
]
TILES['NUM_0'] = [
    'bbbbbbbb',
    'bbwwwwbb',
    'bbwbbwbb',
    'bbwbbwbb',
    'bbwbbwbb',
    'bbwbbwbb',
    'bbwwwwbb',
    'bbbbbbbb',
]
TILES['NUM_1'] = [
    'bbbbbbbb',
    'bbbbwbbb',
    'bbbwwbbb',
    'bbbbwbbb',
    'bbbbwbbb',
    'bbbbwbbb',
    'bbwwwwbb',
    'bbbbbbbb',
]
ORDER = ['ASPH1', 'ASPH2', 'EDGE_V', 'EDGE_H', 'CORNER', 'STRIPE_V', 'DASH',
         'THRESH', 'TAXI', 'NUM_0', 'NUM_1']
IDX = {name: FIRST_TILE + i for i, name in enumerate(ORDER)}

XFLIP, YFLIP = 1 << 10, 1 << 11


def tile(name, xflip=False, yflip=False, pal=PAL):
    """A metatile entry for one of the new tiles."""
    v = SECONDARY_TILE_BASE + IDX[name] | (pal << 12)
    if xflip:
        v |= XFLIP
    if yflip:
        v |= YFLIP
    return v


# The grass the city is drawn on (primary metatile 1), used as the bottom layer
# of every tile where the asphalt meets the grass.
GRASS = [0x026E, 0x026F, 0x024C, 0x024D]
EMPTY = [0, 0, 0, 0]
NORMAL, COVERED = 0 << 29, 1 << 29

A1, A2 = 'ASPH1', 'ASPH2'


def paved(*tiles):
    """A solid asphalt metatile: it needs no grass underneath."""
    return list(tiles), EMPTY, NORMAL


def edged(*tiles):
    """Asphalt over grass, on the middle layer so sprites stay on top."""
    return GRASS, list(tiles), COVERED


METATILES = [
    # name                bottom / top layers
    ('ASPHALT',   paved(tile(A1), tile(A2), tile(A2), tile(A1))),
    ('DASH',      paved(tile('DASH'), tile(A2), tile('DASH'), tile(A1))),
    ('STRIPE_L',  paved(tile(A1), tile('STRIPE_V'), tile(A2), tile('STRIPE_V'))),
    ('STRIPE_R',  paved(tile('STRIPE_V', xflip=True), tile(A1),
                        tile('STRIPE_V', xflip=True), tile(A2))),
    ('THRESHOLD', paved(tile('THRESH'), tile('THRESH'), tile('THRESH'), tile('THRESH'))),
    ('TAXI',      paved(tile('TAXI'), tile(A2), tile('TAXI'), tile(A1))),
    ('NUM_0',     paved(tile(A1), tile(A2), tile('NUM_0'), tile(A1))),
    ('NUM_1',     paved(tile(A1), tile(A2), tile('NUM_1'), tile(A1))),
    ('EDGE_L',    edged(tile('EDGE_V'), tile('STRIPE_V'), tile('EDGE_V'), tile('STRIPE_V'))),
    ('EDGE_R',    edged(tile('STRIPE_V', xflip=True), tile('EDGE_V', xflip=True),
                        tile('STRIPE_V', xflip=True), tile('EDGE_V', xflip=True))),
    ('EDGE_T',    edged(tile('EDGE_H'), tile('EDGE_H'), tile(A1), tile(A2))),
    ('EDGE_B',    edged(tile(A1), tile(A2), tile('EDGE_H', yflip=True), tile('EDGE_H', yflip=True))),
    ('CORNER_TL', edged(tile('CORNER'), tile('EDGE_H'), tile('EDGE_V'), tile(A1))),
    ('CORNER_TR', edged(tile('EDGE_H'), tile('CORNER', xflip=True),
                        tile(A1), tile('EDGE_V', xflip=True))),
    ('CORNER_BL', edged(tile('EDGE_V'), tile(A1),
                        tile('CORNER', yflip=True), tile('EDGE_H', yflip=True))),
    ('CORNER_BR', edged(tile(A1), tile('EDGE_V', xflip=True),
                        tile('EDGE_H', yflip=True), tile('CORNER', xflip=True, yflip=True))),
    # the apron keeps the grass edge but not the runway's side stripe
    ('EDGE_LP',   edged(tile('EDGE_V'), tile(A2), tile('EDGE_V'), tile(A1))),
    ('EDGE_RP',   edged(tile(A2), tile('EDGE_V', xflip=True),
                        tile(A1), tile('EDGE_V', xflip=True))),
]


def write_tiles():
    im = Image.open(TS + '/tiles.png')
    w, h = im.size
    per_row = w // 8
    need = FIRST_TILE + len(ORDER)
    rows = (need + per_row - 1) // per_row
    if rows * 8 > h:
        grown = Image.new('P', (w, rows * 8), 0)
        grown.putpalette(im.getpalette())
        grown.paste(im, (0, 0))
        im = grown
    for name in ORDER:
        idx = IDX[name]
        r, c = divmod(idx, per_row)
        for y, line in enumerate(TILES[name]):
            for x, ch in enumerate(line):
                im.putpixel((c * 8 + x, r * 8 + y), LEGEND[ch])
    im.save(TS + '/tiles.png')
    return im.size, need


def write_palette():
    out = ['JASC-PAL', '0100', '16']
    out += ['%d %d %d' % c for c in COLOURS]
    # .pal files are checked in with CRLF endings (see .gitattributes)
    open(f'{TS}/palettes/{PAL:02d}.pal', 'w', newline='\r\n').write('\n'.join(out) + '\n')


def write_metatiles():
    mt = bytearray(open(TS + '/metatiles.bin', 'rb').read())
    at = bytearray(open(TS + '/metatile_attributes.bin', 'rb').read())
    del mt[FIRST_METATILE * 16:]
    del at[FIRST_METATILE * 4:]
    ids = {}
    for i, (name, (bottom, top, layer)) in enumerate(METATILES):
        ids[name] = FIRST_METATILE + i
        mt += struct.pack('<8H', *bottom, *top)
        at += struct.pack('<I', layer)          # behaviour 0, terrain 0
    open(TS + '/metatiles.bin', 'wb').write(mt)
    open(TS + '/metatile_attributes.bin', 'wb').write(at)
    return ids


def main():
    write_palette()
    size, tiles = write_tiles()
    ids = write_metatiles()
    print(f'tiles.png {size[0]}x{size[1]} ({tiles} tiles, {len(ORDER)} new)')
    print(f'palette {PAL} rewritten, metatiles {FIRST_METATILE}..{FIRST_METATILE + len(METATILES) - 1}')
    for name, i in ids.items():
        print(f'  {name:9s} metatile {i:3d}  block {SECONDARY_TILE_BASE + i}')


if __name__ == '__main__':
    main()
