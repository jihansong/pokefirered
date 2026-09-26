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

    (F is the frame the code sets a picture up; a screen capture shows it one frame
    later, storyboard 3.7.)

    The clock is the VBlank counter, not the number of calls, so a slow frame can not
    push the pictures off the music.

    Cuts. The picture keeps FR/LG's letterbox (window 1, rows 32-127, opened by the
    GAME FREAK scene). A scene draws on up to two layers, BG3 behind (priority 3) and
    BG2 in front (priority 2), from one of two slots: slot 0 is char block 0 and screen
    blocks 28 (BG3) and 29 (BG2), slot 1 char block 1 and screen blocks 30 and 31;
    scenes alternate. The next scene's tiles and maps go into the free slot a few
    frames before its cut; at the cut its palettes and sprites are set up, and the
    switch of the layers to its slot waits for the VBlank callback, so that all of it
    reaches the screen together and no frame is blank or mixed. The layers' scroll
    (camera moves, parallax, shakes) goes the same way: set during the frame, written in
    the VBlank that also uploads that frame's sprites.

    Sprites. A scene is a set of tracks; each track is one sprite that plays a strip of
    same-sized frames from ROM (uncompressed 4bpp, frames one after another). A track
    holds OBJ VRAM for one frame only: when its frame changes, the new frame's tiles are
    copied from ROM in the next VBlank (ProcessSpriteCopyRequests, before the OAM that
    shows them takes effect). So a scene can have any number of frames; what it needs
    in OBJ VRAM is the sum of its tracks' frame sizes (scene 2: 240 tiles of 1024).

    Scenes not drawn yet show a flat colour card with their number (the skeleton,
    docs/v0.11.0-plan.md 10.1 O0). Scene 2 is drawn: tools/make_intro_opening_scene2.py
    makes its pictures and the table of sprite positions it plays back.
*/

// Set to 1 to replace scenes 4 and 5 by a test that plays scene-4/5-sized sprite work
// (about 1,300 tiles of frames through 19 tracks, frames changing every 2 frames) and
// counts slow frames in sOpeningStressLag. Never ship with 1.
#define OPENING_TILE_STRESS_TEST 0

struct OpeningKey
{
    s16 x, y;       // corner of the sprite on screen
    u8 frame;
    u8 flags;
};

#define KEY_HIDE  (1 << 0)
#define KEY_FRONT (1 << 1)

struct OpeningScroll
{
    s16 backX, backY;   // BG3
    s16 frontX, frontY; // BG2
};

// One sprite of a scene: its frames in ROM, its size and draw order (lower in front).
struct OpeningTrack
{
    const u32 *gfx;
    const struct OamData *oam;
    u16 paletteTag;
    u8 width, height;
    u8 subpriority;
};

#include "data/intro_opening_scene2.h"

#define MUSIC_START   20
#define OPENING_END   751
#define PRELOAD_LEAD  4     // frames before a cut the next scene's graphics are loaded

#define NUM_SCENES    7
#define MAX_TRACKS    20

#define BG_BACK       3
#define BG_FRONT      2
#define BG_MAP_BASE   28    // + 2 * slot (back), + 2 * slot + 1 (front)

#define PAL_CARD      1     // BG palette of the colour cards
#define PAL_SCENE2    2     // BG palette of scene 2 (baked into its tilemap)

enum {
    PALTAG_DIGITS = 0x1400,
    PALTAG_S2_PIKACHU,  // PIKACHU, its sparks and bolt
    PALTAG_S2_PROPS,    // OAK's arm, the ball, the puff
};

struct OpeningScene
{
    u16 start;                          // first frame
    void (*load)(u8 scene, u8 slot);    // before the cut: BG tiles and maps
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
    u8 numTracks;
    u8 pendingSlot; // slot the layers switch to at the next VBlank, NO_SLOT if none
    bool8 pendingFront; // whether that slot shows its front layer
    struct OpeningScroll scroll; // written to the layers at the next VBlank
    const struct OpeningTrack *tracks[MAX_TRACKS];
    u8 spriteIds[MAX_TRACKS];
    u8 shownFrame[MAX_TRACKS];          // frame whose tiles are in the track's VRAM
    struct SpriteFrameImage images[MAX_TRACKS];
    struct SpriteTemplate templates[MAX_TRACKS];
#if OPENING_TILE_STRESS_TEST
    u32 calls;
#endif
};

#define NO_SLOT  0xFF
#define NO_FRAME 0xFF

static EWRAM_DATA struct Opening *sOpening = NULL;
#if OPENING_TILE_STRESS_TEST
static EWRAM_DATA u32 sOpeningStressLag = 0;    // VBlanks without a call, read by QA
static EWRAM_DATA u16 sOpeningStressTiles = 0;  // OBJ tiles the test's tracks hold
#endif

static void VBlankCB_Opening(void);
static void Card_Load(u8 scene, u8 slot);
static void Card_Begin(u8 scene, u8 slot);
static void Card_Update(u8 scene, u16 t);
static void Scene_End(u8 scene);
static void Scene2_Load(u8 scene, u8 slot);
static void Scene2_Begin(u8 scene, u8 slot);
static void Scene2_Update(u8 scene, u16 t);
#if OPENING_TILE_STRESS_TEST
static void Stress_Begin(u8 scene, u8 slot);
static void Stress_Update(u8 scene, u16 t);
#define SCENE4_5 Card_Load, Stress_Begin, Stress_Update, Scene_End
#else
#define SCENE4_5 Card_Load, Card_Begin, Card_Update, Scene_End
#endif

static const struct OpeningScene sScenes[NUM_SCENES] = {
    {  0, Card_Load,   Card_Begin,   Card_Update,   Scene_End},
    {136, Scene2_Load, Scene2_Begin, Scene2_Update, Scene_End},
    {212, Card_Load,   Card_Begin,   Card_Update,   Scene_End},
    {289, SCENE4_5},
    {442, SCENE4_5},
    {595, Card_Load,   Card_Begin,   Card_Update,   Scene_End},
    {672, Card_Load,   Card_Begin,   Card_Update,   Scene_End},
};

// ------------------------------------------------------------ graphics

static const u32 sDigits_Gfx[] = INCBIN_U32("graphics/intro/opening/placeholder_digits.4bpp");
static const u16 sDigits_Pal[] = INCBIN_U16("graphics/intro/opening/placeholder_digits.gbapal");

static const u32 sScene2_Bg_Gfx[]      = INCBIN_U32("graphics/intro/opening/scene2/bg.4bpp");
static const u16 sScene2_BgBack_Map[]  = INCBIN_U16("graphics/intro/opening/scene2/bg_back.bin");
static const u16 sScene2_BgFront_Map[] = INCBIN_U16("graphics/intro/opening/scene2/bg_front.bin");
static const u16 sScene2_Bg_Pal[]      = INCBIN_U16("graphics/intro/opening/scene2/bg.gbapal");
static const u32 sScene2_Pikachu_Gfx[] = INCBIN_U32("graphics/intro/opening/scene2/pikachu.4bpp");
static const u16 sScene2_Pikachu_Pal[] = INCBIN_U16("graphics/intro/opening/scene2/pikachu.gbapal");
static const u32 sScene2_Arm_Gfx[]     = INCBIN_U32("graphics/intro/opening/scene2/arm.4bpp");
static const u16 sScene2_Props_Pal[]   = INCBIN_U16("graphics/intro/opening/scene2/arm.gbapal");
static const u32 sScene2_Ball_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene2/ball.4bpp");
static const u32 sScene2_Spark_Gfx[]   = INCBIN_U32("graphics/intro/opening/scene2/spark.4bpp");
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

static const struct OpeningTrack sDigitTrack = {sDigits_Gfx, &sOam_32x32, PALTAG_DIGITS, 32, 32, 0};

// ------------------------------------------------------------ the timeline

void Opening_Init(void)
{
    struct Opening *o = AllocZeroed(sizeof(*o));
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
    HideBg(BG_FRONT);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetBgControlAttributes(BG_BACK, 0, BG_MAP_BASE, 0, 0, 3, 0, 0);
    SetBgControlAttributes(BG_FRONT, 0, BG_MAP_BASE + 1, 0, 0, 2, 0, 0);
    gPlttBufferUnfaded[0] = RGB_BLACK;
    gPlttBufferFaded[0] = RGB_BLACK;

    digitsPal.data = sDigits_Pal;
    digitsPal.tag = PALTAG_DIGITS;
    LoadSpritePalette(&digitsPal);
}

u8 Opening_Run(void)
{
    struct Opening *o = sOpening;
    u32 t = gMain.vblankCounter2 - o->startVblank;
    s8 k;

#if OPENING_TILE_STRESS_TEST
    sOpeningStressLag = t - o->calls++;
#endif
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
    FreeSpritePaletteByTag(PALTAG_DIGITS);
    Free(o);
    sOpening = NULL;
}

// Point the layers at a slot and show them, at the next VBlank. The opening's code
// runs at the start of the frame, often still inside VBlank, where SetGpuReg writes at
// once: the new background would then show a frame before the sprites (OAM) and
// palettes set up on the same frame, which the VBlank callback uploads only at the
// next VBlank. So the switch, and every scroll, waits for that same VBlank.
static void ShowSlot(u8 slot, bool8 front)
{
    sOpening->pendingSlot = slot;
    sOpening->pendingFront = front;
}

static void SetScroll(const struct OpeningScroll *scroll)
{
    sOpening->scroll = *scroll;
}

static void VBlankCB_Opening(void)
{
    struct Opening *o = sOpening;

    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
    if (o == NULL)
        return;
    if (o->pendingSlot != NO_SLOT)
    {
        SetBgControlAttributes(BG_BACK, o->pendingSlot, BG_MAP_BASE + 2 * o->pendingSlot, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF);
        SetBgControlAttributes(BG_FRONT, o->pendingSlot, BG_MAP_BASE + 2 * o->pendingSlot + 1, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF);
        ShowBg(BG_BACK);
        if (o->pendingFront)
            ShowBg(BG_FRONT);
        else
            HideBg(BG_FRONT);
        o->pendingSlot = NO_SLOT;
    }
    SetGpuReg(REG_OFFSET_BG3HOFS, o->scroll.backX);
    SetGpuReg(REG_OFFSET_BG3VOFS, o->scroll.backY);
    SetGpuReg(REG_OFFSET_BG2HOFS, o->scroll.frontX);
    SetGpuReg(REG_OFFSET_BG2VOFS, o->scroll.frontY);
}

// ------------------------------------------------------------ tracks

static u16 TrackFrameSize(const struct OpeningTrack *track)
{
    return track->width * track->height / 2;
}

// Create a track's sprite (hidden). It holds OBJ VRAM for one frame of the track;
// no tiles are copied until TrackShow asks for a frame.
static u8 AddTrack(const struct OpeningTrack *track)
{
    struct Opening *o = sOpening;
    u8 i = o->numTracks;
    struct SpriteTemplate *template;
    u8 spriteId;

    if (i >= MAX_TRACKS)
        return MAX_TRACKS;
    o->images[i].data = track->gfx;
    o->images[i].size = TrackFrameSize(track);
    template = &o->templates[i];
    template->tileTag = TAG_NONE;
    template->paletteTag = track->paletteTag;
    template->oam = track->oam;
    template->anims = gDummySpriteAnimTable;
    template->images = &o->images[i];
    template->affineAnims = gDummySpriteAffineAnimTable;
    template->callback = SpriteCallbackDummy;
    spriteId = CreateSprite(template, 0, 0, track->subpriority);
    if (spriteId != MAX_SPRITES)
        gSprites[spriteId].invisible = TRUE;
    o->tracks[i] = track;
    o->spriteIds[i] = spriteId;
    o->shownFrame[i] = NO_FRAME;
    o->numTracks++;
    return i;
}

// Put track i at (x, y) (corner on screen) showing frame; a new frame's tiles are
// copied from ROM in the coming VBlank.
static void TrackShow(u8 i, s16 x, s16 y, u8 frame)
{
    struct Opening *o = sOpening;
    const struct OpeningTrack *track = o->tracks[i];
    struct Sprite *sprite;
    u16 size;

    if (i >= o->numTracks || o->spriteIds[i] == MAX_SPRITES)
        return;
    sprite = &gSprites[o->spriteIds[i]];
    sprite->x = x + track->width / 2;
    sprite->y = y + track->height / 2;
    sprite->invisible = FALSE;
    if (o->shownFrame[i] != frame)
    {
        size = TrackFrameSize(track);
        RequestSpriteCopy((const u8 *)track->gfx + frame * size,
                          (u8 *)OBJ_VRAM0 + sprite->oam.tileNum * TILE_SIZE_4BPP, size);
        o->shownFrame[i] = frame;
    }
}

static void TrackHide(u8 i)
{
    struct Opening *o = sOpening;

    if (i < o->numTracks && o->spriteIds[i] != MAX_SPRITES)
        gSprites[o->spriteIds[i]].invisible = TRUE;
}

// End of a scene: its sprites go and give their OBJ VRAM back.
static void Scene_End(u8 scene)
{
    struct Opening *o = sOpening;
    u8 i;

    for (i = 0; i < o->numTracks; i++)
    {
        if (o->spriteIds[i] != MAX_SPRITES)
            DestroySprite(&gSprites[o->spriteIds[i]]);
    }
    o->numTracks = 0;
    FreeSpritePaletteByTag(PALTAG_S2_PIKACHU);
    FreeSpritePaletteByTag(PALTAG_S2_PROPS);
}

static const struct OpeningScroll sNoScroll = {0, 0, 0, 0};

// ------------------------------------------------------------ colour cards

// A card is one solid tile (colour 1 of the card palette) over the whole map.
static void Card_Load(u8 scene, u8 slot)
{
    CpuFill32(0, BG_CHAR_ADDR(slot), TILE_SIZE_4BPP);
    CpuFill32(0x11111111, (u8 *)BG_CHAR_ADDR(slot) + TILE_SIZE_4BPP, TILE_SIZE_4BPP);
    CpuFill16(1 | (PAL_CARD << 12), BG_SCREEN_ADDR(BG_MAP_BASE + 2 * slot), BG_SCREEN_SIZE);
}

static void Card_Begin(u8 scene, u8 slot)
{
    LoadPalette(&sCardColors[scene], BG_PLTT_ID(PAL_CARD) + 1, PLTT_SIZEOF(1));
    AddTrack(&sDigitTrack);
    ShowSlot(slot, FALSE);
    SetScroll(&sNoScroll);
    if (scene == 0)
    {
        // Out of the white, as the original did after the GAME FREAK logo
        BlendPalettes(PALETTES_ALL & ~1, 16, RGB_WHITE);
        BeginNormalPaletteFade(PALETTES_ALL & ~1, -2, 16, 0, RGB_WHITE);
    }
}

static void Card_Update(u8 scene, u16 t)
{
    TrackShow(0, (DISPLAY_WIDTH - 32) / 2, (DISPLAY_HEIGHT - 32) / 2, scene);
    // The last scene fades to black before the title screen (F1440-1456)
    if (scene == NUM_SCENES - 1 && t == 62)
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
}

// ------------------------------------------------------------ scene 2

// Same order as the tool's tracks; subpriority: lower is in front (the ball moves in
// front of the hand once it is knocked away, below).
static const struct OpeningTrack sScene2_Tracks[SCENE2_TRACK_COUNT] = {
    [SCENE2_TRACK_PIKACHU]     = {sScene2_Pikachu_Gfx, &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 8},
    [SCENE2_TRACK_SLEEVE]      = {sScene2_Arm_Gfx,     &sOam_64x64, PALTAG_S2_PROPS,   64, 64, 6},
    [SCENE2_TRACK_HAND]        = {sScene2_Arm_Gfx,     &sOam_64x64, PALTAG_S2_PROPS,   64, 64, 5},
    [SCENE2_TRACK_BALL]        = {sScene2_Ball_Gfx,    &sOam_16x16, PALTAG_S2_PROPS,   16, 16, 7},
    [SCENE2_TRACK_SMOKE]       = {sScene2_Ball_Gfx,    &sOam_16x16, PALTAG_S2_PROPS,   16, 16, 3},
    [SCENE2_TRACK_SPARK_CHEEK] = {sScene2_Spark_Gfx,   &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 0},
    [SCENE2_TRACK_SPARK_BALL]  = {sScene2_Spark_Gfx,   &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 1},
    [SCENE2_TRACK_BOLT]        = {sScene2_Bolt_Gfx,    &sOam_64x32, PALTAG_S2_PIKACHU, 64, 32, 2},
};

static void Scene2_Load(u8 scene, u8 slot)
{
    CpuFastCopy(sScene2_Bg_Gfx, BG_CHAR_ADDR(slot), sizeof(sScene2_Bg_Gfx));
    CpuFastCopy(sScene2_BgBack_Map, BG_SCREEN_ADDR(BG_MAP_BASE + 2 * slot), sizeof(sScene2_BgBack_Map));
    CpuFastCopy(sScene2_BgFront_Map, BG_SCREEN_ADDR(BG_MAP_BASE + 2 * slot + 1), sizeof(sScene2_BgFront_Map));
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
        AddTrack(&sScene2_Tracks[i]);
    ShowSlot(slot, TRUE);
}

static void Scene2_Update(u8 scene, u16 t)
{
    const struct OpeningKey *keys;
    u8 i;

    if (t >= SCENE2_FRAMES)
        t = SCENE2_FRAMES - 1;
    keys = sScene2_Keys[t];
    SetScroll(&sScene2_Scroll[t]);
    for (i = 0; i < SCENE2_TRACK_COUNT; i++)
    {
        if (keys[i].flags & KEY_HIDE)
            TrackHide(i);
        else
            TrackShow(i, keys[i].x, keys[i].y, keys[i].frame);
    }
    if (sOpening->spriteIds[SCENE2_TRACK_BALL] != MAX_SPRITES)
        gSprites[sOpening->spriteIds[SCENE2_TRACK_BALL]].subpriority =
            (keys[SCENE2_TRACK_BALL].flags & KEY_FRONT) ? 4 : 7;
}

#if OPENING_TILE_STRESS_TEST
// ------------------------------------------------------------ OBJ tile test (not shipped)

// Scene 4/5 sized sprite work: RED and PIKACHU 64x64 with 20 frames each, a 64x32
// effect with 8 frames and 16 birds 16x16 with 4 frames each, about 1,300 tiles of
// frames in all. The frames are any ROM data (scene 2's sheets and what follows them).
#define STRESS_BIRDS 16
static const struct OpeningTrack sStressTracks[3 + 1] = {
    {sScene2_Pikachu_Gfx, &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 2},
    {sScene2_Arm_Gfx,     &sOam_64x64, PALTAG_S2_PROPS,   64, 64, 3},
    {sScene2_Bolt_Gfx,    &sOam_64x32, PALTAG_S2_PIKACHU, 64, 32, 1},
    {sScene2_Ball_Gfx,    &sOam_16x16, PALTAG_S2_PROPS,   16, 16, 0},
};

static void Stress_Begin(u8 scene, u8 slot)
{
    struct SpritePalette pal;
    u8 i, n;
    u16 tiles = 0;

    Card_Begin(scene, slot);
    pal.data = sScene2_Pikachu_Pal;
    pal.tag = PALTAG_S2_PIKACHU;
    LoadSpritePalette(&pal);
    pal.data = sScene2_Props_Pal;
    pal.tag = PALTAG_S2_PROPS;
    LoadSpritePalette(&pal);
    for (i = 0; i < 3 + STRESS_BIRDS; i++)
    {
        n = AddTrack(&sStressTracks[i < 3 ? i : 3]);
        if (n < MAX_TRACKS && sOpening->spriteIds[n] != MAX_SPRITES)
            tiles += TrackFrameSize(sOpening->tracks[n]) / TILE_SIZE_4BPP;
    }
    sOpeningStressTiles = tiles;
}

static void Stress_Update(u8 scene, u16 t)
{
    u8 i;

    Card_Update(scene, t);
    TrackShow(1, 20 + (t % 40), 48, (t / 2) % 20);
    TrackShow(2, 150 - (t % 30), 48, (t / 2 + 7) % 20);
    TrackShow(3, 80, 40, (t / 2) % 8);
    for (i = 0; i < STRESS_BIRDS; i++)
        TrackShow(4 + i, (i * 15 + t * 2) % 240, 36 + (i % 4) * 20, (t / 2 + i) % 4);
}
#endif
