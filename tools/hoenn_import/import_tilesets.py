#!/usr/bin/env python3
"""Import pokeemerald tilesets into pokefirered as gTileset_Hoenn<Name> (isEmerald = TRUE).
Metatile attributes are converted from Emerald's u16 (behavior | layer<<12) to FR/LG's u32."""
import re, os, shutil, struct, json, sys
EM = '/root/src/pokeemerald'
FR = '/workspaces/pokefirered'

def load_mb(path):
    s = open(path).read()
    out = {}
    enum = re.findall(r'^\s*(MB_\w+)\s*(?:=\s*(\w+))?,', s, re.M)
    if enum:
        i = 0
        for n, v in enum:
            if v: i = int(v, 0)
            out[n] = i; i += 1
    for n, v in re.findall(r'#define (MB_\w+) (0x[0-9A-Fa-f]+|\d+)', s):
        out[n] = int(v, 0)
    return out
EMB = load_mb(EM + '/include/constants/metatile_behaviors.h')
FMB = load_mb(FR + '/include/constants/metatile_behaviors.h')
EMB_BY_NUM = {v: k for k, v in EMB.items()}
MANUAL = {
    'MB_SECRET_BASE_WALL': 'MB_NORMAL', 'MB_LONG_GRASS': 'MB_TALL_GRASS', 'MB_DEEP_SAND': 'MB_SAND',
    'MB_SHORT_GRASS': 'MB_NORMAL', 'MB_LONG_GRASS_SOUTH_EDGE': 'MB_NORMAL', 'MB_NO_RUNNING': 'MB_RUNNING_DISALLOWED',
    'MB_BATTLE_PYRAMID_WARP': 'MB_REGULAR_WARP', 'MB_MOSSDEEP_GYM_WARP': 'MB_REGULAR_WARP', 'MB_MT_PYRE_HOLE': 'MB_FALL_WARP',
    'MB_INTERIOR_DEEP_WATER': 'MB_DEEP_WATER', 'MB_SOOTOPOLIS_DEEP_WATER': 'MB_DEEP_WATER', 'MB_UNUSED_SOOTOPOLIS_DEEP_WATER': 'MB_DEEP_WATER',
    'MB_NO_SURFACING': 'MB_DEEP_WATER', 'MB_UNUSED_SOOTOPOLIS_DEEP_WATER_2': 'MB_DEEP_WATER',
    'MB_STAIRS_OUTSIDE_ABANDONED_SHIP': 'MB_REGULAR_WARP', 'MB_SHOAL_CAVE_ENTRANCE': 'MB_NORMAL',
    'MB_ASHGRASS': 'MB_TALL_GRASS', 'MB_FOOTPRINTS': 'MB_SAND', 'MB_LAVARIDGE_GYM_B1F_WARP': 'MB_REGULAR_WARP',
    'MB_SEAWEED_NO_SURFACING': 'MB_SEAWEED', 'MB_REFLECTION_UNDER_BRIDGE': 'MB_NORMAL',
    'MB_JUMP_NORTHEAST': 'MB_NORMAL', 'MB_JUMP_NORTHWEST': 'MB_NORMAL', 'MB_JUMP_SOUTHEAST': 'MB_NORMAL', 'MB_JUMP_SOUTHWEST': 'MB_NORMAL',
    'MB_NON_ANIMATED_DOOR': 'MB_REGULAR_WARP', 'MB_CRACKED_FLOOR_HOLE': 'MB_FALL_WARP', 'MB_AQUA_HIDEOUT_WARP': 'MB_REGULAR_WARP',
    'MB_LAVARIDGE_GYM_1F_WARP': 'MB_LAVARIDGE_1F_WARP', 'MB_ANIMATED_DOOR': 'MB_WARP_DOOR', 'MB_WATER_DOOR': 'MB_REGULAR_WARP',
    'MB_WATER_SOUTH_ARROW_WARP': 'MB_SOUTH_ARROW_WARP', 'MB_DEEP_SOUTH_WARP': 'MB_SOUTH_ARROW_WARP',
    'MB_CABLE_BOX_RESULTS_1': 'MB_BATTLE_RECORDS', 'MB_CABLE_BOX_RESULTS_2': 'MB_BATTLE_RECORDS', 'MB_WIRELESS_BOX_RESULTS': 'MB_CABLE_CLUB_WIRELESS_MONITOR',
    'MB_PLAYER_ROOM_PC_ON': 'MB_PC', 'MB_PICTURE_BOOK_SHELF': 'MB_BOOKSHELF', 'MB_POKEMON_CENTER_BOOKSHELF': 'MB_BOOKSHELF',
    'MB_TRASH_CAN': 'MB_TRASH_BIN', 'MB_SHOP_SHELF': 'MB_POKEMART_SHELF', 'MB_BLUEPRINT': 'MB_BLUEPRINTS',
}
ENCOUNTER = {'MB_TALL_GRASS', 'MB_LONG_GRASS', 'MB_UNUSED_05', 'MB_DEEP_SAND', 'MB_CAVE', 'MB_INDOOR_ENCOUNTER', 'MB_ASHGRASS', 'MB_FOOTPRINTS'}
WATER_ENC = {'MB_POND_WATER', 'MB_INTERIOR_DEEP_WATER', 'MB_DEEP_WATER', 'MB_SOOTOPOLIS_DEEP_WATER', 'MB_OCEAN_WATER', 'MB_NO_SURFACING',
             'MB_SEAWEED', 'MB_SEAWEED_NO_SURFACING', 'MB_EASTWARD_CURRENT', 'MB_WESTWARD_CURRENT', 'MB_NORTHWARD_CURRENT', 'MB_SOUTHWARD_CURRENT',
             'MB_WATER_DOOR', 'MB_WATER_SOUTH_ARROW_WARP', 'MB_WATERFALL'}
GRASS = {'MB_TALL_GRASS', 'MB_LONG_GRASS', 'MB_ASHGRASS'}
unmapped = {}
def convert_attr(v):
    beh = EMB_BY_NUM.get(v & 0xFF, 'MB_NORMAL'); layer = (v >> 12) & 0xF
    name = beh if beh in FMB else MANUAL.get(beh)
    if name is None:
        unmapped[beh] = unmapped.get(beh, 0) + 1; name = 'MB_NORMAL'
    enc = 2 if beh in WATER_ENC else (1 if beh in ENCOUNTER else 0)
    terrain = 3 if beh == 'MB_WATERFALL' else (2 if beh in WATER_ENC else (1 if beh in GRASS else 0))
    return FMB[name] | (terrain << 9) | (enc << 24) | ((layer & 3) << 29)

def snake(n): return re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', n).lower()

def main(names):
    hdr = open(EM + '/src/data/tilesets/headers.h').read()
    gfx = open(EM + '/src/data/tilesets/graphics.h').read() + open(EM + '/src/graphics.c').read()
    mts = open(EM + '/src/data/tilesets/metatiles.h').read() + open(EM + '/src/graphics.c').read()
    headers, graphics, metatiles, rules = [], [], [], []
    for name in names:
        m = re.search(r'const struct Tileset gTileset_%s =\s*\{(.*?)\};' % name, hdr, re.S)
        body = m.group(1)
        secondary = 'isSecondary = TRUE' in body
        tsym = re.search(r'\.tiles = gTilesetTiles_(\w+)', body).group(1)
        msym = re.search(r'\.metatiles = gMetatiles_(\w+)', body).group(1)
        tm = re.search(r'gTilesetTiles_%s\[\] = INCGFX_U32\("([^"]+)/tiles\.png", "[^"]*"(?:, "-num_tiles (\d+))?' % tsym, gfx)
        if tm is None:
            print('no tiles for', name); continue
        srcdir = tm.group(1)
        ntiles = int(tm.group(2)) if tm.group(2) else None
        mm = re.search(r'gMetatiles_%s\[\] = INCBIN_U16\("([^"]+)/metatiles\.bin"\)' % msym, mts)
        mdir = mm.group(1)
        new = 'Em' + name
        kind = 'secondary' if secondary else 'primary'
        dst = f'data/tilesets/{kind}/{snake(new)}'
        os.makedirs(FR + '/' + dst + '/palettes', exist_ok=True)
        shutil.copy(f'{EM}/{srcdir}/tiles.png', f'{FR}/{dst}/tiles.png')
        for p in range(16):
            shutil.copy(f'{EM}/{srcdir}/palettes/{p:02d}.pal', f'{FR}/{dst}/palettes/{p:02d}.pal')
        shutil.copy(f'{EM}/{mdir}/metatiles.bin', f'{FR}/{dst}/metatiles.bin')
        a = open(f'{EM}/{mdir}/metatile_attributes.bin', 'rb').read()
        vals = struct.unpack(f'<{len(a)//2}H', a)
        open(f'{FR}/{dst}/metatile_attributes.bin', 'wb').write(struct.pack(f'<{len(vals)}I', *[convert_attr(v) for v in vals]))
        if ntiles:
            rules.append(f'$(TILESETGFXDIR)/{kind}/{snake(new)}/tiles.4bpp: %.4bpp: %.png\n\t$(GFX) $< $@ -num_tiles {ntiles} -Wnum_tiles\n')
        graphics.append(f'const u32 gTilesetTiles_{new}[] = INCBIN_U32("{dst}/tiles.4bpp.lz");\n\nconst u16 gTilesetPalettes_{new}[][16] =\n{{\n'
                        + ''.join(f'    INCBIN_U16("{dst}/palettes/{p:02d}.gbapal"),\n' for p in range(16)) + '};\n')
        metatiles.append(f'const u16 gMetatiles_{new}[] = INCBIN_U16("{dst}/metatiles.bin");\nconst u32 gMetatileAttributes_{new}[] = INCBIN_U32("{dst}/metatile_attributes.bin");\n')
        headers.append(f'const struct Tileset gTileset_{new} =\n{{\n    .isCompressed = TRUE,\n    .isSecondary = {"TRUE" if secondary else "FALSE"},\n'
                       f'    .isEmerald = TRUE,\n    .tiles = gTilesetTiles_{new},\n    .palettes = gTilesetPalettes_{new},\n'
                       f'    .metatiles = gMetatiles_{new},\n    .metatileAttributes = gMetatileAttributes_{new},\n    .callback = NULL,\n}};\n')
    open(FR + '/src/data/tilesets/hoenn_graphics.h', 'w').write('// Tilesets imported from pokeemerald (Hoenn)\n\n' + '\n'.join(graphics))
    open(FR + '/src/data/tilesets/hoenn_metatiles.h', 'w').write('// Tilesets imported from pokeemerald (Hoenn)\n\n' + '\n'.join(metatiles))
    open(FR + '/src/data/tilesets/hoenn_headers.h', 'w').write('// Tilesets imported from pokeemerald (Hoenn)\n\n' + '\n'.join(headers))
    open(FR + '/hoenn_tileset_rules.mk', 'w').write('# Tilesets imported from pokeemerald (Hoenn)\n\n' + '\n'.join(rules))
    if unmapped: print('unmapped behaviors (-> MB_NORMAL):', unmapped)
    print(len(names), 'tilesets')

if __name__ == '__main__':
    main(json.load(open(sys.argv[1])))
