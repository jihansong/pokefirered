#include "global.h"
#include "gflib.h"
#include "m4a.h"
#include "task.h"
#include "scanline_effect.h"
#include "libgcnmultiboot.h"
#include "new_menu_helpers.h"
#include "link.h"
#include "menu.h"
#include "random.h"
#include "save.h"
#include "new_game.h"
#include "title_screen.h"
#include "decompress.h"
#include "util.h"
#include "trig.h"
#include "constants/songs.h"
#include "constants/sound.h"

#include "intro_opening.h"

/*
    The intro is grouped into the following scenes
    - Copyright screen
    - GF Logo
    - The Thunder Yellow opening (src/intro_opening.c): PIKACHU vs RAICHU in
      VERMILION GYM on the structure of FR/LG's Gengar/Nidorino fight, made of
      official in-game graphics only and cut to the bars of MUS_INTRO_FIGHT. It
      replaces the fight frame for frame: 751 frames, the song rings out to its end
      and the title screen comes at F1459 as in FR/LG.

    After this it progresses to the title screen
*/

enum {
    GFXTAG_STAR,
    GFXTAG_SPARKLES_SMALL,
    GFXTAG_SPARKLES_BIG,
    GFXTAG_GF_LOGO,
    GFXTAG_PRESENTS,
};

enum {
    PALTAG_STAR,
    PALTAG_SPARKLES,
    PALTAG_UNUSED_2,
    PALTAG_GF,
};

// Background IDs for Game Freak logo scene
enum {
    BG_GF_TEXT_LOGO = 2,
    BG_GF_BACKGROUND
};

enum {
    ANIM_SPARKLE_LOOP,
    ANIM_SPARKLE_ONCE,
};

// Window ids for sWindowTemplates (only one)
enum {
    WIN_GF_TEXT_LOGO,
    WIN_COUNT
};

#define COLOSSEUM_GAME_CODE 0x65366347 // "Gc6e" in ASCII

struct IntroSequenceData;

typedef void (*IntroCallback)(struct IntroSequenceData *);

struct IntroSequenceData
{
    IntroCallback callback;
    u8 state; // IntroCB_Opening: the number of the cut on screen (1-13)
    u8 taskId;
    u16 data[5]; // [0] and [1] are set but never read, the rest are unused
    u16 timer;
    struct Sprite *gameFreakLogoArtSprite;
    u8 gameFreakLogoGfx[0x400];
    u8 gameFreakTextGfx[0x400];
    // The "GAME FREAK" text decompresses to 0x480 bytes and runs over the end of
    // gameFreakTextGfx; keep the original's padding after it.
    u8 unused1[0x2080];
};

static EWRAM_DATA struct GcmbStruct sGcmb = {0};
static EWRAM_DATA u16 sStarSpeedX = 0;
static EWRAM_DATA u16 sStarSpeedY = 0;
static EWRAM_DATA u16 sStarSparklesXmodMask = 0;
static EWRAM_DATA u16 sStarSparklesUnusedVar = 0; // Set but never read
static EWRAM_DATA u16 sStarSparklesSpawnRate = 0;
static EWRAM_DATA u16 sStarSparklesFlickerStartTime = 0;
static EWRAM_DATA u16 sStarSparklesDestroySpriteTime = 0;
static EWRAM_DATA u16 sStarSparklesGravityShift = 0;
static EWRAM_DATA u16 sStarSparklesXspeed = 0;
static EWRAM_DATA u16 sStarSparklesYspeed = 0;
static EWRAM_DATA u16 sStarSparklesXprecision = 0;
static EWRAM_DATA u16 sStarSparklesYprecision = 0;

// General
static void CB2_SetUpIntro(void);
static void CB2_Intro(void);
static void VBlankCB_Intro(void);
static void Intro_ResetGpuRegs(void);
static void StartIntroSequence(void);
static void Task_CallIntroCallback(u8 taskId);
static void SetIntroCB(struct IntroSequenceData * ptr, IntroCallback cb);
static void IntroCB_Init(struct IntroSequenceData * ptr);
static void IntroCB_ExitToTitleScreen(struct IntroSequenceData * ptr);

// GF scene
static void IntroCB_GF_OpenWindow(struct IntroSequenceData * ptr);
static void IntroCB_GF_Star(struct IntroSequenceData * ptr);
static void IntroCB_GF_RevealName(struct IntroSequenceData * ptr);
static void IntroCB_GF_RevealLogo(struct IntroSequenceData * ptr);
static void GFScene_LoadGfxCreateStar(void);
static void GFScene_StartNameSparklesSmall(void);
static void GFScene_StartNameSparklesBig(void);
static void GFScene_Task_NameSparklesSmall(u8 taskId);
static void GFScene_Task_NameSparklesBig(u8 taskId);
static struct Sprite *GFScene_CreateLogoSprite(void);
static void GFScene_CreatePresentsSprite(void);
static void SpriteCB_Star(struct Sprite *sprite);
static void SpriteCB_SparklesSmall_Star(struct Sprite *sprite);
static void SpriteCB_SparklesSmall_Name(struct Sprite *sprite);
static void SpriteCB_SparklesBig(struct Sprite *sprite);

// The opening
static void IntroCB_Opening(struct IntroSequenceData * ptr);

extern const u32 gMultiBootProgram_PokemonColosseum_Start[];
extern const u32 gMultiBootProgram_PokemonColosseum_End[];

static const u16 sCopyright_Pal[] = INCBIN_U16("graphics/intro/copyright.gbapal");
static const u8 sCopyright_Gfx[]  = INCBIN_U8( "graphics/intro/copyright.4bpp.lz");
static const u8 sCopyright_Map[]  = INCBIN_U8( "graphics/intro/copyright.bin.lz");

// Game Freak
static const u16 sGameFreakBg_Pal[]   = INCBIN_U16("graphics/intro/game_freak/bg.gbapal");
static const u8 sGameFreakBg_Gfx[]    = INCBIN_U8( "graphics/intro/game_freak/bg.4bpp.lz");
static const u8 sGameFreakBg_Map[]    = INCBIN_U8( "graphics/intro/game_freak/bg.bin.lz");
static const u16 sGameFreakLogo_Pal[] = INCBIN_U16("graphics/intro/game_freak/logo.gbapal");
static const u8 sGameFreakText_Gfx[]  = INCBIN_U8( "graphics/intro/game_freak/game_freak.4bpp.lz");
static const u32 sGameFreakLogo_Gfx[] = INCBIN_U32("graphics/intro/game_freak/logo.4bpp.lz");
static const u16 sStar_Pal[]          = INCBIN_U16("graphics/intro/game_freak/star.gbapal");
static const u32 sStar_Gfx[]          = INCBIN_U32("graphics/intro/game_freak/star.4bpp.lz");
static const u16 sSparkles_Pal[]      = INCBIN_U16("graphics/intro/game_freak/sparkles.gbapal");
static const u32 sSparklesSmall_Gfx[] = INCBIN_U32("graphics/intro/game_freak/sparkles_small.4bpp.lz");
static const u32 sSparklesBig_Gfx[]   = INCBIN_U32("graphics/intro/game_freak/sparkles_big.4bpp.lz");
static const u32 sPresents_Gfx[]      = INCBIN_U32("graphics/intro/game_freak/presents.4bpp.lz");

static const struct BgTemplate sBgTemplates_GameFreakScene[] = {
    {
        .bg = BG_GF_BACKGROUND,
        .charBaseIndex = 3,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 3,
        .baseTile = 0x000
    }, {
        .bg = BG_GF_TEXT_LOGO,
        .charBaseIndex = 3,
        .mapBaseIndex = 30,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 2,
        .baseTile = 0x010
    }
};

static const struct WindowTemplate sWindowTemplates[WIN_COUNT + 1] = {
	[WIN_GF_TEXT_LOGO] = {
	    .bg = BG_GF_TEXT_LOGO,
	    .tilemapLeft = 6,
	    .tilemapTop = 4,
	    .width = 18,
	    .height = 9,
	    .paletteNum = 13,
	    .baseBlock = 0x000
    },
    [WIN_COUNT] = DUMMY_WIN_TEMPLATE
};

static const struct CompressedSpriteSheet sSpriteSheets_GameFreakScene[] = {
    {sStar_Gfx,          0x80,  GFXTAG_STAR},
    {sSparklesSmall_Gfx, 0x80,  GFXTAG_SPARKLES_SMALL},
    {sSparklesBig_Gfx,   0x800, GFXTAG_SPARKLES_BIG},
    {sGameFreakLogo_Gfx, 0x400, GFXTAG_GF_LOGO},
    {sPresents_Gfx,      0x100, GFXTAG_PRESENTS}
};

static const struct SpritePalette sSpritePalettes_GameFreakScene[] = {
	{sStar_Pal,          PALTAG_STAR},
	{sSparkles_Pal,      PALTAG_SPARKLES},
	{sGameFreakLogo_Pal, PALTAG_GF},
	{0}
};

static const struct Coords16 sTextSparkleCoords[] = {
	{ 72,  80},
	{136,  74},
	{168,  80},
	{120,  80},
	{104,  86},
	{ 88,  74},
	{184,  74},
	{ 56,  86},
	{152,  86}
};

static const struct OamData sOam_Star = {
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x16),
    .matrixNum = 0,
    .size = SPRITE_SIZE(16x16),
    .tileNum = 0x000,
    .priority = 2,
    .paletteNum = 0
};

static const struct OamData sOam_SparklesSmall = {
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(8x8),
    .matrixNum = 0,
    .size = SPRITE_SIZE(8x8),
    .tileNum = 0x000,
    .priority = 2,
    .paletteNum = 0
};

static const union AnimCmd sAnim_SparklesSmall_Loop[] = {
	ANIMCMD_FRAME(0, 4),
	ANIMCMD_FRAME(1, 4),
	ANIMCMD_FRAME(2, 4),
	ANIMCMD_FRAME(3, 4),
	ANIMCMD_JUMP(0)
};

static const union AnimCmd sAnim_SparklesSmall_Once[] = {
	ANIMCMD_FRAME(0, 4),
	ANIMCMD_FRAME(1, 4),
	ANIMCMD_FRAME(2, 4),
	ANIMCMD_FRAME(3, 4),
	ANIMCMD_END
};

static const union AnimCmd *const sAnims_SparklesSmall[] = {
	[ANIM_SPARKLE_LOOP] = sAnim_SparklesSmall_Loop,
	[ANIM_SPARKLE_ONCE] = sAnim_SparklesSmall_Once
};

static const struct SpriteTemplate sSpriteTemplate_Star = {
    .tileTag = GFXTAG_STAR,
    .paletteTag = PALTAG_STAR,
    .oam = &sOam_Star,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_Star
};

static const struct SpriteTemplate sSpriteTemplate_SparklesSmall = {
    .tileTag = GFXTAG_SPARKLES_SMALL,
    .paletteTag = PALTAG_SPARKLES,
    .oam = &sOam_SparklesSmall,
    .anims = sAnims_SparklesSmall,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_SparklesSmall_Star
};

static const struct OamData sOam_SparklesBig = {
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x32),
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x32),
    .tileNum = 0x000,
    .priority = 2,
    .paletteNum = 0
};

static const union AnimCmd sAnim_SparklesBig[] = {
	ANIMCMD_FRAME(0, 8),
	ANIMCMD_FRAME(16, 8),
	ANIMCMD_FRAME(32, 8),
	ANIMCMD_FRAME(48, 8),
	ANIMCMD_END
};

static const union AnimCmd *const sAnims_SparklesBig[] = {
	sAnim_SparklesBig
};

static const struct SpriteTemplate sSpriteTemplate_SparklesBig = {
    .tileTag = GFXTAG_SPARKLES_BIG,
    .paletteTag = PALTAG_SPARKLES,
    .oam = &sOam_SparklesBig,
    .anims = sAnims_SparklesBig,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_SparklesBig
};

static const struct OamData sOam_GameFreakLogo = {
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_BLEND,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x64),
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x64),
    .tileNum = 0x000,
    .priority = 3,
    .paletteNum = 0
};

static const struct SpriteTemplate sSpriteTemplate_GameFreakLogoArt = {
    .tileTag = GFXTAG_GF_LOGO,
    .paletteTag = PALTAG_GF,
    .oam = &sOam_GameFreakLogo,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy
};

static const struct OamData sOam_PresentsText = {
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_BLEND,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x8),
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x8),
    .tileNum = 0x000,
    .priority = 3,
    .paletteNum = 0
};

static const struct SpriteTemplate sSpriteTemplate_Presents = {
    .tileTag = GFXTAG_PRESENTS,
    .paletteTag = PALTAG_GF,
    .oam = &sOam_PresentsText,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy
};

static void VBlankCB_Copyright(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void CB2_WaitFadeBeforeSetUpIntro(void)
{
    if (!UpdatePaletteFade())
        SetMainCallback2(CB2_SetUpIntro);
}

static void LoadCopyrightGraphics(u16 charBase, u16 screenBase, u16 palOffset)
{
    LZ77UnCompVram(sCopyright_Gfx, (void *)BG_VRAM + charBase);
    LZ77UnCompVram(sCopyright_Map, (void *)BG_VRAM + screenBase);
    LoadPalette(sCopyright_Pal, palOffset, sizeof(sCopyright_Pal));
}

static void SerialCB_CopyrightScreen(void)
{
    GameCubeMultiBoot_HandleSerialInterrupt(&sGcmb);
}

static bool8 SetUpCopyrightScreen(void)
{
    switch (gMain.state)
    {
    case 0:
        SetVBlankCallback(NULL);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
// "Fade from white" instead is just pure black in Revision 10.
#if REVISION >= 0xA
        ((vu16*)PLTT)[0] = RGB_BLACK;
#else
        ((vu16*)PLTT)[0] = RGB_WHITE;
#endif
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BG0HOFS, 0);
        SetGpuReg(REG_OFFSET_BG0VOFS, 0);
        DmaFill16(3, 0, VRAM, VRAM_SIZE);
        DmaFill32(3, 0, OAM, OAM_SIZE);
        DmaFill16(3, 0, PLTT + sizeof(vu16), PLTT_SIZE - sizeof(vu16));
        ResetPaletteFade();
        LoadCopyrightGraphics(0 * BG_CHAR_SIZE, 7 * BG_SCREEN_SIZE, BG_PLTT_ID(0));
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
#if REVISION >= 0xA
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
#else
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_WHITEALPHA);
#endif
        SetGpuReg(REG_OFFSET_BG0CNT, BGCNT_PRIORITY(0) | BGCNT_CHARBASE(0) | BGCNT_16COLOR | BGCNT_SCREENBASE(7));
        EnableInterrupts(INTR_FLAG_VBLANK);
        SetVBlankCallback(VBlankCB_Copyright);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_1D_MAP | DISPCNT_BG0_ON);
        SetSerialCallback(SerialCB_CopyrightScreen);
        GameCubeMultiBoot_Init(&sGcmb);
        // fallthrough
    default:
        UpdatePaletteFade();
        gMain.state++;
        GameCubeMultiBoot_Main(&sGcmb);
        break;
    case 140:
        GameCubeMultiBoot_Main(&sGcmb);
        if (sGcmb.gcmb_field_2 != 1)
        {
            BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
            gMain.state++;
        }
        break;
    case 141:
        if (!UpdatePaletteFade())
        {
            gMain.state++;
            if (sGcmb.gcmb_field_2 != 0)
            {
                if (sGcmb.gcmb_field_2 == 2)
                {
                    if (*(u32 *)(EWRAM_START + 0xAC) == COLOSSEUM_GAME_CODE)
                    {
                        CpuCopy16(gMultiBootProgram_PokemonColosseum_Start, (void *)EWRAM_START, 0x28000);
                        *(u32 *)(EWRAM_START + 0xAC) = COLOSSEUM_GAME_CODE;
                    }
                    GameCubeMultiBoot_ExecuteProgram(&sGcmb);
                }
            }
            else
            {
                GameCubeMultiBoot_Quit();
                SetSerialCallback(SerialCB);
            }
            return FALSE;
        }
        break;
    case 142:
        ResetSerial();
        SetMainCallback2(CB2_WaitFadeBeforeSetUpIntro);
        break;
    }
    return TRUE;
}

void CB2_InitCopyrightScreenAfterBootup(void)
{
    if (!SetUpCopyrightScreen())
    {
        ResetMenuAndMonGlobals();
        Save_ResetSaveCounters();
        LoadGameSave(SAVE_NORMAL);
        if (gSaveFileStatus == SAVE_STATUS_EMPTY || gSaveFileStatus == SAVE_STATUS_INVALID)
            Sav2_ClearSetDefault();
        SetPokemonCryStereo(gSaveBlock2Ptr->optionsSound);
    }
}

void CB2_InitCopyrightScreenAfterTitleScreen(void)
{
    SetUpCopyrightScreen();
}

static void CB2_SetUpIntro(void)
{
    switch (gMain.state)
    {
    default:
        gMain.state = 0;
        // fallthrough
    case 0:
        SetVBlankCallback(NULL);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        InitHeap(gHeap, HEAP_SIZE);
        ResetTasks();
        ResetSpriteData();
        ResetPaletteFade();
        ResetTempTileDataBuffers();
        Intro_ResetGpuRegs();
        DmaFill16(3, 0, VRAM, VRAM_SIZE);
        DmaFill32(3, 0, OAM, OAM_SIZE);
        DmaFill16(3, 0, PLTT, PLTT_SIZE);
        FillPalette(RGB_BLACK, 0, PLTT_SIZE);
        ResetBgsAndClearDma3BusyFlags(FALSE);
        InitBgsFromTemplates(0, sBgTemplates_GameFreakScene, ARRAY_COUNT(sBgTemplates_GameFreakScene));
        break;
    case 1:
        LoadPalette(sGameFreakBg_Pal, BG_PLTT_ID(0), sizeof(sGameFreakBg_Pal));
        DecompressAndCopyTileDataToVram(BG_GF_BACKGROUND, sGameFreakBg_Gfx, 0, 0, 0);
        DecompressAndCopyTileDataToVram(BG_GF_BACKGROUND, sGameFreakBg_Map, 0, 0, 1);
        LoadPalette(sGameFreakLogo_Pal, BG_PLTT_ID(13), sizeof(sGameFreakLogo_Pal));
        break;
    case 2:
        if (!FreeTempTileDataBuffersIfPossible())
        {
            StartIntroSequence();
            BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
            SetMainCallback2(CB2_Intro);
            SetVBlankCallback(VBlankCB_Intro);
        }
        return;
    }
    gMain.state++;
}

static void CB2_Intro(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void VBlankCB_Intro(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void Intro_ResetGpuRegs(void)
{
    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetGpuReg(REG_OFFSET_BLDALPHA, 0);
    SetGpuReg(REG_OFFSET_BLDY, 0);
    SetGpuReg(REG_OFFSET_BG0HOFS, 0);
    SetGpuReg(REG_OFFSET_BG0VOFS, 0);
    SetGpuReg(REG_OFFSET_BG1HOFS, 0);
    SetGpuReg(REG_OFFSET_BG1VOFS, 0);
    SetGpuReg(REG_OFFSET_BG2HOFS, 0);
    SetGpuReg(REG_OFFSET_BG2VOFS, 0);
    SetGpuReg(REG_OFFSET_BG3HOFS, 0);
    SetGpuReg(REG_OFFSET_BG3VOFS, 0);
    SetGpuRegBits(REG_OFFSET_DISPCNT, DISPCNT_OBJ_1D_MAP | DISPCNT_OBJ_ON);
}

static void StartIntroSequence(void)
{
    struct IntroSequenceData * ptr = Alloc(sizeof(*ptr));
    SetIntroCB(ptr, IntroCB_Init);
    ptr->taskId = CreateTask(Task_CallIntroCallback, 3);
    SetWordTaskArg(ptr->taskId, 0, (uintptr_t)ptr);
}

static void SetIntroCB(struct IntroSequenceData * ptr, IntroCallback cb)
{
    ptr->callback = cb;
    ptr->state = 0;
}

static void Task_CallIntroCallback(u8 taskId)
{
    struct IntroSequenceData * ptr = (void *)GetWordTaskArg(taskId, 0);
    
    // End intro early if player presses A/Start/Select
    if (JOY_NEW(A_BUTTON | START_BUTTON | SELECT_BUTTON) && ptr->callback != IntroCB_ExitToTitleScreen)
        SetIntroCB(ptr, IntroCB_ExitToTitleScreen);

    ptr->callback(ptr);
}

static void IntroCB_Init(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        InitWindows(sWindowTemplates);
        LZ77UnCompWram(sGameFreakText_Gfx, this->gameFreakTextGfx);
        LZ77UnCompWram(sGameFreakLogo_Gfx, this->gameFreakLogoGfx);
        FillBgTilemapBufferRect(BG_GF_TEXT_LOGO, 0x000, 0, 0, 32, 32, 17);
        FillWindowPixelBuffer(WIN_GF_TEXT_LOGO, PIXEL_FILL(0));
        BlitBitmapToWindow(WIN_GF_TEXT_LOGO, this->gameFreakTextGfx, 0, 40, 144, 16);
        PutWindowTilemap(WIN_GF_TEXT_LOGO);
        CopyWindowToVram(WIN_GF_TEXT_LOGO, COPYWIN_FULL);
        this->state++;
        break;
    case 1:
        if (!IsDma3ManagerBusyWithBgCopy())
            SetIntroCB(this, IntroCB_GF_OpenWindow);
        break;
    }
}

static void IntroCB_GF_OpenWindow(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        SetGpuRegBits(REG_OFFSET_DISPCNT, DISPCNT_WIN1_ON);
        SetGpuReg(REG_OFFSET_WININ, WININ_WIN1_ALL);
        SetGpuReg(REG_OFFSET_WINOUT, 0);
        SetGpuReg(REG_OFFSET_WIN1H, DISPLAY_WIDTH);
        SetGpuReg(REG_OFFSET_WIN1V, 0);
        this->timer = 0;
        this->state++;
        break;
    case 1:
        ShowBg(BG_GF_BACKGROUND);
        BlendPalettes(PALETTES_ALL, 0, RGB_BLACK);
        this->state++;
        break;
    case 2:
        // Extend window height in both directions from midpoint until it reaches a narrow "theatric" view
        this->timer += 8;
        if (this->timer >= 48)
            this->timer = 48;
        SetGpuReg(REG_OFFSET_WIN1V, WIN_RANGE(DISPLAY_HEIGHT / 2 - this->timer, DISPLAY_HEIGHT / 2 + this->timer));
        if (this->timer == 48)
            SetIntroCB(this, IntroCB_GF_Star);
        break;
    }
}

static void IntroCB_GF_Star(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        PlaySE(MUS_GAME_FREAK);
        GFScene_LoadGfxCreateStar();
        this->timer = 0;
        this->state++;
        break;
    case 1:
        if (++this->timer == 30)
        {
            GFScene_StartNameSparklesSmall();
            this->timer = 0;
            this->state++;
        }
        break;
    case 2:
        this->timer++;
        if (this->timer == 90)
            SetIntroCB(this, IntroCB_GF_RevealName);
        break;
    }
}

static void IntroCB_GF_RevealName(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        GFScene_StartNameSparklesBig();
        this->timer = 0;
        this->state++;
        break;
    case 1:
        if (++this->timer >= 40)
            this->state++;
        break;
    case 2:
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG2 | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_ALL);
        StartBlendTask(0, 16, 16, 0, 48, 0);
        this->state++;
        break;
    case 3:
        ShowBg(BG_GF_TEXT_LOGO);
        this->state++;
        break;
    case 4:
        if (!IsBlendTaskActive())
        {
            SetGpuReg(REG_OFFSET_BLDCNT, 0);
            this->timer = 0;
            this->state++;
        }
        break;
    case 5:
        if (++this->timer > 50)
            SetIntroCB(this, IntroCB_GF_RevealLogo);
        break;
    }
}

static void IntroCB_GF_RevealLogo(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_OBJ | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_ALL);
        StartBlendTask(0, 16, 16, 0, 16, 0);
        this->data[0] = 0; // Never read
        this->data[1] = 16; // Never read
        this->timer = 0;
        this->state++;
        break;
    case 1:
        this->gameFreakLogoArtSprite = GFScene_CreateLogoSprite();
        this->state++;
        break;
    case 2:
        if (!IsBlendTaskActive())
        {
            BlitBitmapToWindow(WIN_GF_TEXT_LOGO, this->gameFreakLogoGfx, 0x38, 0x06, 0x20, 0x40);
            BlitBitmapToWindow(WIN_GF_TEXT_LOGO, this->gameFreakTextGfx, 0x00, 0x28, 0x90, 0x10);
            CopyWindowToVram(WIN_GF_TEXT_LOGO, COPYWIN_GFX);
            this->state++;
        }
        break;
    case 3:
        if (!IsDma3ManagerBusyWithBgCopy())
        {
            DestroySprite(this->gameFreakLogoArtSprite);
        #if REVISION >= 1
            GFScene_CreatePresentsSprite();
        #endif
            this->timer = 0;
            this->state++;
        }
        break;
    case 4:
        if (++this->timer > 90)
        {
            SetGpuRegBits(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG2);
            StartBlendTask(16, 0, 0, 16, 20, 0);
            this->state++;
        }
        break;
    case 5:
        if (!IsBlendTaskActive())
        {
            HideBg(BG_GF_TEXT_LOGO);
            this->state++;
        }
        break;
    case 6:
        ResetSpriteData();
        FreeAllSpritePalettes();
        this->timer = 0;
        this->state++;
        break;
    case 7:
        if (++this->timer > 20)
        {
            SetGpuReg(REG_OFFSET_BLDCNT, 0);
            SetIntroCB(this, IntroCB_Opening);
        }
        break;
    }
}

// The opening runs itself (src/intro_opening.c); this only starts it, keeps the scene
// number in state for tools/qa/intro_timeline.py and moves on to the title screen
// when it ends (F1457 after power on, when MUS_INTRO_FIGHT has rung out, as FR/LG).
static void IntroCB_Opening(struct IntroSequenceData * this)
{
    u8 scene;

    if (this->state == 0)
        Opening_Init();
    scene = Opening_Run();
    if (scene == 0)
        SetIntroCB(this, IntroCB_ExitToTitleScreen);
    else
        this->state = scene;
}

static void IntroCB_ExitToTitleScreen(struct IntroSequenceData * this)
{
    switch (this->state)
    {
    case 0:
        Opening_Free();
        FillPalette(RGB_BLACK, 0, PLTT_SIZE);
        this->state++;
        break;
    case 1:
        if (!FreeTempTileDataBuffersIfPossible())
        {
            DestroyTask(this->taskId);
            Free(this);
            DisableInterrupts(INTR_FLAG_HBLANK);
            SetHBlankCallback(NULL);
            SetMainCallback2(CB2_InitTitleScreen);
        }
        break;
    }
}

// Sprite data for SpriteCB_Star
#define sStar_BaseX          data[0]
#define sStar_BaseY          data[1]
#define sStar_SpeedX         data[2]
#define sStar_SpeedY         data[3]
#define sStar_SinIdx         data[4]
#define sStar_SparkleTimer   data[5]
#define sStar_SparkleRngSeed data[6]

static void GFScene_LoadGfxCreateStar(void)
{
    int i;
    u8 spriteId;
    static EWRAM_DATA u32 sStarSparklesRngSeed = 0;

    for (i = 0; i < ARRAY_COUNT(sSpriteSheets_GameFreakScene); i++)
        LoadCompressedSpriteSheet(&sSpriteSheets_GameFreakScene[i]);
    LoadSpritePalettes(sSpritePalettes_GameFreakScene);
    sStarSpeedX = 96;
    sStarSpeedY = 16;
    sStarSparklesXmodMask = 0x07;
    sStarSparklesUnusedVar = 5;
    sStarSparklesSpawnRate = 8;
    sStarSparklesFlickerStartTime = 90;
    sStarSparklesDestroySpriteTime = 120;
    sStarSparklesXspeed = 1;
    sStarSparklesYspeed = 1;
    sStarSparklesXprecision = 5;
    sStarSparklesYprecision = 5;
    if (sStarSparklesRngSeed == 0)
        sStarSparklesRngSeed = 354128453;
    spriteId = CreateSprite(&sSpriteTemplate_Star, 248, 55, 0);
    if (spriteId != MAX_SPRITES)
    {
        gSprites[spriteId].sStar_BaseX = 248 << 4;
        gSprites[spriteId].sStar_BaseY = 55 << 4;
        gSprites[spriteId].sStar_SpeedX = sStarSpeedX;
        gSprites[spriteId].sStar_SpeedY = sStarSpeedY;
        StoreWordInTwoHalfwords((u16 *)&gSprites[spriteId].sStar_SparkleRngSeed, sStarSparklesRngSeed);
    }
}

// Sprite data for SpriteCB_SparklesSmall_Star
#define sSmSparkleStar_BaseX     data[0]
#define sSmSparkleStar_BaseY     data[1]
#define sSmSparkleStar_SpeedX    data[2]
#define sSmSparkleStar_SpeedY    data[3]
#define sSmSparkleStar_FallSpeed data[4]
#define sSmSparkleStar_FallDist  data[5]
#define sSmSparkleStar_Timer     data[7]

static void GFScene_CreateStarSparkle(s16 x, s16 y, u16 random)
{
    static EWRAM_DATA s16 sYmod = 0;

    u8 spriteId;
    s16 xMod = (random & sStarSparklesXmodMask) + 2;
    s16 yMod = sYmod;
    if (++sYmod > 3)
        sYmod = -3;
    x += xMod;
    y += yMod;
    if (x > 0 && x < DISPLAY_WIDTH)
    {
        spriteId = CreateSprite(&sSpriteTemplate_SparklesSmall, x, y, 1);
        if (spriteId != MAX_SPRITES)
        {
            gSprites[spriteId].sSmSparkleStar_BaseX = x << sStarSparklesXprecision;
            gSprites[spriteId].sSmSparkleStar_BaseY = y << sStarSparklesYprecision;
            gSprites[spriteId].sSmSparkleStar_SpeedX = sStarSparklesXspeed * xMod;
            gSprites[spriteId].sSmSparkleStar_SpeedY = sStarSparklesYspeed * yMod;
        }
    }
}

#define tSparkleIdx data[0]
#define tNumLoops   data[1]
#define tTimer      data[2]

static void GFScene_StartNameSparklesSmall(void)
{
    CreateTask(GFScene_Task_NameSparklesSmall, 1);
}

// Sprite data for SpriteCB_SparklesSmall_Name
#define sSmSparkleName_State        data[0]
#define sSmSparkleName_BaseY        data[1]
#define sSmSparkleName_AnimTimer    data[2]
#define sSmSparkleName_NumLoops     data[3]
#define sSmSparkleName_DestroyTimer data[4]

static void GFScene_Task_NameSparklesSmall(u8 taskId)
{
    s16 * data = gTasks[taskId].data;
    u8 i;
    u8 spriteId;

    tTimer++;
    data[3]++; // Unused
    if (tTimer > 6)
    {
        tTimer = 0;
        i = tSparkleIdx;
        spriteId = CreateSprite(&sSpriteTemplate_SparklesSmall, sTextSparkleCoords[i].x, sTextSparkleCoords[i].y, 2);
        StartSpriteAnim(&gSprites[spriteId], ANIM_SPARKLE_ONCE);
        gSprites[spriteId].callback = SpriteCB_SparklesSmall_Name;
        gSprites[spriteId].sSmSparkleName_BaseY = sTextSparkleCoords[i].y << 4;
        gSprites[spriteId].sSmSparkleName_AnimTimer = 120;
        gSprites[spriteId].sSmSparkleName_NumLoops = tNumLoops;
        if (gSprites[spriteId].sSmSparkleName_NumLoops < 0)
            gSprites[spriteId].sSmSparkleName_NumLoops = 1;
        if (++tSparkleIdx >= ARRAY_COUNT(sTextSparkleCoords))
        {
            if (++tNumLoops > 1)
                DestroyTask(taskId);
            else
                tSparkleIdx = 0;
        }
    }
}

#undef tSparkleIdx
#undef tNumLoops
#undef tTimer

#define tTimer       data[0]
#define tSparkleIdx  data[1]
#define tNumSparkles data[2]

static void GFScene_StartNameSparklesBig(void)
{
    CreateTask(GFScene_Task_NameSparklesBig, 2);
}

static void GFScene_Task_NameSparklesBig(u8 taskId)
{
    s16 * data = gTasks[taskId].data;
    u8 i;

    if (tTimer == 0)
    {
        i = tSparkleIdx;
        tSparkleIdx += 4;
        if (tSparkleIdx >= ARRAY_COUNT(sTextSparkleCoords))
            tSparkleIdx -= ARRAY_COUNT(sTextSparkleCoords);
        CreateSprite(&sSpriteTemplate_SparklesBig, sTextSparkleCoords[i].x, sTextSparkleCoords[i].y, 3);
        if (++tNumSparkles >= (int)ARRAY_COUNT(sTextSparkleCoords))
            DestroyTask(taskId);
    }
    if (++tTimer > 9)
        tTimer = 0;
}

#undef tTimer
#undef tSparkleIdx
#undef tNumSparkles

static struct Sprite *GFScene_CreateLogoSprite(void)
{
    u8 spriteId = CreateSprite(&sSpriteTemplate_GameFreakLogoArt, 120, 70, 4);
    return &gSprites[spriteId];
}

#if REVISION >= 1
static void GFScene_CreatePresentsSprite(void)
{
    int i;
    for (i = 0; i < 2; i++)
        gSprites[CreateSprite(&sSpriteTemplate_Presents, 104 + 32 * i, 108, 5)].oam.tileNum += i * 4;
}
#endif

static void SpriteCB_Star(struct Sprite *sprite)
{
    u32 random;
    sprite->sStar_BaseX -= sprite->sStar_SpeedX;
    sprite->sStar_BaseY += sprite->sStar_SpeedY;
    sprite->sStar_SinIdx += 48;
    sprite->x = sprite->sStar_BaseX >> 4;
    sprite->y = sprite->sStar_BaseY >> 4;
    sprite->y2 = gSineTable[(sprite->sStar_SinIdx >> 4) + 64] >> 5;
    sprite->sStar_SparkleTimer++;
    if (sprite->sStar_SparkleTimer % sStarSparklesSpawnRate)
    {
        LoadWordFromTwoHalfwords(&sprite->sStar_SparkleRngSeed, &random);
        random = ISO_RANDOMIZE1(random);
        StoreWordInTwoHalfwords(&sprite->sStar_SparkleRngSeed, random);
        random >>= 16;
        GFScene_CreateStarSparkle(sprite->x, sprite->y + sprite->y2, random);
    }
    if (sprite->x < -8)
        DestroySprite(sprite);
}

// Callback for the sparkles that trail behind the star
static void SpriteCB_SparklesSmall_Star(struct Sprite *sprite)
{
    sprite->sSmSparkleStar_BaseX += sprite->sSmSparkleStar_SpeedX;
    sprite->sSmSparkleStar_BaseY += sprite->sSmSparkleStar_SpeedY;
    sprite->sSmSparkleStar_FallDist += ++sprite->sSmSparkleStar_FallSpeed;
    sprite->sSmSparkleStar_Timer++;
    sprite->x = (u16)sprite->sSmSparkleStar_BaseX >> sStarSparklesXprecision;
    sprite->y = sprite->sSmSparkleStar_BaseY >> sStarSparklesYprecision;
    if (sStarSparklesGravityShift && sprite->sSmSparkleStar_SpeedY < 0)
        sprite->y2 = sprite->sSmSparkleStar_FallDist >> sStarSparklesGravityShift;
    if (sprite->sSmSparkleStar_Timer > sStarSparklesFlickerStartTime)
    {
        sprite->invisible = !sprite->invisible;
        if (sprite->sSmSparkleStar_Timer > sStarSparklesDestroySpriteTime)
            DestroySprite(sprite);
    }
    if (sprite->y + sprite->y2 < 0 || sprite->y + sprite->y2 > DISPLAY_HEIGHT)
        DestroySprite(sprite);
}

// Callback for the small sparkles during the "Game Freak" text reveal
static void SpriteCB_SparklesSmall_Name(struct Sprite *sprite)
{
    if (sprite->sSmSparkleName_AnimTimer)
    {
        sprite->sSmSparkleName_AnimTimer--;
        sprite->sSmSparkleName_BaseY++;
        sprite->y = sprite->sSmSparkleName_BaseY >> 4;
        if (sprite->y > 86)
        {
            sprite->y = 74;
            sprite->sSmSparkleName_BaseY = 74 << 4;
        }
        if (sprite->animEnded)
        {
            if (sprite->sSmSparkleName_State == 0)
            {
                sprite->x += 26;
                if (sprite->x > 188)
                {
                    sprite->x = (188 * 2) - sprite->x;
                    sprite->sSmSparkleName_State = 1;
                }
            }
            else
            {
                sprite->x -= 26;
                if (sprite->x < 52)
                {
                    sprite->x = (52 * 2) - sprite->x;
                    sprite->sSmSparkleName_State = 0;
                }
            }
            StartSpriteAnim(sprite, ANIM_SPARKLE_ONCE);
        }
    }
    else
    {
        if (sprite->sSmSparkleName_NumLoops)
            DestroySprite(sprite);
        if (sprite->animEnded)
            StartSpriteAnim(sprite, ANIM_SPARKLE_LOOP);
        sprite->sSmSparkleName_BaseY += 4;
        sprite->y = sprite->sSmSparkleName_BaseY >> 4;
        if (++sprite->sSmSparkleName_DestroyTimer > 50)
            DestroySprite(sprite);
    }
}

// Callback for the big sparkles during the "Game Freak" text reveal
static void SpriteCB_SparklesBig(struct Sprite *sprite)
{
    if (sprite->animEnded)
        DestroySprite(sprite);
}
