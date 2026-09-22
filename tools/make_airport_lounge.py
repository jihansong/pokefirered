#!/usr/bin/env python3
"""Build the window lounge of the Vermilion airport terminal (MAP_KANTO_AIRPORT).

The terminal gets eight more columns on its east side: a lounge whose north
wall is one big window onto the apron and the runway. The view reuses the
runway tiles of the city (tools/make_runway_tiles.py) under a glass tinted
copy of their palette, with the window frame on the top layer so it is drawn
over the airliner that parks at the gate behind the glass.

The terminal's own tileset, pokeemerald's Battle Frontier set, is full (509 of
512 metatiles) and is rewritten whenever the Hoenn import runs, so the lounge
lives in a tileset of its own, gTileset_KantoAirport: a copy of that set plus
the lounge tiles, written into metatile slots the terminal does not use.

Running it again rebuilds the same files.
"""
import json, os, re, shutil, struct, sys
from PIL import Image

FR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.dont_write_bytecode = True  # keep tools/ free of __pycache__
sys.path.insert(0, FR + '/tools')
import make_runway_tiles as runway  # noqa: E402

SRC = FR + '/data/tilesets/secondary/em_battle_frontier'
DST = FR + '/data/tilesets/secondary/kanto_airport'
LAYOUT = 'LAYOUT_KANTO_AIRPORT'
TILESET = 'gTileset_KantoAirport'

PRIMARY_TILES = 512        # Emerald tilesets keep Emerald's split
PRIMARY_METATILES = 512
FIRST_TILE = 320           # the Battle Frontier set has 320 tiles
FIRST_METATILE = 440       # slots 440..508 are not used by the terminal
VIEW_PAL, FRAME_PAL = 12, 6  # the two secondary palettes the set leaves unused

OLD_WIDTH, LOUNGE_X, LOUNGE_W = 25, 25, 8
WINDOW_ROWS = 4            # rows 0..3 are glass

# Battle Frontier blocks the lounge floor reuses
FLOOR, PLANT_TOP, PLANT_BOTTOM = 512, 607, 615


def view_colours():
    """The runway palette seen through the glass: blended towards a pale sky blue."""
    glass = (189, 222, 255)
    out = [runway.COLOURS[0]]
    for r, g, b in runway.COLOURS[1:]:
        out.append(tuple(round(c * 0.75 + t * 0.25) for c, t in zip((r, g, b), glass)))
    return out


FRAME_COLOURS = [
    (0, 0, 0),         # 0 transparent
    (65, 74, 98),      # 1 frame shadow
    (115, 123, 148),   # 2 frame
    (172, 180, 205),   # 3 frame light
    (238, 246, 255),   # 4 frame highlight
    (213, 238, 255),   # 5 glass reflection
    (90, 98, 123),     # 6 sill shadow
    (148, 156, 180),   # 7 sill
] + [(0, 0, 0)] * 8

FRAME_LEGEND = {'.': 0, 'k': 1, 'g': 2, 'l': 3, 'w': 4, 'r': 5, 's': 6, 'S': 7}
FRAME_TILES = {
    'RAIL': [
        'kkkkkkkk',
        'wlwlwlwl',
        'gggggggg',
        'kkkkkkkk',
        '........',
        '........',
        '........',
        '........',
    ],
    'POST': [
        'klgk....',
        'klgk....',
        'kwgk....',
        'klgk....',
        'klgk....',
        'kwgk....',
        'klgk....',
        'klgk....',
    ],
    'RAIL_POST': [
        'kkkkkkkk',
        'wlwlwlwl',
        'gggggggg',
        'klgkkkkk',
        'klgk....',
        'kwgk....',
        'klgk....',
        'klgk....',
    ],
    'SILL': [
        '........',
        '........',
        '........',
        '........',
        'kkkkkkkk',
        'wSwSwSwS',
        'SSSSSSSS',
        'ssssssss',
    ],
    'SILL_POST': [
        'klgk....',
        'klgk....',
        'kwgk....',
        'klgk....',
        'kkkkkkkk',
        'wSwSwSwS',
        'SSSSSSSS',
        'ssssssss',
    ],
    'STREAK': [
        '.....r..',
        '....r..r',
        '...r..r.',
        '..r..r..',
        '.r..r...',
        'r..r....',
        '..r.....',
        '.r......',
    ],
}
FRAME_ORDER = ['RAIL', 'POST', 'RAIL_POST', 'SILL', 'SILL_POST', 'STREAK']

# The view, one runway metatile name per block: the apron with the gate's lead
# in line on the left, the runway on the right.
VIEW = [
    ['ASPHALT', 'ASPHALT', 'TAXI', 'ASPHALT', 'STRIPE_L', 'ASPHALT', 'DASH',    'STRIPE_R'],
    ['ASPHALT', 'ASPHALT', 'TAXI', 'ASPHALT', 'STRIPE_L', 'ASPHALT', 'ASPHALT', 'STRIPE_R'],
    ['ASPHALT', 'ASPHALT', 'TAXI', 'ASPHALT', 'STRIPE_L', 'ASPHALT', 'DASH',    'STRIPE_R'],
    ['ASPHALT', 'ASPHALT', 'TAXI', 'ASPHALT', 'STRIPE_L', 'ASPHALT', 'ASPHALT', 'STRIPE_R'],
]
# posts on the lounge's two ends and between the apron and the runway panes
POST_COLUMNS = {0, 8, 16}          # in 8x8 tile columns of the lounge (0..16)
STREAKS = {(3, 1), (4, 2), (11, 1), (12, 2), (5, 5), (13, 5)}  # (tile x, tile y)

XFLIP, YFLIP = 1 << 10, 1 << 11


def tile_index(i):
    return PRIMARY_TILES + i


def copy_base():
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(DST + '/palettes')
    for f in ('tiles.png', 'metatiles.bin', 'metatile_attributes.bin'):
        shutil.copy(f'{SRC}/{f}', f'{DST}/{f}')
    for i in range(16):
        shutil.copy(f'{SRC}/palettes/{i:02d}.pal', f'{DST}/palettes/{i:02d}.pal')


def write_pal(slot, colours):
    lines = ['JASC-PAL', '0100', '16'] + ['%d %d %d' % c for c in colours]
    open(f'{DST}/palettes/{slot:02d}.pal', 'w', newline='\r\n').write('\n'.join(lines) + '\n')


def add_tiles():
    """Append the runway tiles (the city's own pixels) and the frame tiles."""
    im = Image.open(DST + '/tiles.png')
    city = Image.open(runway.TS + '/tiles.png')
    w, h = im.size
    per_row = w // 8
    names = [('runway', n) for n in runway.ORDER] + [('frame', n) for n in FRAME_ORDER]
    need = FIRST_TILE + len(names)
    rows = (need + per_row - 1) // per_row
    if rows * 8 > h:
        grown = Image.new('P', (w, rows * 8), 0)
        grown.putpalette(im.getpalette())
        grown.paste(im, (0, 0))
        im = grown
    index = {}
    cpr = city.size[0] // 8
    for i, (kind, name) in enumerate(names):
        idx = FIRST_TILE + i
        index[(kind, name)] = idx
        r, c = divmod(idx, per_row)
        if kind == 'runway':
            sr, sc = divmod(runway.IDX[name], cpr)
            im.paste(city.crop((sc * 8, sr * 8, sc * 8 + 8, sr * 8 + 8)), (c * 8, r * 8))
        else:
            for y, line in enumerate(FRAME_TILES[name]):
                for x, ch in enumerate(line):
                    im.putpixel((c * 8 + x, r * 8 + y), FRAME_LEGEND[ch])
    im.save(DST + '/tiles.png')
    return index


def view_tile_grid(index):
    """8x8 tile entries for the glass view, from the runway metatile definitions."""
    defs = {name: bottom for name, (bottom, _, _) in runway.METATILES}
    first_city_tile = runway.SECONDARY_TILE_BASE + runway.FIRST_TILE
    grid = [[0] * (LOUNGE_W * 2) for _ in range(WINDOW_ROWS * 2)]
    for by, row in enumerate(VIEW):
        for bx, name in enumerate(row):
            for k, entry in enumerate(defs[name]):
                city_idx = (entry & 0x3FF) - first_city_tile
                tname = runway.ORDER[city_idx]
                v = tile_index(index[('runway', tname)]) | (entry & (XFLIP | YFLIP)) | (VIEW_PAL << 12)
                grid[by * 2 + k // 2][bx * 2 + k % 2] = v
    return grid


def frame_tile_grid(index):
    """8x8 top layer entries: rail on top, sill at the bottom, posts, reflections."""
    tw, th = LOUNGE_W * 2, WINDOW_ROWS * 2
    grid = [[0] * tw for _ in range(th)]

    def t(name, flip=0):
        return tile_index(index[('frame', name)]) | flip | (FRAME_PAL << 12)

    for ty in range(th):
        for tx in range(tw):
            top, bottom = ty == 0, ty == th - 1
            # a post sits on the left edge of its tile; the one closing the
            # lounge on the right is the last tile column, flipped
            post_l = tx in POST_COLUMNS
            post_r = tx == tw - 1
            flip = XFLIP if post_r and not post_l else 0
            post = post_l or post_r
            if top:
                grid[ty][tx] = t('RAIL_POST', flip) if post else t('RAIL')
            elif bottom:
                grid[ty][tx] = t('SILL_POST', flip) if post else t('SILL')
            elif post:
                grid[ty][tx] = t('POST', flip)
            elif (tx, ty) in STREAKS:
                grid[ty][tx] = t('STREAK')
    return grid


def add_metatiles(view, frame):
    mt = bytearray(open(DST + '/metatiles.bin', 'rb').read())
    at = bytearray(open(DST + '/metatile_attributes.bin', 'rb').read())
    blocks, slot, seen = {}, FIRST_METATILE, {}
    for by in range(WINDOW_ROWS):
        for bx in range(LOUNGE_W):
            bottom = [view[by * 2 + dy][bx * 2 + dx] for dy in (0, 1) for dx in (0, 1)]
            top = [frame[by * 2 + dy][bx * 2 + dx] for dy in (0, 1) for dx in (0, 1)]
            key = tuple(bottom + top)
            if key not in seen:
                if slot * 16 + 16 > len(mt):
                    raise SystemExit('out of metatile slots')
                mt[slot * 16:slot * 16 + 16] = struct.pack('<8H', *key)
                # normal layer type: the frame on the top layer covers sprites
                at[slot * 4:slot * 4 + 4] = struct.pack('<I', 0)
                seen[key] = slot
                slot += 1
            blocks[(bx, by)] = PRIMARY_METATILES + seen[key]
    open(DST + '/metatiles.bin', 'wb').write(mt)
    open(DST + '/metatile_attributes.bin', 'wb').write(at)
    return blocks, slot - FIRST_METATILE


def check_free_slots():
    """Make sure the terminal does not use the metatile slots we write into."""
    lay = layout_entry()
    w, h = lay['width'], lay['height']
    blocks = struct.unpack('<%dH' % (w * h), open(FR + '/' + lay['blockdata_filepath'], 'rb').read())
    used = {(v & 0x3FF) - PRIMARY_METATILES for y in range(h) for x in range(min(w, OLD_WIDTH))
            for v in [blocks[y * w + x]] if (v & 0x3FF) >= PRIMARY_METATILES}
    clash = sorted(u for u in used if u >= FIRST_METATILE)
    if clash:
        raise SystemExit(f'terminal uses metatiles {clash}')


def layout_entry():
    return next(l for l in json.load(open(FR + '/data/layouts/layouts.json'))['layouts']
                if l and l.get('id') == LAYOUT)


def write_layout(window):
    path = FR + '/data/layouts/layouts.json'
    data = json.load(open(path))
    lay = next(l for l in data['layouts'] if l and l.get('id') == LAYOUT)
    w, h = lay['width'], lay['height']
    bin_path = FR + '/' + lay['blockdata_filepath']
    old = struct.unpack('<%dH' % (w * h), open(bin_path, 'rb').read())
    nw = OLD_WIDTH + LOUNGE_W
    new = [0] * (nw * h)
    for y in range(h):
        for x in range(OLD_WIDTH):
            new[y * nw + x] = old[y * w + x]

    def put(x, y, block, collision):
        new[y * nw + x] = (block & 0x3FF) | (collision << 10) | (0 << 12)

    for y in range(h):
        for dx in range(LOUNGE_W):
            x = LOUNGE_X + dx
            if y < WINDOW_ROWS:
                put(x, y, window[(dx, y)], 1)
            else:
                put(x, y, FLOOR, 0)
    # a potted plant in the far corner, like the ones by the entrance
    put(nw - 1, h - 2, PLANT_TOP, 0)
    put(nw - 1, h - 1, PLANT_BOTTOM, 1)
    # elevation 3 like the rest of the floor
    for i, v in enumerate(new):
        if (i % nw) >= OLD_WIDTH:
            new[i] = (v & 0xFFF) | (3 << 12)
    open(bin_path, 'wb').write(struct.pack('<%dH' % (nw * h), *new))
    # patch only this layout's entry, so the rest of the file keeps its formatting
    text = open(path).read()
    start = text.index('"id": "%s"' % LAYOUT)
    end = text.index('}', start)
    entry = re.sub(r'"width": \d+', '"width": %d' % nw, text[start:end])
    entry = re.sub(r'"secondary_tileset": "\w+"', '"secondary_tileset": "%s"' % TILESET, entry)
    open(path, 'w').write(text[:start] + entry + text[end:])


def main():
    check_free_slots()
    copy_base()
    write_pal(VIEW_PAL, view_colours())
    write_pal(FRAME_PAL, FRAME_COLOURS)
    index = add_tiles()
    window, count = add_metatiles(view_tile_grid(index), frame_tile_grid(index))
    write_layout(window)
    print(f'{TILESET}: +{len(runway.ORDER) + len(FRAME_ORDER)} tiles, +{count} metatiles '
          f'(slots {FIRST_METATILE}..{FIRST_METATILE + count - 1}), palettes {FRAME_PAL} and {VIEW_PAL}')
    print(f'{LAYOUT}: {OLD_WIDTH} -> {OLD_WIDTH + LOUNGE_W} blocks wide')


if __name__ == '__main__':
    main()
