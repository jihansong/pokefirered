#include "global.h"
#include "gflib.h"
#include "scanline_effect.h"
#include "task.h"
#include "help_system.h"
#include "overworld.h"
#include "event_data.h"
#include "field_fadetransition.h"
#include "field_weather.h"
#include "trig.h"
#include "constants/songs.h"
#include "constants/maps.h"
#include "constants/airplane.h"

// The airplane flight between regions (VERMILION AIRPORT, SLATEPORT HARBOR):
// the plane takes off from a runway, cruises over parallax clouds and lands.
// BG1 is the runway, BG2 the near clouds, BG3 the sky; the plane is an affine
// sprite so it can pitch up on take-off and down on landing.

#define TAG_PLANE 0x7A00

enum {
    PHASE_TAKEOFF,
    PHASE_CRUISE,
    PHASE_LANDING,
    PHASE_EXIT,
};

#define TAKEOFF_FRAMES 170
#define CRUISE_FRAMES  200
#define LANDING_FRAMES 190

#define GROUND_Y_SHOWN 90   // BG1 vertical offset with the runway at the bottom of the screen
#define GROUND_Y_HIDDEN -80 // ... and with it dropped out of view
#define RUNWAY_SPRITE_Y 126

static EWRAM_DATA void *sTilemapBuffers[3] = {NULL};

static const u32 sSkyTiles[] = INCBIN_U32("graphics/airplane/sky.4bpp");
static const u16 sSkyPal[] = INCBIN_U16("graphics/airplane/sky.gbapal");
static const u16 sSkyTilemap[] = INCBIN_U16("graphics/airplane/sky_tilemap.bin");
static const u32 sCloudTiles[] = INCBIN_U32("graphics/airplane/clouds.4bpp");
static const u16 sCloudPal[] = INCBIN_U16("graphics/airplane/clouds.gbapal");
static const u16 sCloudTilemap[] = INCBIN_U16("graphics/airplane/clouds_tilemap.bin");
static const u32 sGroundTiles[] = INCBIN_U32("graphics/airplane/ground.4bpp");
static const u16 sGroundPal[] = INCBIN_U16("graphics/airplane/ground.gbapal");
static const u16 sGroundTilemap[] = INCBIN_U16("graphics/airplane/ground_tilemap.bin");
static const u32 sPlaneTiles[] = INCBIN_U32("graphics/airplane/plane.4bpp");
static const u16 sPlanePal[] = INCBIN_U16("graphics/airplane/plane.gbapal");

static const struct BgTemplate sBgTemplates[] = {
    {.bg = 1, .charBaseIndex = 0, .mapBaseIndex = 26, .screenSize = 2, .paletteMode = 0, .priority = 1, .baseTile = 0},
    {.bg = 2, .charBaseIndex = 1, .mapBaseIndex = 29, .screenSize = 0, .paletteMode = 0, .priority = 2, .baseTile = 0},
    {.bg = 3, .charBaseIndex = 2, .mapBaseIndex = 30, .screenSize = 0, .paletteMode = 0, .priority = 3, .baseTile = 0},
};

// Map, x, y where the player arrives
static const s8 sDestinations[AIRPLANE_DEST_COUNT][4] = {
    [AIRPLANE_DEST_KANTO] = {MAP(MAP_KANTO_AIRPORT), 12, 7},
    [AIRPLANE_DEST_HOENN] = {MAP(MAP_SLATEPORT_CITY_HARBOR), 12, 13},
};

static const struct SpriteSheet sPlaneSheet = {sPlaneTiles, sizeof(sPlaneTiles), TAG_PLANE};
static const struct SpritePalette sPlanePalette = {sPlanePal, TAG_PLANE};

static const struct OamData sPlaneOam = {
    .affineMode = ST_OAM_AFFINE_DOUBLE,
    .shape = SPRITE_SHAPE(64x32),
    .size = SPRITE_SIZE(64x32),
    .priority = 0,
};

static const union AnimCmd sPlaneAnim[] = {
    ANIMCMD_FRAME(0, 1),
    ANIMCMD_END,
};

static const union AnimCmd *const sPlaneAnims[] = {sPlaneAnim};

static const struct SpriteTemplate sPlaneTemplate = {
    .tileTag = TAG_PLANE,
    .paletteTag = TAG_PLANE,
    .oam = &sPlaneOam,
    .anims = sPlaneAnims,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

#define tPhase      data[0]
#define tTimer      data[1]
#define tSpeed      data[2]  // runway scroll, 1/16 px per frame
#define tPlaneX     data[3]  // 1/16 px
#define tPlaneY     data[4]  // 1/16 px
#define tPitch      data[5]  // rotation, 1/256 of a turn (negative: nose up)
#define tGroundY    data[6]
#define tSprite     data[7]
#define tSubX       data[8]

static void CB2_SetUpAirplaneScene(void);
static void Task_AirplaneFlight(u8 taskId);

void DoAirplaneFlightScene(void)
{
    SetVBlankCallback(NULL);
    HelpSystem_Disable();
    SetMainCallback2(CB2_SetUpAirplaneScene);
}

static void VBlankCB_Airplane(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void MainCB2_Airplane(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void ResetGpu(void)
{
    DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
    DmaClear32(3, (void *)OAM, OAM_SIZE);
    DmaClear16(3, (void *)PLTT, PLTT_SIZE);
    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetGpuReg(REG_OFFSET_BLDALPHA, 0);
    SetGpuReg(REG_OFFSET_BLDY, 0);
}

static void CB2_SetUpAirplaneScene(void)
{
    u8 i, taskId;

    switch (gMain.state)
    {
    case 0:
        ResetGpu();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        ResetPaletteFade();
        FreeAllSpritePalettes();
        gMain.state++;
        break;
    case 1:
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sBgTemplates, NELEMS(sBgTemplates));
        for (i = 0; i < 3; i++)
        {
            // BG1 is 256x512 so the runway can drop away without wrapping back in at the top
            sTilemapBuffers[i] = AllocZeroed(i == 0 ? BG_SCREEN_SIZE * 2 : BG_SCREEN_SIZE);
            SetBgTilemapBuffer(i + 1, sTilemapBuffers[i]);
        }
        for (i = 0; i < 4; i++)
        {
            ChangeBgX(i, 0, BG_COORD_SET);
            ChangeBgY(i, 0, BG_COORD_SET);
        }
        gMain.state++;
        break;
    case 2:
        LoadBgTiles(1, sGroundTiles, sizeof(sGroundTiles), 0);
        LoadBgTiles(2, sCloudTiles, sizeof(sCloudTiles), 0);
        LoadBgTiles(3, sSkyTiles, sizeof(sSkyTiles), 0);
        CopyToBgTilemapBuffer(1, sGroundTilemap, BG_SCREEN_SIZE, 0);
        CopyToBgTilemapBuffer(2, sCloudTilemap, BG_SCREEN_SIZE, 0);
        CopyToBgTilemapBuffer(3, sSkyTilemap, BG_SCREEN_SIZE, 0);
        LoadPalette(sSkyPal, BG_PLTT_ID(0), PLTT_SIZE_4BPP);
        LoadPalette(sCloudPal, BG_PLTT_ID(1), PLTT_SIZE_4BPP);
        LoadPalette(sGroundPal, BG_PLTT_ID(2), PLTT_SIZE_4BPP);
        gMain.state++;
        break;
    case 3:
        if (!IsDma3ManagerBusyWithBgCopy())
        {
            CopyBgTilemapBufferToVram(1);
            CopyBgTilemapBufferToVram(2);
            CopyBgTilemapBufferToVram(3);
            ChangeBgY(1, GROUND_Y_SHOWN << 8, BG_COORD_SET);
            ShowBg(1);
            ShowBg(2);
            ShowBg(3);
            gMain.state++;
        }
        break;
    case 4:
        LoadSpriteSheet(&sPlaneSheet);
        LoadSpritePalette(&sPlanePalette);
        BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_0 | DISPCNT_OBJ_1D_MAP | DISPCNT_BG1_ON | DISPCNT_BG2_ON | DISPCNT_BG3_ON | DISPCNT_OBJ_ON);
        SetVBlankCallback(VBlankCB_Airplane);
        taskId = CreateTask(Task_AirplaneFlight, 8);
        gTasks[taskId].tPhase = PHASE_TAKEOFF;
        gTasks[taskId].tPlaneX = 36 << 4;
        gTasks[taskId].tPlaneY = RUNWAY_SPRITE_Y << 4;
        gTasks[taskId].tGroundY = GROUND_Y_SHOWN;
        gTasks[taskId].tSprite = CreateSprite(&sPlaneTemplate, 36, RUNWAY_SPRITE_Y, 0);
        gSprites[gTasks[taskId].tSprite].oam.matrixNum = 0;
        SetOamMatrixRotationScaling(0, 0x100, 0x100, 0);
        PlaySE(SE_M_FLY);
        SetMainCallback2(MainCB2_Airplane);
        gMain.state = 0;
        break;
    }
}

static void UpdatePlane(struct Task *task)
{
    struct Sprite *sprite = &gSprites[task->tSprite];

    sprite->x = task->tPlaneX >> 4;
    sprite->y = task->tPlaneY >> 4;
    SetOamMatrixRotationScaling(0, 0x100, 0x100, (u16)(task->tPitch << 8));
    ChangeBgY(1, task->tGroundY << 8, BG_COORD_SET);
    task->tSubX += task->tSpeed;
    ChangeBgX(1, (task->tSubX >> 4) << 8, BG_COORD_SET);
    ChangeBgX(2, 0x100 + (task->tSpeed << 3), BG_COORD_ADD);   // clouds drift faster than the sky
    ChangeBgX(3, 0x40 + (task->tSpeed << 1), BG_COORD_ADD);
}

static void Task_AirplaneFlight(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    s16 t = task->tTimer++;

    switch (task->tPhase)
    {
    case PHASE_TAKEOFF:
        if (task->tSpeed < 96)
            task->tSpeed++;                        // accelerate down the runway
        if (task->tPlaneX < (104 << 4))
            task->tPlaneX += 6;
        if (t > 70)                                // rotate and climb
        {
            if (task->tPitch > -6)
                task->tPitch--;
            task->tPlaneY -= 10;
            if (task->tGroundY > GROUND_Y_HIDDEN)
                task->tGroundY -= 1;
        }
        if (t >= TAKEOFF_FRAMES)
        {
            task->tPhase = PHASE_CRUISE;
            task->tTimer = 0;
        }
        break;
    case PHASE_CRUISE:
        if (task->tPitch < 0 && (t % 4) == 0)
            task->tPitch++;
        if (task->tGroundY > GROUND_Y_HIDDEN)
            task->tGroundY -= 2;
        task->tPlaneY += Sin((t * 4) & 0xFF, 3);   // gentle bob
        if (t % 70 == 0)
            PlaySE(SE_M_GUST);
        if (t >= CRUISE_FRAMES)
        {
            task->tPhase = PHASE_LANDING;
            task->tTimer = 0;
        }
        break;
    case PHASE_LANDING:
        if (task->tGroundY < GROUND_Y_SHOWN)
            task->tGroundY += 1;                   // the runway rises into view
        if (task->tPlaneY < (RUNWAY_SPRITE_Y << 4))
        {
            task->tPlaneY += 11;
            if (task->tPitch < 3 && (t % 6) == 0)
                task->tPitch++;
        }
        else
        {
            task->tPlaneY = RUNWAY_SPRITE_Y << 4;  // touchdown
            if (task->tPitch > 0 && (t % 3) == 0)
                task->tPitch--;
            if (task->tSpeed > 0)
                task->tSpeed--;
        }
        if (task->tPlaneX < (150 << 4))
            task->tPlaneX += 4;
        if (t == LANDING_FRAMES - 40)
        {
            Overworld_FadeOutMapMusic();
            WarpFadeOutScreen();
        }
        if (t >= LANDING_FRAMES && !gPaletteFade.active)
        {
            task->tPhase = PHASE_EXIT;
        }
        break;
    case PHASE_EXIT:
    {
        const s8 *dest = sDestinations[gSpecialVar_0x8004 < AIRPLANE_DEST_COUNT ? gSpecialVar_0x8004 : 0];
        u8 i;

        SetWarpDestination(dest[0], dest[1], -1, dest[2], dest[3]);
        PlaySE(SE_EXIT);
        gFieldCallback = FieldCB_DefaultWarpExit;
        WarpIntoMap();
        SetMainCallback2(CB2_LoadMap);
        ResetInitialPlayerAvatarState();
        FreeSpriteTilesByTag(TAG_PLANE);
        FreeSpritePaletteByTag(TAG_PLANE);
        for (i = 0; i < 3; i++)
            FREE_AND_SET_NULL(sTilemapBuffers[i]);
        HelpSystem_Enable();
        DestroyTask(taskId);
        return;
    }
    }
    UpdatePlane(task);
}
