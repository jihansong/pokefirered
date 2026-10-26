// Adapted from pinned HnS JohtoGeneral callbacks, not generated artwork.
static void TilesetAnim_TYHnsJohtoGeneral(u16);
static void QueueAnimTiles_TYHnsJohtoGeneral_Flower(u16);
static void QueueAnimTiles_TYHnsJohtoGeneral_SandWaterEdge(u16);
static void QueueAnimTiles_TYHnsJohtoGeneral_Waterfall(u16);
static void QueueAnimTiles_TYHnsJohtoGeneral_LandWaterEdge(u16);

static const u16 sTYHnsJohtoGeneral_Flower_Frame0[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/flower/0.4bpp");
static const u16 sTYHnsJohtoGeneral_Flower_Frame1[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/flower/1.4bpp");
static const u16 sTYHnsJohtoGeneral_Flower_Frame2[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/flower/2.4bpp");
static const u16 sTYHnsJohtoGeneral_Flower_Frame3[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/flower/3.4bpp");
static const u16 sTYHnsJohtoGeneral_Flower_Frame4[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/flower/4.4bpp");

static const u16 *const sTYHnsJohtoGeneral_Flower[] = {
    sTYHnsJohtoGeneral_Flower_Frame0,
    sTYHnsJohtoGeneral_Flower_Frame1,
    sTYHnsJohtoGeneral_Flower_Frame2,
    sTYHnsJohtoGeneral_Flower_Frame3,
    sTYHnsJohtoGeneral_Flower_Frame4
};

static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame0[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/0.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame1[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/1.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame2[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/2.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame3[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/3.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame4[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/4.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame5[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/5.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame6[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/6.4bpp");
static const u16 sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame7[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/water_current_landwatersedge/7.4bpp");

static const u16 *const sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge[] = {
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame0,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame1,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame2,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame3,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame4,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame5,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame6,
    sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge_Frame7
};

static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame0[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/0.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame1[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/1.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame2[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/2.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame3[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/3.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame4[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/4.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame5[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/5.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame6[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/6.4bpp");
static const u16 sTYHnsJohtoGeneral_SandWatersEdge_Frame7[] = INCBIN_U16("data/tilesets/primary/ty_hns_johto_general/anim/sandwatersedge/7.4bpp");

static const u16 *const sTYHnsJohtoGeneral_SandWatersEdge[] = {
    sTYHnsJohtoGeneral_SandWatersEdge_Frame0,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame1,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame2,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame3,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame4,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame5,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame6,
    sTYHnsJohtoGeneral_SandWatersEdge_Frame7
};

void InitTilesetAnim_TYHnsJohtoGeneral(void)
{
    sPrimaryTilesetAnimCounter = 0;
    sPrimaryTilesetAnimCounterMax = 256;
    sPrimaryTilesetAnimCallback = TilesetAnim_TYHnsJohtoGeneral;
}

static void TilesetAnim_TYHnsJohtoGeneral(u16 timer)
{
    if (timer % 8 == 0)
        QueueAnimTiles_TYHnsJohtoGeneral_SandWaterEdge(timer >> 3);
    if (timer % 16 == 1)
        QueueAnimTiles_TYHnsJohtoGeneral_LandWaterEdge(timer >> 4);
    if (timer % 16 == 2)
        QueueAnimTiles_TYHnsJohtoGeneral_Flower(timer >> 4);
    if (timer % 16 == 3)
        QueueAnimTiles_TYHnsJohtoGeneral_Waterfall(timer / 16);
}

static void QueueAnimTiles_TYHnsJohtoGeneral_Flower(u16 timer)
{
    u16 i = timer % ARRAY_COUNT(sTYHnsJohtoGeneral_Flower);
    AppendTilesetAnimToBuffer(sTYHnsJohtoGeneral_Flower[i], (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(508)), 4 * TILE_SIZE_4BPP);
}

static void QueueAnimTiles_TYHnsJohtoGeneral_SandWaterEdge(u16 timer)
{
    u16 i = timer % ARRAY_COUNT(sTYHnsJohtoGeneral_SandWatersEdge);
    AppendTilesetAnimToBuffer(sTYHnsJohtoGeneral_SandWatersEdge[i], (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(416)), 18 * TILE_SIZE_4BPP);
}

static void QueueAnimTiles_TYHnsJohtoGeneral_Waterfall(u16 timer)
{
    u16 i = timer % ARRAY_COUNT(sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge);
    const u16 *frame = sTYHnsJohtoGeneral_WaterCurrentLandWatersEdge[i];
    const u16 *src = frame + (34 * (TILE_SIZE_4BPP / 2));
    AppendTilesetAnimToBuffer(src, (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(450)), 12 * TILE_SIZE_4BPP);
}

static void QueueAnimTiles_TYHnsJohtoGeneral_LandWaterEdge(u16 timer)
{
    return;
}

