// Original ride algorithms/assets: pret/pokeemerald 5eff78649e7170a877b961ef0b3da13b81a16038.
// FRLG lifecycle: Task.data+heap only; no new mutable RAM globals.
// Existing MUS_MT_CHIMNEY fallback; no new music or credits changes.
#include "global.h"
#include "gflib.h"
#include "hoenn_cable_car.h"
#include "help_system.h"
#include "field_player_avatar.h"
#include "field_fadetransition.h"
#include "script_movement.h"
#include "follower_pikachu.h"
#include "companion_misty.h"
#include "quest_log.h"
#include "constants/maps.h"
#include "constants/game_stat.h"
#include "constants/quest_log.h"
#include "bg.h"
#include "decompress.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_weather.h"
#include "gpu_regs.h"
#include "graphics.h"
#include "malloc.h"
#include "main.h"
#include "menu.h"
#include "new_menu_helpers.h"
#include "overworld.h"
#include "palette.h"
#include "random.h"
#include "scanline_effect.h"
#include "script.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "constants/event_object_movement.h"
#include "constants/event_objects.h"
#include "constants/rgb.h"
#include "constants/songs.h"
#include "constants/field_weather.h"
#include "constants/weather.h"

#define GOING_DOWN gSpecialVar_0x8004

#define STATE_END 0xFF

enum {
    TAG_CABLE_CAR = 1,
    TAG_DOOR,
    TAG_CABLE,
};

struct CableCar
{
    u8 bgTaskId;
    u8 state;
    u8 weather;
    u16 weatherDelay;
    u16 timer;
    u8 bg0HorizontalOffset;
    u8 bg0VerticalOffset;
    u8 unused0[2];
    u8 bg1HorizontalOffset;
    u8 bg1VerticalOffset;
    u8 unused1[6];
    u8 bg3HorizontalOffset;
    u8 bg3VerticalOffset;
    u8 unused2[2];
    u8 groundTileIdx;
    u8 groundSegmentXStart;
    u8 groundSegmentYStart;
    u8 groundTilemapOffset;
    u8 groundTimer; // Incremented, but does nothing
    u8 groundXOffset;
    u8 groundYOffset;
    u8 groundXBase;
    u8 groundYBase;
    u16 groundTileBuffer[9][12];
    u8 unused3[2];
    u16 bgTilemapBuffers[4][32 * 32];
    u8 groundXUp, groundYUp, groundSegmentYUp;
    u8 groundXDown, groundYDown, groundSegmentYDown;
    bool8 failed;
    const u16 *groundTilemap;
    const u16 *treesTilemap;
    const u16 *bgMountainsTilemap;
    const u16 *pylonTopTilemap;
    const u16 *pylonPoleTilemap;
};


static struct CableCar *GetCableCar(void);
static void CB2_EndCableCar(void);
static void CableCarFieldArrival(void);
static void Task_CableCarArrival(u8 taskId);
static void CableCarSetWeather(u8 weather);
static void TuckCableCarFollowers(void);
static void CB2_LoadCableCar(void);
static void SetBgRegs(bool8);
static void CreateCableCarSprites(void);
static void InitGroundTilemapData(bool8);
static void Task_CableCar(u8);
static void Task_AnimateBgGoingUp(u8);
static void Task_AnimateBgGoingDown(u8);
static void VBlankCB_CableCar(void);
static void CB2_CableCar(void);
static void AnimateGroundGoingUp(void);
static void AnimateGroundGoingDown(void);
static void SpriteCB_CableCar(struct Sprite *);
static void SpriteCB_Cable(struct Sprite *);
static void DrawNextGroundSegmentGoingUp(void);
static void DrawNextGroundSegmentGoingDown(void);

static const struct BgTemplate sBgTemplates[4] = {
    {
        .bg = 0,
        .charBaseIndex = 0,
        .mapBaseIndex = 28,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 1,
        .baseTile = 0
    },
    {
        .bg = 1,
        .charBaseIndex = 0,
        .mapBaseIndex = 29,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 2,
        .baseTile = 0
    },
    {
        .bg = 2,
        .charBaseIndex = 0,
        .mapBaseIndex = 30,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 3,
        .baseTile = 0
    },
    {
        .bg = 3,
        .charBaseIndex = 0,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0
    },
};

extern const u32 gObjectEventPic_HoennCableCar[];
extern const u16 gObjectEventPal_HoennCableCar[];
static const u16 sGround_Tilemap[] = INCBIN_U16("graphics/hoenn_cable_car/ground.bin");
static const u16 sTrees_Tilemap[] = INCBIN_U16("graphics/hoenn_cable_car/trees.bin");
static const u16 sBgMountains_Tilemap[] = INCBIN_U16("graphics/hoenn_cable_car/bg_mountains.bin");
static const u16 sPylonTop_Tilemap[] = INCBIN_U16("graphics/hoenn_cable_car/pylon_top.bin");
static const u16 sPylonPole_Tilemap[] = INCBIN_U16("graphics/hoenn_cable_car/pylon_pole.bin");
static const u32 sBgTiles[] = INCBIN_U32("graphics/hoenn_cable_car/bg.4bpp");
static const u16 sBgPalette[] = INCBIN_U16("graphics/hoenn_cable_car/bg.gbapal");
static const u32 sDoorTiles[] = INCBIN_U32("graphics/hoenn_cable_car/door.4bpp");
static const u32 sCableTiles[] = INCBIN_U32("graphics/hoenn_cable_car/cable.4bpp");
static const struct SpriteSheet sSpriteSheets[] = {
    { gObjectEventPic_HoennCableCar, 0x800, TAG_CABLE_CAR },
    { sDoorTiles, 0x40, TAG_DOOR },
    { sCableTiles, 0x80, TAG_CABLE },
};
static const struct SpritePalette sSpritePalette = { gObjectEventPal_HoennCableCar, TAG_CABLE_CAR };

static const struct OamData sOam_CableCar =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_DOUBLE,
    .objMode = ST_OAM_OBJ_NORMAL,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(64x64),
    .x = 0,
    .size = SPRITE_SIZE(64x64),
    .tileNum = 0,
    .priority = 2,
    .paletteNum = 0,
};

static const struct OamData sOam_CableCarDoor =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_DOUBLE,
    .objMode = ST_OAM_OBJ_NORMAL,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x8),
    .x = 0,
    .size = SPRITE_SIZE(16x8),
    .tileNum = 0,
    .priority = 2,
    .paletteNum = 0,
};

static const struct OamData sOam_Cable =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_DOUBLE,
    .objMode = ST_OAM_OBJ_NORMAL,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x16),
    .x = 0,
    .size = SPRITE_SIZE(16x16),
    .tileNum = 0,
    .priority = 2,
    .paletteNum = 0,
};

static const struct SpriteTemplate sSpriteTemplates_CableCar[] =
{
    {
        .tileTag = TAG_CABLE_CAR,
        .paletteTag = TAG_CABLE_CAR,
        .oam = &sOam_CableCar,
        .anims = gDummySpriteAnimTable,
        .images = NULL,
        .affineAnims = gDummySpriteAffineAnimTable,
        .callback = SpriteCB_CableCar,
    },
    {
        .tileTag = TAG_DOOR,
        .paletteTag = TAG_CABLE_CAR,
        .oam = &sOam_CableCarDoor,
        .anims = gDummySpriteAnimTable,
        .images = NULL,
        .affineAnims = gDummySpriteAffineAnimTable,
        .callback = SpriteCB_CableCar,
    },
};

static const struct SpriteTemplate sSpriteTemplate_Cable =
{
    .tileTag = TAG_CABLE,
    .paletteTag = TAG_CABLE_CAR,
    .oam = &sOam_Cable,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_Cable,
};

static void Task_LoadCableCar(u8 taskId)
{
    if (!gPaletteFade.active)
    {
        SetMainCallback2(CB2_LoadCableCar);
        DestroyTask(taskId);
    }
}

bool8 HoennCableCarRide(void)
{
    u8 taskId;
    // Playback must not change direction, destination, stats or live field state.
    if (QL_IS_PLAYBACK_STATE)
        return FALSE;
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_ROUTE112_CABLE_CAR_STATION)
     || gSaveBlock1Ptr->location.mapNum > MAP_NUM(MAP_MT_CHIMNEY_CABLE_CAR_STATION)
     || GOING_DOWN != (gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_MT_CHIMNEY_CABLE_CAR_STATION))
     || GOING_DOWN > 1 || FuncIsActiveTask(Task_LoadCableCar)
     || FuncIsActiveTask(Task_CableCar) || GetTaskCount() >= NUM_TASKS)
        return FALSE;
    taskId = CreateTask(Task_LoadCableCar, 1);
    if (taskId == TASK_NONE)
        return FALSE;
    LockPlayerFieldControls();
    HelpSystem_Disable();
    TuckCableCarFollowers();
    BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
    return TRUE;
}

static void CB2_LoadCableCar(void)
{
    u8 i;
    u8 owner;
    struct CableCar *ctx;
    switch (gMain.state)
    {
    case 0:
    default:
        SetVBlankCallback(NULL);
        SetBgRegs(FALSE);
        ScanlineEffect_Stop();
        DmaFillLarge16(3, 0, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, (void *)OAM, OAM_SIZE);
        DmaClear16(3, (void *)PLTT, PLTT_SIZE);
        // Reset before creating the one task that owns the heap allocation.
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
        owner = CreateTask(Task_CableCar, 0);
        ctx = AllocZeroed(sizeof(*ctx));
        SetWordTaskArg(owner, 14, (u32)ctx);
        if (ctx == NULL)
        {
            SetMainCallback2(CB2_EndCableCar);
            return;
        }
        gMain.state++;
        break;
    case 1:
        ResetPaletteFade();
        ResetTempTileDataBuffers();
        StartWeather();
        for (i = 0; i < NUM_ASH_SPRITES; i++)
            gWeatherPtr->sprites.s2.ashSprites[i] = NULL;
        InitMapMusic();
        ResetMapMusic();
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sBgTemplates, ARRAY_COUNT(sBgTemplates));
        for (i = 0; i < 4; i++)
            SetBgTilemapBuffer(i, GetCableCar()->bgTilemapBuffers[i]);
        gSpriteCoordOffsetX = gSpriteCoordOffsetY = 0;
        gMain.state++;
        break;
    case 2:
        for (i = 0; i < ARRAY_COUNT(sSpriteSheets); i++)
        {
            LoadSpriteSheet(&sSpriteSheets[i]);
            if (GetSpriteTileStartByTag(sSpriteSheets[i].tag) == 0xFFFF)
            {
                GetCableCar()->failed = TRUE;
                SetMainCallback2(CB2_EndCableCar);
                return;
            }
        }
        if (LoadSpritePalette(&sSpritePalette) == 0xFF
         || LoadBgTiles(0, sBgTiles, sizeof(sBgTiles), 0) == 0xFFFF)
        {
            GetCableCar()->failed = TRUE;
            SetMainCallback2(CB2_EndCableCar);
            return;
        }
        GetCableCar()->groundTilemap = sGround_Tilemap;
        GetCableCar()->treesTilemap = sTrees_Tilemap;
        GetCableCar()->bgMountainsTilemap = sBgMountains_Tilemap;
        GetCableCar()->pylonPoleTilemap = sPylonPole_Tilemap;
        GetCableCar()->pylonTopTilemap = sPylonTop_Tilemap;
        gMain.state++;
        break;
    case 3:
        if (!IsDma3ManagerBusyWithBgCopy())
        {
            LoadPalette(sBgPalette, BG_PLTT_ID(0), sizeof(sBgPalette));
            gMain.state++;
        }
        break;
    case 4:
        CreateCableCarSprites();
        if (GetCableCar()->failed)
        {
            SetMainCallback2(CB2_EndCableCar);
            return;
        }
        RunTasks();
        gMain.state++;
        break;
    case 5:
        RunTasks();
        AnimateSprites();
        owner = FindTaskIdByFunc(Task_CableCar);
        if (++gTasks[owner].data[1] >= 300)
        {
            GetCableCar()->failed = TRUE;
            SetMainCallback2(CB2_EndCableCar);
        }
        else if (GetCableCar()->weather == WEATHER_VOLCANIC_ASH
              || gWeatherPtr->sprites.s2.ashSprites[0] != NULL)
            gMain.state++;
        break;
    case 6:
        CopyToBgTilemapBufferRect_ChangePalette(1, GetCableCar()->treesTilemap, 0, 17, 32, 15, 17);
        CopyToBgTilemapBufferRect_ChangePalette(2, GetCableCar()->bgMountainsTilemap, 0, 0, 30, 20, 17);
        CopyToBgTilemapBufferRect_ChangePalette(3, GetCableCar()->pylonTopTilemap, 0, 0, 5, 2, 17);
        CopyToBgTilemapBufferRect_ChangePalette(3, GetCableCar()->pylonPoleTilemap, 0, 2, 2, 20, 17);
        gMain.state++;
        break;
    case 7:
        InitGroundTilemapData(GOING_DOWN);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x48, 0, 14, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x6C, 12, 17, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x90, 24, 20, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap, 0, 17, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x24, 0, 20, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap, 12, 20, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x24, 12, 23, 12, 3, 17);
        CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap, 24, 23, 12, 3, 17);
        gMain.state++;
        break;
    case 8:
        BeginNormalPaletteFade(PALETTES_ALL, 3, 16, 0, RGB_BLACK);
        FadeInNewBGM(MUS_MT_CHIMNEY, 1);
        SetBgRegs(TRUE);
        gMain.state++;
        break;
    case 9:
        owner = FindTaskIdByFunc(Task_CableCar);
        if (GetTaskCount() >= NUM_TASKS)
        {
            GetCableCar()->failed = TRUE;
            SetMainCallback2(CB2_EndCableCar);
            return;
        }
        GetCableCar()->bgTaskId = CreateTask(GOING_DOWN ? Task_AnimateBgGoingDown : Task_AnimateBgGoingUp, 1);
        if (GetCableCar()->bgTaskId == TASK_NONE)
        {
            GetCableCar()->failed = TRUE;
            SetMainCallback2(CB2_EndCableCar);
            return;
        }
        gTasks[owner].data[0] = 1;
        SetVBlankCallback(VBlankCB_CableCar);
        SetMainCallback2(CB2_CableCar);
        break;
    }
}

static void CB2_CableCar(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
    MapMusicMain();
}

static void CB2_EndCableCar(void)
{
    u8 i;
    struct CableCar *ctx = GetCableCar();
    bool8 completed = ctx != NULL && !ctx->failed && ctx->state == STATE_END;
    u8 source = gSaveBlock1Ptr->location.mapNum;
    u8 destination = completed ? (GOING_DOWN ? MAP_NUM(MAP_ROUTE112_CABLE_CAR_STATION) : MAP_NUM(MAP_MT_CHIMNEY_CABLE_CAR_STATION)) : source;
    SetVBlankCallback(NULL);
    for (i = 0; i < 4; i++)
    {
        HideBg(i);
        UnsetBgTilemapBuffer(i);
    }
    SetBgRegs(FALSE);
    gSpriteCoordOffsetX = gSpriteCoordOffsetY = 0;
    CableCarSetWeather(WEATHER_NONE);
    for (i = 0; i < NUM_ASH_SPRITES; i++)
        gWeatherPtr->sprites.s2.ashSprites[i] = NULL;
    // Stop every consumer before freeing. No ResetTasks occurs while it owns a live pointer.
    ResetSpriteData();
    FreeAllSpritePalettes();
    if (ctx != NULL)
        Free(ctx);
    ResetTasks();
    ResetPaletteFade();
    ResetBgsAndClearDma3BusyFlags(0);
    DmaFillLarge16(3, 0, (void *)VRAM, VRAM_SIZE, 0x1000);
    DmaClear32(3, (void *)OAM, OAM_SIZE);
    DmaClear16(3, (void *)PLTT, PLTT_SIZE);
    if (completed)
        IncrementGameStat(GAME_STAT_RODE_CABLE_CAR);
    SetWarpDestination(MAP_GROUP(MAP_ROUTE112_CABLE_CAR_STATION), destination, WARP_ID_NONE, 6, 4);
    WarpIntoMap();
    gFieldCallback = CableCarFieldArrival;
    SetMainCallback2(CB2_LoadMap);
}

static void Task_CableCar(u8 taskId)
{
    u8 i = 0;

    if (gTasks[taskId].data[0] == 0)
        return;
    GetCableCar()->timer++;
    if (GetCableCar()->timer >= 900 && GetCableCar()->state < 3)
    {
        GetCableCar()->failed = TRUE;
        GetCableCar()->state = 3;
        BeginNormalPaletteFade(PALETTES_ALL, 3, 0, 16, RGB_BLACK);
    }
    switch (GetCableCar()->state)
    {
    case 0:
        // Wait to change weather
        if (GetCableCar()->timer == GetCableCar()->weatherDelay)
        {
            SetNextWeather(GetCableCar()->weather);
            GetCableCar()->state = 1;
        }
        break;
    case 1:
        // Update ash sprites
        switch (GetCableCar()->weather)
        {
        case WEATHER_VOLCANIC_ASH:
            if (gWeatherPtr->sprites.s2.ashSprites[0] != NULL && gWeatherPtr->sprites.s2.ashSprites[0]->oam.priority != 0)
            {
                for (; i < NUM_ASH_SPRITES; i++)
                {
                    if (gWeatherPtr->sprites.s2.ashSprites[i])
                        gWeatherPtr->sprites.s2.ashSprites[i]->oam.priority = 0;
                }

                GetCableCar()->state = 2;
            }
            break;
        case WEATHER_SUNNY:
            if (gWeatherPtr->currWeather == WEATHER_SUNNY)
            {
                GetCableCar()->state = 2;
            }
            else if (GetCableCar()->timer >= GetCableCar()->weatherDelay + 8)
            {
                for (; i < NUM_ASH_SPRITES; i++)
                {
                    if (gWeatherPtr->sprites.s2.ashSprites[i])
                        gWeatherPtr->sprites.s2.ashSprites[i]->invisible ^= 1;
                }
            }
            break;
        }
        break;
    case 2:
        // Wait to fade out
        if (GetCableCar()->timer >= 570)
        {
            GetCableCar()->state = 3;
            BeginNormalPaletteFade(PALETTES_ALL, 3, 0, 16, RGB_BLACK);
            FadeOutBGM(4);
        }
        break;
    case 3:
        // Wait for fade out
        if (!gPaletteFade.active)
            GetCableCar()->state = STATE_END;
        break;
    case STATE_END:
        SetVBlankCallback(NULL);
        DestroyTask(GetCableCar()->bgTaskId);
        gTasks[taskId].data[0] = 0;
        SetMainCallback2(CB2_EndCableCar);
        break;
    }
}

static void Task_AnimateBgGoingUp(u8 taskId)
{
    if (GetCableCar()->state != STATE_END)
    {
        GetCableCar()->bg3HorizontalOffset--;
        if ((GetCableCar()->timer % 2) == 0)
            GetCableCar()->bg3VerticalOffset--;

        if ((GetCableCar()->timer % 8) == 0)
        {
            GetCableCar()->bg1HorizontalOffset--;
            GetCableCar()->bg1VerticalOffset--;
        }

        switch (GetCableCar()->bg3HorizontalOffset)
        {
        case 175:
            FillBgTilemapBufferRect(3, 0, 0, 22, 2, 10, 17);
            break;
        case 40:
            FillBgTilemapBufferRect(3, 0, 3, 0, 2, 2, 17);
            break;
        case 32:
            FillBgTilemapBufferRect(3, 0, 2, 0, 1, 2, 17);
            break;
        case 16:
            CopyToBgTilemapBufferRect_ChangePalette(3, GetCableCar()->pylonTopTilemap, 0, 0, 5,  2, 17);
            CopyToBgTilemapBufferRect_ChangePalette(3, GetCableCar()->pylonPoleTilemap, 0, 2, 2, 30, 17);
            GetCableCar()->bg3VerticalOffset = 64;
            break;
        }
    }

    AnimateGroundGoingUp();
    gSpriteCoordOffsetX = (gSpriteCoordOffsetX + 1) % 128;
}

static void Task_AnimateBgGoingDown(u8 taskId)
{
    if (GetCableCar()->state != STATE_END)
    {
        GetCableCar()->bg3HorizontalOffset++;
        if ((GetCableCar()->timer % 2) == 0)
            GetCableCar()->bg3VerticalOffset++;

        if ((GetCableCar()->timer % 8) == 0)
        {
            GetCableCar()->bg1HorizontalOffset++;
            GetCableCar()->bg1VerticalOffset++;
        }

        switch (GetCableCar()->bg3HorizontalOffset)
        {
        case 176:
            CopyToBgTilemapBufferRect_ChangePalette(3, GetCableCar()->pylonPoleTilemap, 0, 2, 2, 30, 17);
            break;
        case 16:
            FillBgTilemapBufferRect(3, 0, 2,  0, 3,  2, 17);
            FillBgTilemapBufferRect(3, 0, 0, 22, 2, 10, 17);
            GetCableCar()->bg3VerticalOffset = 192;
            break;
        case 32:
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[2], 2, 0, 1, 1, 17);
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[3], 3, 0, 1, 1, 17);
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[7], 2, 1, 1, 1, 17);
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[8], 3, 1, 1, 1, 17);
            break;
        case 40:
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[4], 4, 0, 1, 1, 17);
            FillBgTilemapBufferRect(3, GetCableCar()->pylonTopTilemap[9], 4, 1, 1, 1, 17);
            break;
        }
    }

    AnimateGroundGoingDown();
    if (GetCableCar()->timer < GetCableCar()->weatherDelay)
        gSpriteCoordOffsetX = (gSpriteCoordOffsetX + 247) % 248;
    else
        gWeatherPtr->ashBaseSpritesX = (gWeatherPtr->ashBaseSpritesX + 247) % 248;
}

static void VBlankCB_CableCar(void)
{
    CopyBgTilemapBufferToVram(0);
    CopyBgTilemapBufferToVram(3);
    SetGpuReg(REG_OFFSET_BG3HOFS, GetCableCar()->bg3HorizontalOffset);
    SetGpuReg(REG_OFFSET_BG3VOFS, GetCableCar()->bg3VerticalOffset);
    SetGpuReg(REG_OFFSET_BG1HOFS, GetCableCar()->bg1HorizontalOffset);
    SetGpuReg(REG_OFFSET_BG1VOFS, GetCableCar()->bg1VerticalOffset);
    SetGpuReg(REG_OFFSET_BG0HOFS, GetCableCar()->bg0HorizontalOffset);
    SetGpuReg(REG_OFFSET_BG0VOFS, GetCableCar()->bg0VerticalOffset);
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void SpriteCB_Cable(struct Sprite *sprite)
{

}

#define sXPos  data[0]
#define sYPos  data[1]

static void SpriteCB_CableCar(struct Sprite *sprite)
{
    if (GetCableCar()->state != STATE_END)
    {
        if (!GOING_DOWN)
        {
            sprite->x = sprite->sXPos - (u8)(14 * GetCableCar()->timer / 100);
            sprite->y = sprite->sYPos - (u8)(67 * GetCableCar()->timer / 1000);
        }
        else
        {
            sprite->x = sprite->sXPos + (u8)(14 * GetCableCar()->timer / 100);
            sprite->y = sprite->sYPos + (u8)(67 * GetCableCar()->timer / 1000);
        }
    }
}

#define sState data[2]
#define sTimer data[3]

static void SpriteCB_Player(struct Sprite *sprite)
{
    if (GetCableCar()->state != STATE_END)
    {
        // Move along with cable car
        if (!GOING_DOWN)
        {
            sprite->x = sprite->sXPos - (u8)(14 * GetCableCar()->timer / 100);
            sprite->y = sprite->sYPos - (u8)(67 * GetCableCar()->timer / 1000);
        }
        else
        {
            sprite->x = sprite->sXPos + (u8)(14 * GetCableCar()->timer / 100);
            sprite->y = sprite->sYPos + (u8)(67 * GetCableCar()->timer / 1000);
        }

        // Bounce up and down
        switch (sprite->sState)
        {
        case 0:
            sprite->y2 = 17;
            if (sprite->sTimer++ > 9)
            {
                sprite->sTimer = 0;
                sprite->sState++;
            }
            break;
        default:
            sprite->y2 = 16;
            if (sprite->sTimer++ > 9)
            {
                sprite->sTimer = 0;
                sprite->sState = 0;
            }
            break;
        }
    }
}

#undef sState
#undef sTimer

#define sTimer      data[0]
#define sSameDir    data[1] // Whether or not the hiker is headed the same dir as the Cable Car
#define sDelay      data[2]

static void SpriteCB_HikerGoingUp(struct Sprite *sprite)
{
    if (sprite->sTimer == 0)
    {
        sprite->x += 2 * sprite->centerToCornerVecX;
        sprite->y += 16 + sprite->centerToCornerVecY;
    }

    if (++sprite->sTimer >= sprite->sDelay)
    {
        switch (sprite->sSameDir)
        {
        case FALSE:
            sprite->x++;
            if ((sprite->sTimer % 4) == 0)
                sprite->y++;
            break;
        case TRUE:
            // Hiker moves slower if travelling with the Cable Car
            if ((sprite->sTimer % 2) != 0)
            {
                sprite->x++;
                if ((sprite->x % 4) == 0)
                    sprite->y++;
            }
            break;
        }

        if (sprite->y > DISPLAY_HEIGHT)
            DestroySprite(sprite);
    }
}

static void SpriteCB_HikerGoingDown(struct Sprite *sprite)
{
    if (sprite->sTimer == 0)
        sprite->y += 16 + sprite->centerToCornerVecY;

    if (++sprite->sTimer >= sprite->sDelay)
    {
        switch (sprite->sSameDir)
        {
        case FALSE:
            sprite->x--;
            if ((sprite->sTimer % 4) == 0)
                sprite->y--;
            break;
        case TRUE:
            // Hiker moves slower if travelling with the Cable Car
            if ((sprite->sTimer % 2) != 0)
            {
                sprite->x--;
                if ((sprite->x % 4) == 0)
                    sprite->y--;
            }
            break;
        }

        if (sprite->y < 80)
            DestroySprite(sprite);
    }
}

#undef sTimer

static void SetBgRegs(bool8 active)
{
    switch (active)
    {
    case FALSE:
    default:
        SetGpuReg(REG_OFFSET_WININ, 0);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN1H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        SetGpuReg(REG_OFFSET_WIN1V, 0);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BG3CNT, 0);
        SetGpuReg(REG_OFFSET_BG2CNT, 0);
        SetGpuReg(REG_OFFSET_BG1CNT, 0);
        SetGpuReg(REG_OFFSET_BG0CNT, 0);
        SetGpuReg(REG_OFFSET_BG3HOFS, 0);
        SetGpuReg(REG_OFFSET_BG3VOFS, 0);
        SetGpuReg(REG_OFFSET_BG2HOFS, 0);
        SetGpuReg(REG_OFFSET_BG2VOFS, 0);
        SetGpuReg(REG_OFFSET_BG1HOFS, 0);
        SetGpuReg(REG_OFFSET_BG1VOFS, 0);
        SetGpuReg(REG_OFFSET_BG0HOFS, 0);
        SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        break;
    case TRUE:
        SetGpuReg(REG_OFFSET_WININ, 0);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_WIN0H, 0);
        SetGpuReg(REG_OFFSET_WIN1H, 0);
        SetGpuReg(REG_OFFSET_WIN0V, 0);
        SetGpuReg(REG_OFFSET_WIN1V, 0);
        if (!GOING_DOWN)
        {
            GetCableCar()->bg3HorizontalOffset = 176;
            GetCableCar()->bg3VerticalOffset = 16;
            GetCableCar()->bg1HorizontalOffset = 0;
            GetCableCar()->bg1VerticalOffset = 80;
            GetCableCar()->bg0VerticalOffset = 0;
            GetCableCar()->bg0VerticalOffset = 0;
        }
        else
        {
            GetCableCar()->bg3HorizontalOffset = 96;
            GetCableCar()->bg3VerticalOffset = 232;
            GetCableCar()->bg1HorizontalOffset = 0;
            GetCableCar()->bg1VerticalOffset = 4;
            GetCableCar()->bg0VerticalOffset = 0;
            GetCableCar()->bg0VerticalOffset = 0;
        }

        SetGpuReg(REG_OFFSET_BG3HOFS, GetCableCar()->bg3HorizontalOffset);
        SetGpuReg(REG_OFFSET_BG3VOFS, GetCableCar()->bg3VerticalOffset);
        SetGpuReg(REG_OFFSET_BG2HOFS, 0);
        SetGpuReg(REG_OFFSET_BG2VOFS, 0);
        SetGpuReg(REG_OFFSET_BG1HOFS, GetCableCar()->bg1HorizontalOffset);
        SetGpuReg(REG_OFFSET_BG1VOFS, GetCableCar()->bg1VerticalOffset);
        SetGpuReg(REG_OFFSET_BG0HOFS, GetCableCar()->bg0HorizontalOffset);
        SetGpuReg(REG_OFFSET_BG0VOFS, GetCableCar()->bg0VerticalOffset);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
        CopyBgTilemapBufferToVram(1);
        CopyBgTilemapBufferToVram(2);
        ShowBg(0);
        ShowBg(1);
        ShowBg(2);
        ShowBg(3);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT2_ALL);
        break;
    }
}

static void CreateCableCarSprites(void)
{
    u8 spriteId;
    u8 i;

    u16 rval = Random();
    u8 hikerGraphicsIds[4] = {
        OBJ_EVENT_GFX_HIKER,
        OBJ_EVENT_GFX_CAMPER,
        OBJ_EVENT_GFX_PICNICKER,
        OBJ_EVENT_GFX_ZIGZAGOON_1
    };
    s16 hikerCoords[2][2] = {
        {   0,  80 }, // Going up
        { 240, 146 }  // Going down
    };
    u8 hikerMovementDelayTable[4] = { 0, 60, 120, 170};
    void (*hikerCallbacks[2])(struct Sprite *) = {
        SpriteCB_HikerGoingUp,
        SpriteCB_HikerGoingDown
    };

    switch (GOING_DOWN)
    {
        case FALSE:
        default:
            // Create player sprite
            spriteId = CreateObjectGraphicsSprite(GetPlayerAvatarGraphicsIdByStateId(PLAYER_AVATAR_GFX_NORMAL), SpriteCB_Player, 200, 73, 102);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            if (spriteId != MAX_SPRITES)
            {
                gSprites[spriteId].oam.priority = 2;
                gSprites[spriteId].x2 = 8;
                gSprites[spriteId].y2 = 16;
                gSprites[spriteId].sXPos = 200;
                gSprites[spriteId].sYPos = 73;
            }
            // Create car sprite
            spriteId = CreateSprite(&sSpriteTemplates_CableCar[0], 176, 43, 0x67);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            gSprites[spriteId].x2 = gSprites[spriteId].y2 = 32;
            gSprites[spriteId].sXPos = 176;
            gSprites[spriteId].sYPos = 43;
            // Create door sprite
            spriteId = CreateSprite(&sSpriteTemplates_CableCar[1], 200, 99, 0x65);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            gSprites[spriteId].x2 = 8;
            gSprites[spriteId].y2 = 4;
            gSprites[spriteId].sXPos = 200;
            gSprites[spriteId].sYPos = 99;
            // Init weather
            GetCableCar()->weather = WEATHER_VOLCANIC_ASH;
            GetCableCar()->weatherDelay = 350;
            CableCarSetWeather(WEATHER_SUNNY);
            break;
        case TRUE:
            CopyToBgTilemapBufferRect_ChangePalette(0, GetCableCar()->groundTilemap + 0x24, 24, 26, 12, 3, 17);
            // Create player sprite
            spriteId = CreateObjectGraphicsSprite(GetPlayerAvatarGraphicsIdByStateId(PLAYER_AVATAR_GFX_NORMAL), SpriteCB_Player, 128, 39, 102);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            if (spriteId != MAX_SPRITES)
            {
                gSprites[spriteId].oam.priority = 2;
                gSprites[spriteId].x2 = 8;
                gSprites[spriteId].y2 = 16;
                gSprites[spriteId].sXPos = 128;
                gSprites[spriteId].sYPos = 39;
            }
            // Create car sprite
            spriteId = CreateSprite(&sSpriteTemplates_CableCar[0], 104, 9, 0x67);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            gSprites[spriteId].x2 = gSprites[spriteId].y2 = 32;
            gSprites[spriteId].sXPos = 104;
            gSprites[spriteId].sYPos = 9;
            // Create door sprite
            spriteId = CreateSprite(&sSpriteTemplates_CableCar[1], 128, 65, 0x65);
            if (spriteId == MAX_SPRITES)
            {
                GetCableCar()->failed = TRUE;
                return;
            }
            gSprites[spriteId].x2 = 8;
            gSprites[spriteId].y2 = 4;
            gSprites[spriteId].sXPos = 128;
            gSprites[spriteId].sYPos = 65;
            // Init weather
            GetCableCar()->weather = WEATHER_SUNNY;
            GetCableCar()->weatherDelay = 265;
            CableCarSetWeather(WEATHER_VOLCANIC_ASH);
            break;
    }
    for (i = 0; i < 9; i++)
    {
        spriteId = CreateSprite(&sSpriteTemplate_Cable, 16 * i + 96, 8 * i - 8, 0x68);
        if (spriteId == MAX_SPRITES)
        {
            GetCableCar()->failed = TRUE;
            return;
        }
        gSprites[spriteId].x2 = 8;
        gSprites[spriteId].y2 = 8;
    }

    // 1/64 chance for an NPC to appear hiking on the ground below the Cable Car
    if ((rval % 64) == 0)
    {
        // BUGFIX: The - 1 in the below ARRAY_COUNT means the Zigzagoon is never used
#ifdef BUGFIX
        spriteId = CreateObjectGraphicsSprite(hikerGraphicsIds[rval % ARRAY_COUNT(hikerGraphicsIds)], hikerCallbacks[GOING_DOWN], hikerCoords[GOING_DOWN][0], hikerCoords[GOING_DOWN][1], 106);
        if (spriteId == MAX_SPRITES)
        {
            GetCableCar()->failed = TRUE;
            return;
        }
#else
        spriteId = CreateObjectGraphicsSprite(hikerGraphicsIds[rval % (ARRAY_COUNT(hikerGraphicsIds) - 1)], hikerCallbacks[GOING_DOWN], hikerCoords[GOING_DOWN][0], hikerCoords[GOING_DOWN][1], 106);
        if (spriteId == MAX_SPRITES)
        {
            GetCableCar()->failed = TRUE;
            return;
        }
#endif
        if (spriteId != MAX_SPRITES)
        {
            gSprites[spriteId].oam.priority = 2;
            gSprites[spriteId].x2 = -gSprites[spriteId].centerToCornerVecX;
            gSprites[spriteId].y2 = -gSprites[spriteId].centerToCornerVecY;

            // Randomly choose which direction the NPC is going
            if (!GOING_DOWN)
            {
                if (rval % 2)
                {
                    StartSpriteAnim(&gSprites[spriteId], ANIM_STD_GO_WEST);
                    gSprites[spriteId].sSameDir = TRUE;
                    gSprites[spriteId].y += 2;
                }
                else
                {
                    StartSpriteAnim(&gSprites[spriteId], ANIM_STD_GO_EAST);
                    gSprites[spriteId].sSameDir = FALSE;
                }
            }
            else
            {
                if (rval % 2)
                {
                    StartSpriteAnim(&gSprites[spriteId], ANIM_STD_GO_EAST);
                    gSprites[spriteId].sSameDir = TRUE;
                    gSprites[spriteId].y += 2;
                }
                else
                {
                    StartSpriteAnim(&gSprites[spriteId], ANIM_STD_GO_WEST);
                    gSprites[spriteId].sSameDir = FALSE;
                }
            }
            gSprites[spriteId].sDelay = hikerMovementDelayTable[rval % ARRAY_COUNT(hikerMovementDelayTable)];
        }
    }
}

static void BufferNextGroundSegment(void)
{
    u8 i, j, k;
    u8 offset;

    for (i = 0, k = 0, offset = 0x24 * (GetCableCar()->groundTilemapOffset + 2); i < 3; i++)
    {
        for (j = 0; j < ARRAY_COUNT(GetCableCar()->groundTileBuffer[0]); j++)
        {
            GetCableCar()->groundTileBuffer[i][j] = GetCableCar()->groundTilemap[offset++];
            GetCableCar()->groundTileBuffer[i + 3][j] = GetCableCar()->groundTilemap[k];
            GetCableCar()->groundTileBuffer[i + 6][j] = (GetCableCar()->groundTilemap + 0x24)[k];
            k++;
        }
    }

    GetCableCar()->groundTilemapOffset = (GetCableCar()->groundTilemapOffset + 1) % 3;
}

static void AnimateGroundGoingUp(void)
{
    GetCableCar()->groundTimer = (GetCableCar()->groundTimer + 1) % 96;
    GetCableCar()->bg0HorizontalOffset = GetCableCar()->groundXBase - GetCableCar()->groundXOffset;
    GetCableCar()->bg0VerticalOffset = GetCableCar()->groundYBase - GetCableCar()->groundYOffset;
    GetCableCar()->groundXOffset++;
    if ((GetCableCar()->groundXOffset % 4) == 0)
        GetCableCar()->groundYOffset++;

    if (GetCableCar()->groundXOffset > 16)
        DrawNextGroundSegmentGoingUp();
}

static void AnimateGroundGoingDown(void)
{
    GetCableCar()->groundTimer = (GetCableCar()->groundTimer + 1) % 96;
    GetCableCar()->bg0HorizontalOffset = GetCableCar()->groundXBase + GetCableCar()->groundXOffset;
    GetCableCar()->bg0VerticalOffset = GetCableCar()->groundYBase + GetCableCar()->groundYOffset;
    GetCableCar()->groundXOffset++;
    if ((GetCableCar()->groundXOffset % 4) == 0)
        GetCableCar()->groundYOffset++;

    if (GetCableCar()->groundXOffset > 16)
        DrawNextGroundSegmentGoingDown();
}

static void DrawNextGroundSegmentGoingUp(void)
{
    u8 i = 0;

    GetCableCar()->groundXOffset = GetCableCar()->groundYOffset = 0;
    GetCableCar()->groundXBase = GetCableCar()->bg0HorizontalOffset;
    GetCableCar()->groundYBase = GetCableCar()->bg0VerticalOffset;
    GetCableCar()->groundSegmentXStart = (GetCableCar()->groundSegmentXStart + 30) % 32;
    GetCableCar()->groundTileIdx -= 2;
    GetCableCar()->groundSegmentYUp = (GetCableCar()->groundSegmentYStart + 23) % 32;

    // Draw next segment
    for (i = 0; i < ARRAY_COUNT(GetCableCar()->groundTileBuffer); i++)
    {
        GetCableCar()->groundXUp = GetCableCar()->groundSegmentXStart;
        GetCableCar()->groundYUp = (GetCableCar()->groundSegmentYUp + i) % 32;
        FillBgTilemapBufferRect(0, GetCableCar()->groundTileBuffer[i][GetCableCar()->groundTileIdx], GetCableCar()->groundXUp, GetCableCar()->groundYUp, 1, 1, 17);
        GetCableCar()->groundXUp = (GetCableCar()->groundXUp + 1) % 32;
        FillBgTilemapBufferRect(0, GetCableCar()->groundTileBuffer[i][GetCableCar()->groundTileIdx + 1], GetCableCar()->groundXUp, GetCableCar()->groundYUp, 1, 1, 17);
    }

    // Erase old segment
    GetCableCar()->groundXUp = (GetCableCar()->groundSegmentXStart + 30) % 32;
    FillBgTilemapBufferRect(0, 0, GetCableCar()->groundXUp, 0, 2, 32, 17);
    if (GetCableCar()->groundTileIdx == 0)
    {
        GetCableCar()->groundSegmentYStart = (GetCableCar()->groundSegmentYStart + 29) % 32;
        GetCableCar()->groundTileIdx = 12;
        BufferNextGroundSegment();
        GetCableCar()->groundXUp = (GetCableCar()->groundSegmentYStart + 1) % 32;
        FillBgTilemapBufferRect(0, 0, 0, GetCableCar()->groundXUp, 32, 9, 17);
    }
}

static void DrawNextGroundSegmentGoingDown(void)
{
    u8 i = 0;

    GetCableCar()->groundXOffset = GetCableCar()->groundYOffset = 0;
    GetCableCar()->groundXBase = GetCableCar()->bg0HorizontalOffset;
    GetCableCar()->groundYBase = GetCableCar()->bg0VerticalOffset;
    GetCableCar()->groundSegmentXStart = (GetCableCar()->groundSegmentXStart + 2) % 32;
    GetCableCar()->groundTileIdx += 2;
    GetCableCar()->groundSegmentYDown = GetCableCar()->groundSegmentYStart;

    // Draw next segment
    for (i = 0; i < ARRAY_COUNT(GetCableCar()->groundTileBuffer); i++)
    {
        GetCableCar()->groundXDown = GetCableCar()->groundSegmentXStart;
        GetCableCar()->groundYDown = (GetCableCar()->groundSegmentYDown + i) % 32;
        FillBgTilemapBufferRect(0, GetCableCar()->groundTileBuffer[i][GetCableCar()->groundTileIdx], GetCableCar()->groundXDown, GetCableCar()->groundYDown, 1, 1, 17);
        GetCableCar()->groundXDown = (GetCableCar()->groundXDown + 1) % 32;
        FillBgTilemapBufferRect(0, GetCableCar()->groundTileBuffer[i][GetCableCar()->groundTileIdx + 1], GetCableCar()->groundXDown, GetCableCar()->groundYDown, 1, 1, 17);
    }

    // Erase old segment
    GetCableCar()->groundYDown = (GetCableCar()->groundSegmentYStart + 23) % 32;
    FillBgTilemapBufferRect(0, 0, GetCableCar()->groundSegmentXStart, GetCableCar()->groundYDown, 2, 9, 17);
    if (GetCableCar()->groundTileIdx == 10)
    {
        GetCableCar()->groundSegmentYStart = (GetCableCar()->groundSegmentYStart + 3) % 32;
        GetCableCar()->groundTileIdx = -2;
        BufferNextGroundSegment();
    }
}

static void InitGroundTilemapData(bool8 goingDown)
{
    switch (goingDown)
    {
        case FALSE:
        default:
            GetCableCar()->groundTilemapOffset = 2;
            GetCableCar()->groundSegmentXStart = 0;
            GetCableCar()->groundSegmentYStart = 20;
            GetCableCar()->groundTileIdx = 12;
            BufferNextGroundSegment();
            DrawNextGroundSegmentGoingUp();
            break;
        case TRUE:
            GetCableCar()->groundTilemapOffset = 2;
            GetCableCar()->groundSegmentXStart = 28;
            GetCableCar()->groundSegmentYStart = 20;
            GetCableCar()->groundTileIdx = 4;
            BufferNextGroundSegment();
            DrawNextGroundSegmentGoingDown();
            break;
    }

    GetCableCar()->groundTimer = 0;
}


static struct CableCar *GetCableCar(void)
{
    u8 taskId = FindTaskIdByFunc(Task_CableCar);
    if (taskId == TASK_NONE)
        return NULL;
    return (struct CableCar *)GetWordTaskArg(taskId, 14);
}

static void CableCarSetWeather(u8 weather)
{
    SetCurrentAndNextWeather(weather);
    gWeatherPtr->readyForInit = TRUE;
}

static void TuckCableCarFollowers(void)
{
    struct ObjectEvent *player = &gObjectEvents[gPlayerAvatar.objectEventId];
    struct ObjectEvent *followers[2];
    u8 i;
    followers[0] = GetFollowerPikachuObject();
    followers[1] = GetMistyCompanionObject();
    for (i = 0; i < ARRAY_COUNT(followers); i++)
    {
        if (followers[i] != NULL && followers[i]->spriteId < MAX_SPRITES)
        {
            ObjectEventClearHeldMovementIfActive(followers[i]);
            MoveObjectEventToMapCoords(followers[i], player->currentCoords.x, player->currentCoords.y);
            followers[i]->invisible = TRUE;
        }
    }
}

static const u8 sCableCarExit[] = {
    MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_WALK_NORMAL_DOWN,
    MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_DELAY_16, MOVEMENT_ACTION_STEP_END
};
static const u8 sCableCarFollowFromLeft[] = {
    MOVEMENT_ACTION_DELAY_16, MOVEMENT_ACTION_WALK_NORMAL_RIGHT,
    MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_STEP_END
};
static const u8 sCableCarFollowFromRight[] = {
    MOVEMENT_ACTION_DELAY_16, MOVEMENT_ACTION_WALK_NORMAL_LEFT,
    MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_WALK_NORMAL_DOWN, MOVEMENT_ACTION_STEP_END
};

static void CableCarFieldArrival(void)
{
    u8 group = gSaveBlock1Ptr->location.mapGroup;
    u8 map = gSaveBlock1Ptr->location.mapNum;
    bool8 upper = map == MAP_NUM(MAP_MT_CHIMNEY_CABLE_CAR_STATION);
    gFieldCallback = NULL;
    Overworld_PlaySpecialMapMusic();
    LockPlayerFieldControls();
    FreezeObjectEvents();
    TryMoveObjectEventToMapCoords(1, map, group, upper ? 5 : 7, 4);
    TuckCableCarFollowers();
    WarpFadeInScreen();
    if (GetTaskCount() < NUM_TASKS)
        CreateTask(Task_CableCarArrival, 10);
    else
    {
        TryMoveObjectEventToMapCoords(LOCALID_PLAYER, map, group, 6, 7);
        TryMoveObjectEventToMapCoords(1, map, group, 6, 6);
        UnfreezeObjectEvents();
        HelpSystem_Enable();
        UnlockPlayerFieldControls();
    }
}

static void Task_CableCarArrival(u8 taskId)
{
    s16 *data = gTasks[taskId].data;
    u8 group = gSaveBlock1Ptr->location.mapGroup;
    u8 map = gSaveBlock1Ptr->location.mapNum;
    bool8 failed = FALSE;
    TuckCableCarFollowers();
    if (++data[1] >= 600)
        failed = TRUE;
    else if (data[0] == 0)
    {
        if (!FieldFadeTransitionBackgroundEffectIsFinished())
            return;
        if (GetTaskCount() >= NUM_TASKS)
            failed = TRUE;
        else
        {
            failed = ScriptMovement_StartObjectMovementScript(LOCALID_PLAYER, map, group, sCableCarExit);
            failed |= ScriptMovement_StartObjectMovementScript(1, map, group,
                map == MAP_NUM(MAP_MT_CHIMNEY_CABLE_CAR_STATION) ? sCableCarFollowFromLeft : sCableCarFollowFromRight);
        }
        data[0] = 1;
        if (!failed)
            return;
    }
    else if (!ScriptMovement_IsObjectMovementFinished(LOCALID_PLAYER, map, group)
          || !ScriptMovement_IsObjectMovementFinished(1, map, group))
        return;
    ScriptMovement_UnfreezeObjectEvents();
    if (failed)
    {
        u8 attendant;
        // Allocation/movement failure returns to the regular counter position.
        ObjectEventClearHeldMovementIfActive(&gObjectEvents[gPlayerAvatar.objectEventId]);
        if (!TryGetObjectEventIdByLocalIdAndMap(1, map, group, &attendant))
            ObjectEventClearHeldMovementIfActive(&gObjectEvents[attendant]);
        TryMoveObjectEventToMapCoords(LOCALID_PLAYER, map, group, 6, 7);
        TryMoveObjectEventToMapCoords(1, map, group, 6, 6);
    }
    TuckCableCarFollowers();
    UnfreezeObjectEvents();
    HelpSystem_Enable();
    UnlockPlayerFieldControls();
    DestroyTask(taskId);
}

