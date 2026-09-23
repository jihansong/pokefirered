#!/usr/bin/env python3
"""The snowbound mountain past SEVAULT CANYON (Thunder Yellow v0.6.0).

The mountain reuses MT. EMBER's summit path and summit, recolored as ice and
snow (the summit uses FR/LG's fog weather; WEATHER_SNOW draws nothing here): two new secondary tilesets share MT. EMBER's tiles and metatiles and only
get new palettes (every color mapped by brightness onto an icy ramp, the way the
FR/LG Icefall Cave is colored). Writes
  data/tilesets/secondary/silver_cave/palettes/*.pal  (from mt_ember)
  data/tilesets/secondary/silver_peak/palettes/*.pal  (from sevii_islands_123)
  data/layouts/SilverMountain_{1F,2F,3F,Summit}/     (copies of MT. EMBER's)
and appends the four layouts to layouts.json once. Also cuts the cave door
into SEVAULT CANYON (see below)."""
import json, os, shutil
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DARK, LIGHT = (33, 49, 90), (222, 234, 255)


def ice(c):
    r, g, b = c
    y = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    y = min(1.0, y * 1.1)  # lift mid tones towards snow
    c = [DARK[i] + (LIGHT[i] - DARK[i]) * y for i in range(3)]
    c[2] = min(255, c[2] + 16 * (1 - y))  # a little more blue in the shadows
    return tuple(int(round(v)) for v in c)


def read_pal(p):
    l = open(p).read().split('\n')
    return [tuple(int(v) for v in x.split()) for x in l[3:3 + int(l[2])]]


def write_pal(p, cols):
    with open(p, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n%d\n' % len(cols) + ''.join('%d %d %d\n' % c for c in cols))


def recolor_tileset(src, dst, primary=False):
    kind = 'primary' if primary else 'secondary'
    sd, dd = f'{R}/data/tilesets/{kind}/{src}/palettes', f'{R}/data/tilesets/{kind}/{dst}/palettes'
    os.makedirs(dd, exist_ok=True)
    # a primary tileset owns palettes 0..6, a secondary one 7..12; the rest stay as they are
    own = range(0, 7) if primary else range(7, 13)
    for i in range(16):
        cols = read_pal(f'{sd}/{i:02d}.pal')
        write_pal(f'{dd}/{i:02d}.pal', [cols[0]] + [ice(c) for c in cols[1:]] if i in own else cols)


recolor_tileset('mt_ember', 'silver_cave')
recolor_tileset('sevii_islands_123', 'silver_peak')
# The summit's ground and stairs come from the primary tileset, so the peak needs
# an icy copy of that too (same tiles and metatiles, palettes 0..6 recolored).
recolor_tileset('general', 'silver_general', primary=True)

lays = json.load(open(R + '/data/layouts/layouts.json'))
by_id = {l['id']: l for l in lays['layouts'] if l}
added = False
for name, src, ts in [('1F', 'LAYOUT_MT_EMBER_SUMMIT_PATH_1F', 'gTileset_SilverCave'),
                      ('2F', 'LAYOUT_MT_EMBER_SUMMIT_PATH_2F', 'gTileset_SilverCave'),
                      ('3F', 'LAYOUT_MT_EMBER_SUMMIT_PATH_3F', 'gTileset_SilverCave'),
                      ('Summit', 'LAYOUT_MT_EMBER_SUMMIT', 'gTileset_SilverPeak')]:
    s = by_id[src]
    d = f'data/layouts/SilverMountain_{name}'
    os.makedirs(f'{R}/{d}', exist_ok=True)
    shutil.copy(f'{R}/{s["blockdata_filepath"]}', f'{R}/{d}/map.bin')
    shutil.copy(f'{R}/{s["border_filepath"]}', f'{R}/{d}/border.bin')
    lid = f'LAYOUT_SILVER_MOUNTAIN_{name.upper()}'
    if lid not in by_id:
        lays['layouts'].append({'id': lid, 'name': f'SilverMountain_{name}_Layout', 'width': s['width'], 'height': s['height'],
                                'border_width': s['border_width'], 'border_height': s['border_height'],
                                'primary_tileset': 'gTileset_SilverGeneral' if ts == 'gTileset_SilverPeak' else s['primary_tileset'], 'secondary_tileset': ts,
                                'border_filepath': f'{d}/border.bin', 'blockdata_filepath': f'{d}/map.bin'})
        added = True
# The way in: the SEVAULT CANYON cave-door metatile (as at the TANOBY KEY) set into the
# cliff above the canyon's top plateau, at (10,3), on the plateau's elevation 3.
import struct
CANYON = R + '/data/layouts/SevenIsland_SevaultCanyon/map.bin'
cb = bytearray(open(CANYON, 'rb').read())
struct.pack_into('<H', cb, (3 * 24 + 10) * 2, 0x0A9 | (3 << 12))
open(CANYON, 'wb').write(cb)

if added:
    open(R + '/data/layouts/layouts.json', 'w').write(json.dumps(lays, indent=2, ensure_ascii=False) + '\n')
print('ok')
