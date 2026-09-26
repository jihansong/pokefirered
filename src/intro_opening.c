#include "global.h"
#include "gflib.h"
#include "m4a.h"
#include "intro_opening.h"
#include "constants/songs.h"

/*
    The Thunder Yellow opening (docs/anim/opening-storyboard.md).

    It takes the place of FR/LG's Gengar/Nidorino fight: it starts on the frame the
    fight did (F706 after power on, frame 0 below) and hands over to the title screen
    on the frame the fight did (F1457, frame 751), so the title still appears at F1459.
    MUS_INTRO_FIGHT starts on frame 20 as before; its bars start on frames 59, 136,
    212, 289, 365, 442, 519, 595 and 672, and every scene cuts on a bar.

      #  frames    F          bars  scene
      1    0-135   706- 841   0-1   Pallet Town at dawn, setting off
      2  136-211   842- 917   2     the PIKACHU that hates POKe BALLS
      3  212-288   918- 994   3     three friends join
      4  289-441   995-1147   4-5   storm and SPEAROW, shielding PIKACHU
      5  442-594  1148-1300   6-7   THUNDERBOLT
      6  595-671  1301-1377   8     rainbow and the golden bird
      7  672-750  1378-1456   9     TEAM ROCKET blasts off, fade to black
         751      1457              to the title screen

    The clock is the VBlank counter, not the number of calls, so a slow frame can not
    push the pictures off the music.

    Cuts. The picture keeps FR/LG's letterbox (window 1, rows 32-127, opened by the
    GAME FREAK scene). Each scene draws on BG3 from one of two slots: slot 0 is char
    block 0 and screen block 28, slot 1 char block 1 and screen block 29, and scenes
    alternate. The next scene's tiles and map go into the free slot (and its sprite
    tiles into OBJ VRAM) a few frames before its cut; at the cut its palettes, sprites
    and the switch of BG3 to its slot are all set in one frame and reach the screen
    together at the next VBlank, so no frame is blank or mixed.

    Scenes not drawn yet show a flat colour card with their number (the skeleton,
    docs/v0.11.0-plan.md 10.1 O0). Scene 2 is drawn: tools/make_intro_opening_scene2.py
    makes its pictures and the table of sprite positions it plays back.
*/

struct OpeningKey
{
    s16 x, y;       // corner of the sprite on screen
    u8 frame;
    u8 flags;
};

#define KEY_HIDE  (1 << 0)
#define KEY_FRONT (1 << 1)

#include "data/intro_opening_scene2.h"

#define MUSIC_START   20
#define OPENING_END   751
#define PRELOAD_LEAD  4     // frames before a cut the next scene's graphics are loaded

#define NUM_SCENES    7
#define MAX_SPRITES_PER_SCENE 8

#define BG_SCENE      3
#define BG_MAP_BASE   28    // + slot

#define PAL_CARD      1     // BG palette of the colour cards
#define PAL_SCENE2    2     // BG palette of scene 2 (baked into its tilemap)

enum {
    TAG_DIGITS = 0x1400,
    TAG_S2_PIKACHU,
    TAG_S2_ARM,
    TAG_S2_PROPS,
    TAG_S2_BOLT,
};

enum {
    PALTAG_DIGITS = 0x1400,
    PALTAG_S2_PIKACHU,
    PALTAG_S2_PROPS,
};

struct OpeningScene
{
    u16 start;                          // first frame
    void (*load)(u8 scene, u8 slot);    // before the cut: tiles, map, sprite tiles
    void (*begin)(u8 scene, u8 slot);   // at the cut: palettes, sprites, show the slot
    void (*update)(u8 scene, u16 t);    // every frame, t = frames since the cut
    void (*end)(u8 scene);              // after its last frame
};

struct Opening
{
    u32 startVblank;
    s8 scene;       // index of the scene on screen, -1 before the first
    s8 loaded;      // index of the scene whose graphics wait in the free slot
    bool8 musicStarted;
    u8 numSprites;
    u8 spriteIds[MAX_SPRITES_PER_SCENE];
    u8 pendingSlot; // slot BG3 switches to at the next VBlank, NO_SLOT if none
};

#define NO_SLOT 0xFF

static EWRAM_DATA struct Opening *sOpening = NULL;

static void VBlankCB_Opening(void);
static void Card_Load(u8 scene, u8 slot);
static void Card_Begin(u8 scene, u8 slot);
static void Card_Update(u8 scene, u16 t);
static void Scene_DestroySprites(u8 scene);
static void Scene2_Load(u8 scene, u8 slot);
static void Scene2_Begin(u8 scene, u8 slot);
static void Scene2_Update(u8 scene, u16 t);
static void Scene2_End(u8 scene);

static const struct OpeningScene sScenes[NUM_SCENES] = {
    {  0, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
    {136, Scene2_Load, Scene2_Begin, Scene2_Update, Scene2_End},
    {212, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
    {289, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
    {442, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
    {595, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
    {672, Card_Load,   Card_Begin,   Card_Update,   Scene_DestroySprites},
};

// ------------------------------------------------------------ graphics

static const u32 sDigits_Gfx[] = INCBIN_U32("graphics/intro/opening/placeholder_digits.4bpp");
static const u16 sDigits_Pal[] = INCBIN_U16("graphics/intro/opening/placeholder_digits.gbapal");

static const u32 sScene2_Bg_Gfx[]      = INCBIN_U32("graphics/intro/opening/scene2/bg.4bpp");
static const u16 sScene2_Bg_Map[]      = INCBIN_U16("graphics/intro/opening/scene2/bg.bin");
static const u16 sScene2_Bg_Pal[]      = INCBIN_U16("graphics/intro/opening/scene2/bg.gbapal");
static const u32 sScene2_Pikachu_Gfx[] = INCBIN_U32("graphics/intro/opening/scene2/pikachu.4bpp");
static const u16 sScene2_Pikachu_Pal[] = INCBIN_U16("graphics/intro/opening/scene2/pikachu.gbapal");
static const u32 sScene2_Arm_Gfx[]     = INCBIN_U32("graphics/intro/opening/scene2/arm.4bpp");
static const u32 sScene2_Props_Gfx[]   = INCBIN_U32("graphics/intro/opening/scene2/props.4bpp");
static const u16 sScene2_Props_Pal[]   = INCBIN_U16("graphics/intro/opening/scene2/props.gbapal");
static const u32 sScene2_Bolt_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene2/bolt.4bpp");

// The colour of each scene's stand-in card: dawn, lab, friends, storm, thunder,
// rainbow sky, dusk.
static const u16 sCardColors[NUM_SCENES] = {
    RGB(31, 22, 14),
    RGB(24, 20, 14),
    RGB(12, 24, 12),
    RGB(10, 12, 16),
    RGB(31, 29, 8),
    RGB(14, 24, 31),
    RGB(22, 16, 26),
};

static const struct OamData sOam_64x64 = {
    .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64),
    .priority = 1,
};

static const struct OamData sOam_64x32 = {
    .shape = SPRITE_SHAPE(64x32),
    .size = SPRITE_SIZE(64x32),
    .priority = 1,
};

static const struct OamData sOam_32x32 = {
    .shape = SPRITE_SHAPE(32x32),
    .size = SPRITE_SIZE(32x32),
    .priority = 1,
};

static const struct OamData sOam_16x16 = {
    .shape = SPRITE_SHAPE(16x16),
    .size = SPRITE_SIZE(16x16),
    .priority = 1,
};

static const struct SpriteTemplate sSpriteTemplate_Digit = {
    .tileTag = TAG_DIGITS,
    .paletteTag = PALTAG_DIGITS,
    .oam = &sOam_32x32,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

// ------------------------------------------------------------ the timeline

void Opening_Init(void)
{
    struct Opening *o = AllocZeroed(sizeof(*o));
    struct SpriteSheet digits;
    struct SpritePalette digitsPal;

    sOpening = o;
    o->startVblank = gMain.vblankCounter2;
    o->scene = -1;
    o->loaded = -1;
    o->pendingSlot = NO_SLOT;
    SetVBlankCallback(VBlankCB_Opening);

    // Leave the GAME FREAK scene's layers and keep its letterbox window. BG3 (its
    // faded backdrop) stays until the first card replaces it at the first VBlank.
    HideBg(0);
    HideBg(1);
    HideBg(2);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetBgControlAttributes(BG_SCENE, 0, BG_MAP_BASE, 0, 0, 3, 0, 0);
    ChangeBgX(BG_SCENE, 0, BG_COORD_SET);
    ChangeBgY(BG_SCENE, 0, BG_COORD_SET);
    gPlttBufferUnfaded[0] = RGB_BLACK;
    gPlttBufferFaded[0] = RGB_BLACK;

    digits.data = sDigits_Gfx;
    digits.size = sizeof(sDigits_Gfx);
    digits.tag = TAG_DIGITS;
    LoadSpriteSheet(&digits);
    digitsPal.data = sDigits_Pal;
    digitsPal.tag = PALTAG_DIGITS;
    LoadSpritePalette(&digitsPal);
}

u8 Opening_Run(void)
{
    struct Opening *o = sOpening;
    u32 t = gMain.vblankCounter2 - o->startVblank;
    s8 k;

    if (t >= OPENING_END)
        return 0;

    if (!o->musicStarted && t >= MUSIC_START)
    {
        m4aSongNumStart(MUS_INTRO_FIGHT);
        o->musicStarted = TRUE;
    }

    for (k = NUM_SCENES - 1; k > 0 && t < sScenes[k].start; k--)
        ;

    if (k != o->scene)
    {
        if (o->scene >= 0)
            sScenes[o->scene].end(o->scene);
        if (o->loaded != k)
            sScenes[k].load(k, k & 1);
        o->loaded = -1;
        o->scene = k;
        sScenes[k].begin(k, k & 1);
    }
    sScenes[k].update(k, t - sScenes[k].start);

    if (k + 1 < NUM_SCENES && o->loaded != k + 1 && t + PRELOAD_LEAD >= sScenes[k + 1].start)
    {
        sScenes[k + 1].load(k + 1, (k + 1) & 1);
        o->loaded = k + 1;
    }
    return k + 1;
}

void Opening_Free(void)
{
    struct Opening *o = sOpening;

    if (o == NULL)
        return;
    if (o->scene >= 0)
        sScenes[o->scene].end(o->scene);
    FreeSpriteTilesByTag(TAG_S2_PIKACHU);
    FreeSpriteTilesByTag(TAG_S2_ARM);
    FreeSpriteTilesByTag(TAG_S2_PROPS);
    FreeSpriteTilesByTag(TAG_S2_BOLT);
    FreeSpriteTilesByTag(TAG_DIGITS);
    FreeSpritePaletteByTag(PALTAG_DIGITS);
    FreeSpritePaletteByTag(PALTAG_S2_PIKACHU);
    FreeSpritePaletteByTag(PALTAG_S2_PROPS);
    Free(o);
    sOpening = NULL;
}

// Point BG3 at a slot and show it, at the next VBlank. The opening's code runs at
// the start of the frame, often still inside VBlank, where SetGpuReg writes at once:
// the new background would then show a frame before the sprites (OAM) and palettes
// set up on the same frame, which the VBlank callback uploads only at the next
// VBlank. So the switch waits for that same VBlank.
static void ShowSlot(u8 slot)
{
    sOpening->pendingSlot = slot;
}

static void VBlankCB_Opening(void)
{
    struct Opening *o = sOpening;

    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
    if (o != NULL && o->pendingSlot != NO_SLOT)
    {
        SetBgControlAttributes(BG_SCENE, o->pendingSlot, BG_MAP_BASE + o->pendingSlot, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF);
        ShowBg(BG_SCENE);
        o->pendingSlot = NO_SLOT;
    }
}

static u8 AddSprite(const struct SpriteTemplate *template, u8 subpriority)
{
    struct Opening *o = sOpening;
    u8 spriteId = CreateSprite(template, 0, 0, subpriority);

    if (o->numSprites < MAX_SPRITES_PER_SCENE)
        o->spriteIds[o->numSprites++] = spriteId;
    if (spriteId != MAX_SPRITES)
        gSprites[spriteId].invisible = TRUE;
    return spriteId;
}

static void Scene_DestroySprites(u8 scene)
{
    struct Opening *o = sOpening;
    u8 i;

    for (i = 0; i < o->numSprites; i++)
    {
        if (o->spriteIds[i] != MAX_SPRITES)
            DestroySprite(&gSprites[o->spriteIds[i]]);
    }
    o->numSprites = 0;
}

// ------------------------------------------------------------ colour cards

// A card is one solid tile (colour 1 of the card palette) over the whole map.
static void Card_Load(u8 scene, u8 slot)
{
    CpuFill32(0, BG_CHAR_ADDR(slot), TILE_SIZE_4BPP);
    CpuFill32(0x11111111, (u8 *)BG_CHAR_ADDR(slot) + TILE_SIZE_4BPP, TILE_SIZE_4BPP);
    CpuFill16(1 | (PAL_CARD << 12), BG_SCREEN_ADDR(BG_MAP_BASE + slot), BG_SCREEN_SIZE);
}

static void Card_Begin(u8 scene, u8 slot)
{
    u8 spriteId;

    LoadPalette(&sCardColors[scene], BG_PLTT_ID(PAL_CARD) + 1, PLTT_SIZEOF(1));
    spriteId = AddSprite(&sSpriteTemplate_Digit, 0);
    if (spriteId != MAX_SPRITES)
    {
        gSprites[spriteId].x = DISPLAY_WIDTH / 2;
        gSprites[spriteId].y = DISPLAY_HEIGHT / 2;
        gSprites[spriteId].oam.tileNum += scene * 16;
        gSprites[spriteId].invisible = FALSE;
    }
    ShowSlot(slot);
    if (scene == 0)
    {
        // Out of the white, as the original did after the GAME FREAK logo
        BlendPalettes(PALETTES_ALL & ~1, 16, RGB_WHITE);
        BeginNormalPaletteFade(PALETTES_ALL & ~1, -2, 16, 0, RGB_WHITE);
    }
}

static void Card_Update(u8 scene, u16 t)
{
    // The last scene fades to black before the title screen (F1440-1456)
    if (scene == NUM_SCENES - 1 && t == 62)
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
}

// ------------------------------------------------------------ scene 2

static const struct SpriteTemplate sSpriteTemplate_S2_Pikachu = {
    .tileTag = TAG_S2_PIKACHU,
    .paletteTag = PALTAG_S2_PIKACHU,
    .oam = &sOam_64x64,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct SpriteTemplate sSpriteTemplate_S2_Arm = {
    .tileTag = TAG_S2_ARM,
    .paletteTag = PALTAG_S2_PROPS,
    .oam = &sOam_64x64,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct SpriteTemplate sSpriteTemplate_S2_Prop = {
    .tileTag = TAG_S2_PROPS,
    .paletteTag = PALTAG_S2_PROPS,
    .oam = &sOam_16x16,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct SpriteTemplate sSpriteTemplate_S2_Bolt = {
    .tileTag = TAG_S2_BOLT,
    .paletteTag = PALTAG_S2_PROPS,
    .oam = &sOam_64x32,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

// Per track: template, size, the first tile of its frames in the sheet
// (sparks follow the five ball frames in props.png) and its draw order
// (lower is in front; the ball moves in front of the hand once it is knocked away).
static const struct {
    const struct SpriteTemplate *template;
    u8 width, height;
    u8 firstFrame;
    u8 subpriority;
} sScene2_Tracks[SCENE2_TRACK_COUNT] = {
    [SCENE2_TRACK_PIKACHU]     = {&sSpriteTemplate_S2_Pikachu, 64, 64, 0, 7},
    [SCENE2_TRACK_SLEEVE]      = {&sSpriteTemplate_S2_Arm,     64, 64, 0, 5},
    [SCENE2_TRACK_HAND]        = {&sSpriteTemplate_S2_Arm,     64, 64, 0, 4},
    [SCENE2_TRACK_BALL]        = {&sSpriteTemplate_S2_Prop,    16, 16, 0, 6},
    [SCENE2_TRACK_SPARK_CHEEK] = {&sSpriteTemplate_S2_Prop,    16, 16, 5, 0},
    [SCENE2_TRACK_SPARK_BALL]  = {&sSpriteTemplate_S2_Prop,    16, 16, 5, 1},
    [SCENE2_TRACK_BOLT]        = {&sSpriteTemplate_S2_Bolt,    64, 32, 0, 2},
};

static void Scene2_Load(u8 scene, u8 slot)
{
    struct SpriteSheet sheet;

    CpuFastCopy(sScene2_Bg_Gfx, BG_CHAR_ADDR(slot), sizeof(sScene2_Bg_Gfx));
    CpuFastCopy(sScene2_Bg_Map, BG_SCREEN_ADDR(BG_MAP_BASE + slot), sizeof(sScene2_Bg_Map));
    sheet.data = sScene2_Pikachu_Gfx;
    sheet.size = sizeof(sScene2_Pikachu_Gfx);
    sheet.tag = TAG_S2_PIKACHU;
    LoadSpriteSheet(&sheet);
    sheet.data = sScene2_Arm_Gfx;
    sheet.size = sizeof(sScene2_Arm_Gfx);
    sheet.tag = TAG_S2_ARM;
    LoadSpriteSheet(&sheet);
    sheet.data = sScene2_Props_Gfx;
    sheet.size = sizeof(sScene2_Props_Gfx);
    sheet.tag = TAG_S2_PROPS;
    LoadSpriteSheet(&sheet);
    sheet.data = sScene2_Bolt_Gfx;
    sheet.size = sizeof(sScene2_Bolt_Gfx);
    sheet.tag = TAG_S2_BOLT;
    LoadSpriteSheet(&sheet);
}

static void Scene2_Begin(u8 scene, u8 slot)
{
    struct SpritePalette pal;
    u8 i;

    LoadPalette(sScene2_Bg_Pal, BG_PLTT_ID(PAL_SCENE2), sizeof(sScene2_Bg_Pal));
    pal.data = sScene2_Pikachu_Pal;
    pal.tag = PALTAG_S2_PIKACHU;
    LoadSpritePalette(&pal);
    pal.data = sScene2_Props_Pal;
    pal.tag = PALTAG_S2_PROPS;
    LoadSpritePalette(&pal);
    for (i = 0; i < SCENE2_TRACK_COUNT; i++)
        AddSprite(sScene2_Tracks[i].template, sScene2_Tracks[i].subpriority);
    ShowSlot(slot);
}

static void Scene2_Update(u8 scene, u16 t)
{
    struct Opening *o = sOpening;
    const struct OpeningKey *keys;
    u8 i;

    if (t >= SCENE2_FRAMES)
        t = SCENE2_FRAMES - 1;
    keys = sScene2_Keys[t];
    for (i = 0; i < SCENE2_TRACK_COUNT && i < o->numSprites; i++)
    {
        struct Sprite *sprite;
        u8 w = sScene2_Tracks[i].width;
        u8 h = sScene2_Tracks[i].height;
        u8 tilesPerFrame = (w / 8) * (h / 8);

        if (o->spriteIds[i] == MAX_SPRITES)
            continue;
        sprite = &gSprites[o->spriteIds[i]];
        sprite->x = keys[i].x + w / 2;
        sprite->y = keys[i].y + h / 2;
        sprite->invisible = (keys[i].flags & KEY_HIDE) ? TRUE : FALSE;
        sprite->oam.tileNum = sprite->sheetTileStart + (sScene2_Tracks[i].firstFrame + keys[i].frame) * tilesPerFrame;
        if (i == SCENE2_TRACK_BALL)
            sprite->subpriority = (keys[i].flags & KEY_FRONT) ? 3 : 6;
    }
}

static void Scene2_End(u8 scene)
{
    Scene_DestroySprites(scene);
    FreeSpriteTilesByTag(TAG_S2_PIKACHU);
    FreeSpriteTilesByTag(TAG_S2_ARM);
    FreeSpriteTilesByTag(TAG_S2_PROPS);
    FreeSpriteTilesByTag(TAG_S2_BOLT);
    FreeSpritePaletteByTag(PALTAG_S2_PIKACHU);
    FreeSpritePaletteByTag(PALTAG_S2_PROPS);
}
