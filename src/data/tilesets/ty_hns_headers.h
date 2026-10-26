void InitTilesetAnim_TYHnsJohtoGeneral(void);

const struct Tileset gTileset_TYHnsJohtoGeneral =
{
    .isCompressed = TRUE,
    .isSecondary = FALSE,
    .isEmerald = FALSE,
    .tiles = gTilesetTiles_TYHnsJohtoGeneral,
    .palettes = gTilesetPalettes_TYHnsJohtoGeneral,
    .metatiles = gMetatiles_TYHnsJohtoGeneral,
    .metatileAttributes = gMetatileAttributes_TYHnsJohtoGeneral,
    .callback = InitTilesetAnim_TYHnsJohtoGeneral,
};

const struct Tileset gTileset_TYHnsNewBarkTown =
{
    .isCompressed = TRUE,
    .isSecondary = TRUE,
    .isEmerald = FALSE,
    .tiles = gTilesetTiles_TYHnsNewBarkTown,
    .palettes = gTilesetPalettes_TYHnsNewBarkTown,
    .metatiles = gMetatiles_TYHnsNewBarkTown,
    .metatileAttributes = gMetatileAttributes_TYHnsNewBarkTown,
    .callback = NULL,
};

const struct Tileset gTileset_TYHnsCherryFrontier =
{
    .isCompressed = TRUE,
    .isSecondary = TRUE,
    .isEmerald = FALSE,
    .tiles = gTilesetTiles_TYHnsCherryFrontier,
    .palettes = gTilesetPalettes_TYHnsCherryFrontier,
    .metatiles = gMetatiles_TYHnsCherryFrontier,
    .metatileAttributes = gMetatileAttributes_TYHnsCherryFrontier,
    .callback = NULL,
};

const struct Tileset gTileset_TYHnsJohtoBuilding =
{
    .isCompressed = TRUE,
    .isSecondary = FALSE,
    .isEmerald = FALSE,
    .tiles = gTilesetTiles_TYHnsJohtoBuilding,
    .palettes = gTilesetPalettes_TYHnsJohtoBuilding,
    .metatiles = gMetatiles_TYHnsJohtoBuilding,
    .metatileAttributes = gMetatileAttributes_TYHnsJohtoBuilding,
    .callback = NULL,
};
const struct Tileset gTileset_TYHnsHouseLab =
{
    .isCompressed = TRUE,
    .isSecondary = TRUE,
    .isEmerald = FALSE,
    .tiles = gTilesetTiles_TYHnsHouseLab,
    .palettes = gTilesetPalettes_TYHnsHouseLab,
    .metatiles = gMetatiles_TYHnsHouseLab,
    .metatileAttributes = gMetatileAttributes_TYHnsHouseLab,
    .callback = NULL,
};
