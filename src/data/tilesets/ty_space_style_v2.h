// Original Emerald pixel/palette variants for five appended space maps.
static const u32 sTYSpaceStyleV2InteriorTiles[] = INCBIN_U32("data/tilesets/secondary/ty_space_interior_v3/tiles.4bpp");
static const u16 sTYSpaceStyleV2InteriorPalettes[][16] = INCBIN_U16("data/tilesets/secondary/ty_space_interior_v3/palettes.gbapal");
static const u16 sTYSpaceStyleV2InteriorMetatiles[] = INCBIN_U16("data/tilesets/secondary/ty_space_interior_v3/metatiles.bin");
static const u32 sTYSpaceStyleV2InteriorAttributes[] = INCBIN_U32("data/tilesets/secondary/ty_space_interior_v3/metatile_attributes.bin");
const struct Tileset gTileset_TYSpaceStyleV2Interior = {
    .isCompressed = FALSE, .isSecondary = TRUE, .isEmerald = TRUE,
    .tiles = sTYSpaceStyleV2InteriorTiles, .palettes = sTYSpaceStyleV2InteriorPalettes,
    .metatiles = sTYSpaceStyleV2InteriorMetatiles, .metatileAttributes = sTYSpaceStyleV2InteriorAttributes,
    .callback = NULL,
};
static const u32 sTYSpaceStyleV2LaunchTiles[] = INCBIN_U32("data/tilesets/secondary/ty_space_style_v2_launch/tiles.4bpp");
static const u16 sTYSpaceStyleV2LaunchPalettes[][16] = INCBIN_U16("data/tilesets/secondary/ty_space_style_v2_launch/palettes.gbapal");
static const u16 sTYSpaceStyleV2LaunchMetatiles[] = INCBIN_U16("data/tilesets/secondary/ty_space_style_v2_launch/metatiles.bin");
static const u32 sTYSpaceStyleV2LaunchAttributes[] = INCBIN_U32("data/tilesets/secondary/ty_space_style_v2_launch/metatile_attributes.bin");
const struct Tileset gTileset_TYSpaceStyleV2Launch = {
    .isCompressed = FALSE, .isSecondary = TRUE, .isEmerald = TRUE,
    .tiles = sTYSpaceStyleV2LaunchTiles, .palettes = sTYSpaceStyleV2LaunchPalettes,
    .metatiles = sTYSpaceStyleV2LaunchMetatiles, .metatileAttributes = sTYSpaceStyleV2LaunchAttributes,
    .callback = NULL,
};
