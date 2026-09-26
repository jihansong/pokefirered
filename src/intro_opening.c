#include "global.h"
#include "gflib.h"
#include "m4a.h"
#include "sound.h"
#include "blend_palette.h"
#include "intro_opening.h"
#include "constants/songs.h"
#include "constants/species.h"

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
    push the pictures off the music. Frames the opening had to skip are counted in
    gOpeningDroppedFrames for QA (it must stay 0).

    Scenes drawn so far are tables made by tools (tools/make_intro_opening_scene*.py):
    per frame, every sprite track's place, frame and flags; the scroll of the layers;
    which backgrounds show; palette events. A table scene is played by the Table_*
    functions below. Scenes not drawn yet show a flat colour card with their number.

    Cuts. The picture keeps FR/LG's letterbox (window 1, rows 32-127, opened by the
    GAME FREAK scene). A scene draws on up to three layers, BG3 behind (priority 3), BG2
    (priority 2, behind the sprites) and BG1 (priority 0, in front of them, e.g. rain),
    from one of two slots: slot 0 is char block 0 with screen blocks 28, 29 and 20,
    slot 1 char block 1 with screen blocks 30, 31 and 21; scenes alternate. The next
    scene's tiles and maps go into the free slot a few frames before its cut; at the
    cut its palettes and sprites are set up, and the switch of the layers to its slot
    waits for the VBlank callback, so that all of it reaches the screen together and no
    frame is blank or mixed. The layers' scroll goes the same way: set during the
    frame, written in the VBlank that also uploads that frame's sprites; and only when
    that frame's sprites were built (a late frame repeats, it never shows half a cut).

    Sprites. A scene is a set of tracks; each track is one sprite that plays a strip of
    same-sized frames from ROM (uncompressed 4bpp, frames one after another). A track
    holds OBJ VRAM for one frame only: when its frame changes, the new frame's tiles are
    copied from ROM in the next VBlank (ProcessSpriteCopyRequests, before the OAM that
    shows them takes effect). A scene's sprites are made, hidden, when its graphics are
    preloaded, with one block of OBJ tiles for all of them; the cut only shows them.
*/

struct OpeningKey
{
    s16 x, y;       // corner of the sprite on screen
    u8 frame;
    u8 flags;
};

#define KEY_HIDE  (1 << 0)
#define KEY_FRONT (1 << 1)  // drawn with the track's front subpriority
#define KEY_HFLIP (1 << 2)
#define KEY_VFLIP (1 << 3)

struct OpeningScroll
{
    s16 backX, backY;   // BG3
    s16 frontX, frontY; // BG2
    s16 topX, topY;     // BG1
};

struct OpeningEvent
{
    u16 t;
    u8 type;
    u8 target;
    u8 coeff;
    u16 color;
};

enum {
    EVENT_BLEND,        // BlendPalettes(target, coeff, color): coeff 0 undoes it
    EVENT_CRY,          // PIKACHU's cry
    EVENT_BLEND_RANGE,  // BlendPalette on colours of the scene's BG palette: target =
                        // first colour | (count - 1) << 4
};

enum {
    TARGET_BG,          // the scene's BG palette
    TARGET_OBJ,         // the scene's sprite palettes
    TARGET_ALL,         // every palette but the backdrop's
};

// One sprite of a scene: its frames in ROM, its size and draw order (lower in front).
struct OpeningTrack
{
    const u32 *gfx;
    const struct OamData *oam;
    u16 paletteTag;
    u8 width, height;
    u8 subpriority;
    u8 frontSubpriority;    // with KEY_FRONT
};

// Which map each layer shows (MAP_*) for one of a table scene's layouts.
struct OpeningLayout
{
    u8 back, front, top;
};

enum {
    MAP_NONE,
    MAP_BACK,           // the slot's first map
    MAP_FRONT,          // the slot's second map
    MAP_EXTRA,          // the slot's third map
};

struct OpeningTableScene
{
    const struct OpeningTrack *tracks;
    u8 trackCount;
    u16 frames;
    const struct OpeningKey *keys;          // frames x trackCount
    const struct OpeningScroll *scroll;
    const u8 *layout;
    const struct OpeningLayout *layouts;
    const struct OpeningEvent *events;      // in time order, ended by t = 0xFFFF
    const u32 *bgGfx;
    u16 bgGfxSize;
    const u16 *maps[3];                     // back, front, extra (2 KB each or NULL)
    const u16 *bgPal;
    u8 bgBank;
    const u16 *const *objPals;
    const u16 *objPalTags;
    u8 objPalCount;
};

#include "data/intro_opening_scene2.h"
#include "data/intro_opening_scene45.h"

#define MUSIC_START   20
#define OPENING_END   751
#define PRELOAD_LEAD  4     // frames before a cut the next scene's graphics are loaded

#define NUM_SCENES    7
#define MAX_TRACKS    24

#define BG_BACK       3
#define BG_FRONT      2
#define BG_TOP        1
#define BG_MAP_BASE   28    // + 2 * slot (back), + 2 * slot + 1 (front)
#define BG_MAP_EXTRA  20    // + slot: a third map (in char block 2's space, unused)

#define PAL_CARD      1     // BG palette of the colour cards

#define TAG_ANCHOR 0x1400  // one tile, so the scenes' sprites count as sheet sprites

extern u8 gSpriteTileAllocBitmap[];
extern bool8 gShouldProcessSpriteCopyRequests;

enum {
    PALTAG_DIGITS = 0x1400,
    PALTAG_S2_PIKACHU,  // PIKACHU, its sparks and bolt
    PALTAG_S2_PROPS,    // OAK's arm, the ball, the puff
    PALTAG_RED,
    PALTAG_RED_SHIELD,  // RED crouched, with the small PIKACHU's colours
    PALTAG_SPEAROW,
};

struct OpeningScene
{
    u16 start;                          // first frame
    void (*load)(u8 scene, u8 slot);    // before the cut: BG tiles and maps, sprites
    void (*begin)(u8 scene, u8 slot);   // at the cut: palettes, show the slot
    void (*update)(u8 scene, u16 t);    // every frame, t = frames since the cut
    void (*end)(u8 scene);              // after its last frame
};

struct OpeningTrackSet
{
    u8 count;
    s16 tileStart;                      // one block of OBJ tiles for all the tracks
    u16 tileCount;
    const struct OpeningTrack *tracks[MAX_TRACKS];
    u8 spriteIds[MAX_TRACKS];
    u8 shownFrame[MAX_TRACKS];          // frame whose tiles are in the track's VRAM
    u16 tileOffset[MAX_TRACKS];
    struct SpriteTemplate templates[MAX_TRACKS];
};

struct Opening
{
    u32 startVblank;
    u32 lastT;
    s8 scene;       // index of the scene on screen, -1 before the first
    s8 loaded;      // index of the scene whose graphics wait in the free slot
    bool8 musicStarted;
    u8 pendingSlot;     // char block the layers switch to at the next VBlank, NO_SLOT if none
    u8 pendingMaps[3];  // screen blocks for BG3, BG2, BG1 (NO_SLOT: hidden)
    u8 layout;          // layout of the table scene on screen
    s32 lastEventT;     // last scene frame whose events were run
    struct OpeningScroll scroll; // written to the layers at the next VBlank
    struct OpeningTrackSet sets[2];     // by slot: the scene on screen, the next one
};

#define NO_SLOT  0xFF
#define NO_FRAME 0xFF

static EWRAM_DATA struct Opening *sOpening = NULL;
EWRAM_DATA u16 gOpeningDroppedFrames = 0;   // frames the opening skipped (QA: must be 0)

static void VBlankCB_Opening(void);
static void DestroyTracks(u8 set);
static void Card_Load(u8 scene, u8 slot);
static void Card_Begin(u8 scene, u8 slot);
static void Card_Update(u8 scene, u16 t);
static void Scene_End(u8 scene);
static void Table_Load(u8 scene, u8 slot);
static void Table_Begin(u8 scene, u8 slot);
static void Table_Update(u8 scene, u16 t);
static void Table_End(u8 scene);

#define CARD  Card_Load, Card_Begin, Card_Update, Scene_End
#define TABLE Table_Load, Table_Begin, Table_Update, Table_End

static const struct OpeningScene sScenes[NUM_SCENES] = {
    {  0, CARD},
    {136, TABLE},
    {212, CARD},
    {289, TABLE},
    {442, TABLE},
    {595, CARD},
    {672, CARD},
};

// ------------------------------------------------------------ graphics

static const u32 sDigits_Gfx[] = INCBIN_U32("graphics/intro/opening/placeholder_digits.4bpp");
static const u16 sDigits_Pal[] = INCBIN_U16("graphics/intro/opening/placeholder_digits.gbapal");

static const u32 sScene2_Bg_Gfx[]      = INCBIN_U32("graphics/intro/opening/scene2/bg.4bpp");
static const u16 sScene2_BgBack_Map[]  = INCBIN_U16("graphics/intro/opening/scene2/bg_back.bin");
static const u16 sScene2_BgFront_Map[] = INCBIN_U16("graphics/intro/opening/scene2/bg_front.bin");
static const u16 sScene2_BgCloseup_Map[] = INCBIN_U16("graphics/intro/opening/scene2/bg_closeup.bin");
static const u16 sScene2_Bg_Pal[]      = INCBIN_U16("graphics/intro/opening/scene2/bg.gbapal");
static const u32 sScene2_Pikachu_Gfx[] = INCBIN_U32("graphics/intro/opening/scene2/pikachu.4bpp");
static const u16 sScene2_Pikachu_Pal[] = INCBIN_U16("graphics/intro/opening/scene2/pikachu.gbapal");
static const u32 sScene2_Arm_Gfx[]     = INCBIN_U32("graphics/intro/opening/scene2/arm.4bpp");
static const u16 sScene2_Props_Pal[]   = INCBIN_U16("graphics/intro/opening/scene2/arm.gbapal");
static const u32 sScene2_Ball_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene2/ball.4bpp");
static const u32 sScene2_Spark_Gfx[]   = INCBIN_U32("graphics/intro/opening/scene2/spark.4bpp");
static const u32 sScene2_Bolt_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene2/bolt.4bpp");
static const u32 sScene2_Closeup_Gfx[] = INCBIN_U32("graphics/intro/opening/scene2/closeup.4bpp");
static const u32 sScene2_CrackleCu_Gfx[] = INCBIN_U32("graphics/intro/opening/scene2/crackle_cu.4bpp");

// closeup.png: for each quarter of the 128x128 close-up, its two frames (64x64 each)
#define CLOSEUP_QUARTER(q) (sScene2_Closeup_Gfx + (q) * 2 * (64 * 64 / 2) / 4)

static const u32 sStorm_Bg_Gfx[]      = INCBIN_U32("graphics/intro/opening/scene45/bg.4bpp");
static const u16 sStorm_Sky_Map[]     = INCBIN_U16("graphics/intro/opening/scene45/bg_sky.bin");
static const u16 sStorm_Field_Map[]   = INCBIN_U16("graphics/intro/opening/scene45/bg_field.bin");
static const u16 sStorm_Rain_Map[]    = INCBIN_U16("graphics/intro/opening/scene45/bg_rain.bin");
static const u16 sStorm_Bg_Pal[]      = INCBIN_U16("graphics/intro/opening/scene45/bg.gbapal");
static const u32 sStorm_Red_Gfx[]     = INCBIN_U32("graphics/intro/opening/scene45/red.4bpp");
static const u16 sStorm_Red_Pal[]     = INCBIN_U16("graphics/intro/opening/scene45/red.gbapal");
static const u32 sStorm_Shield_Gfx[]  = INCBIN_U32("graphics/intro/opening/scene45/shield.4bpp");
static const u16 sStorm_Shield_Pal[]  = INCBIN_U16("graphics/intro/opening/scene45/shield.gbapal");
static const u32 sStorm_Shield5_Gfx[] = INCBIN_U32("graphics/intro/opening/scene45/shield5.4bpp");
static const u32 sStorm_Bird_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene45/bird.4bpp");
static const u16 sStorm_Bird_Pal[]    = INCBIN_U16("graphics/intro/opening/scene45/bird.gbapal");
static const u32 sStorm_Small_Gfx[]   = INCBIN_U32("graphics/intro/opening/scene45/small.4bpp");
static const u32 sStorm_Pika_Gfx[]    = INCBIN_U32("graphics/intro/opening/scene45/pika.4bpp");
static const u16 sStorm_Pika_Pal[]    = INCBIN_U16("graphics/intro/opening/scene45/pika.gbapal");
static const u32 sStorm_Crackle_Gfx[] = INCBIN_U32("graphics/intro/opening/scene45/crackleL.4bpp");
static const u32 sStorm_BoltDown_Gfx[] = INCBIN_U32("graphics/intro/opening/scene45/boltA.4bpp");
static const u32 sStorm_Burst_Gfx[]   = INCBIN_U32("graphics/intro/opening/scene45/burst.4bpp");

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

static const struct OamData sOam_32x64 = {
    .shape = SPRITE_SHAPE(32x64),
    .size = SPRITE_SIZE(32x64),
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

static const struct OpeningTrack sDigitTrack = {sDigits_Gfx, &sOam_32x32, PALTAG_DIGITS, 32, 32, 0, 0};

// ------------------------------------------------------------ scene 2: the lab

// Same order as the tool's tracks; subpriority: lower is in front (the ball moves in
// front of the hand once it is knocked away).
static const struct OpeningTrack sScene2_Tracks[SCENE2_TRACK_COUNT] = {
    [SCENE2_TRACK_PIKACHU]     = {sScene2_Pikachu_Gfx, &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 8, 8},
    [SCENE2_TRACK_SLEEVE]      = {sScene2_Arm_Gfx,     &sOam_64x64, PALTAG_S2_PROPS,   64, 64, 6, 6},
    [SCENE2_TRACK_HAND]        = {sScene2_Arm_Gfx,     &sOam_64x64, PALTAG_S2_PROPS,   64, 64, 5, 5},
    [SCENE2_TRACK_BALL]        = {sScene2_Ball_Gfx,    &sOam_16x16, PALTAG_S2_PROPS,   16, 16, 7, 4},
    [SCENE2_TRACK_SMOKE]       = {sScene2_Ball_Gfx,    &sOam_16x16, PALTAG_S2_PROPS,   16, 16, 3, 3},
    [SCENE2_TRACK_SPARK_CHEEK] = {sScene2_Spark_Gfx,   &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 0, 0},
    [SCENE2_TRACK_SPARK_BALL]  = {sScene2_Spark_Gfx,   &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 1, 1},
    [SCENE2_TRACK_BOLT]        = {sScene2_Bolt_Gfx,    &sOam_64x32, PALTAG_S2_PIKACHU, 64, 32, 2, 2},
    [SCENE2_TRACK_BUST0]       = {CLOSEUP_QUARTER(0),  &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 9, 9},
    [SCENE2_TRACK_BUST1]       = {CLOSEUP_QUARTER(1),  &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 9, 9},
    [SCENE2_TRACK_BUST2]       = {CLOSEUP_QUARTER(2),  &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 9, 9},
    [SCENE2_TRACK_BUST3]       = {CLOSEUP_QUARTER(3),  &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 9, 9},
    [SCENE2_TRACK_CRACKLE_CU]  = {sScene2_CrackleCu_Gfx, &sOam_32x32, PALTAG_S2_PIKACHU, 32, 32, 0, 0},
};

static const struct OpeningLayout sScene2_Layouts[] = {
    {MAP_BACK, MAP_FRONT, MAP_NONE},     // the lab: wall and shelf, table
    {MAP_EXTRA, MAP_NONE, MAP_NONE},     // the close-up: bands
};

static const u16 *const sScene2_ObjPals[] = {sScene2_Pikachu_Pal, sScene2_Props_Pal};
static const u16 sScene2_ObjPalTags[] = {PALTAG_S2_PIKACHU, PALTAG_S2_PROPS};

// ------------------------------------------------------------ scenes 4 and 5: the storm

#define BIRD(i) {sStorm_Bird_Gfx, &sOam_16x16, PALTAG_SPEAROW, 16, 16, 20 + (i), (i)}
#define BIRDS \
    BIRD(0), BIRD(1), BIRD(2), BIRD(3), BIRD(4), BIRD(5), \
    BIRD(6), BIRD(7), BIRD(8), BIRD(9), BIRD(10), BIRD(11)

static const struct OpeningTrack sScene4_Tracks[SCENE4_TRACK_COUNT] = {
    {sStorm_Red_Gfx,    &sOam_64x64, PALTAG_RED,        64, 64, 10, 10},
    {sStorm_Shield_Gfx, &sOam_64x64, PALTAG_RED_SHIELD, 64, 64, 10, 10},
    BIRDS
};

static const struct OpeningTrack sScene5_Tracks[SCENE5_TRACK_COUNT] = {
    {sStorm_Shield5_Gfx,  &sOam_64x64, PALTAG_RED_SHIELD, 64, 64, 10, 10},
    {sStorm_Small_Gfx,    &sOam_32x32, PALTAG_S2_PIKACHU, 32, 32, 12, 12},
    {sStorm_Pika_Gfx,     &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 13, 13},
    {sStorm_Crackle_Gfx,  &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 14, 14},
    {sStorm_Crackle_Gfx,  &sOam_16x16, PALTAG_S2_PIKACHU, 16, 16, 15, 15},
    {sStorm_BoltDown_Gfx, &sOam_32x64, PALTAG_S2_PIKACHU, 32, 64, 16, 16},
    {sStorm_BoltDown_Gfx, &sOam_32x64, PALTAG_S2_PIKACHU, 32, 64, 17, 17},
    {sStorm_Burst_Gfx,    &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 18, 18},
    {sStorm_Burst_Gfx,    &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 18, 18},
    {sStorm_Burst_Gfx,    &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 18, 18},
    {sStorm_Burst_Gfx,    &sOam_64x64, PALTAG_S2_PIKACHU, 64, 64, 18, 18},
    BIRDS
};

static const struct OpeningLayout sStorm_Layouts[] = {
    {MAP_BACK, MAP_FRONT, MAP_NONE},     // sky and field
    {MAP_BACK, MAP_FRONT, MAP_EXTRA},    // and the rain in front of everything
};

static const u16 *const sScene4_ObjPals[] = {sStorm_Red_Pal, sStorm_Shield_Pal, sStorm_Bird_Pal};
static const u16 sScene4_ObjPalTags[] = {PALTAG_RED, PALTAG_RED_SHIELD, PALTAG_SPEAROW};
static const u16 *const sScene5_ObjPals[] = {sStorm_Shield_Pal, sStorm_Pika_Pal, sStorm_Bird_Pal};
static const u16 sScene5_ObjPalTags[] = {PALTAG_RED_SHIELD, PALTAG_S2_PIKACHU, PALTAG_SPEAROW};

static const struct OpeningTableScene sTableScenes[NUM_SCENES] = {
    [1] = {
        sScene2_Tracks, SCENE2_TRACK_COUNT, SCENE2_FRAMES, sScene2_Keys[0], sScene2_Scroll,
        sScene2_Layout, sScene2_Layouts, sScene2_Events, sScene2_Bg_Gfx, sizeof(sScene2_Bg_Gfx),
        {sScene2_BgBack_Map, sScene2_BgFront_Map, sScene2_BgCloseup_Map}, sScene2_Bg_Pal, 2,
        sScene2_ObjPals, sScene2_ObjPalTags, ARRAY_COUNT(sScene2_ObjPalTags),
    },
    [3] = {
        sScene4_Tracks, SCENE4_TRACK_COUNT, SCENE4_FRAMES, sScene4_Keys[0], sScene4_Scroll,
        sScene4_Layout, sStorm_Layouts, sScene4_Events, sStorm_Bg_Gfx, sizeof(sStorm_Bg_Gfx),
        {sStorm_Sky_Map, sStorm_Field_Map, sStorm_Rain_Map}, sStorm_Bg_Pal, 3,
        sScene4_ObjPals, sScene4_ObjPalTags, ARRAY_COUNT(sScene4_ObjPalTags),
    },
    [4] = {
        sScene5_Tracks, SCENE5_TRACK_COUNT, SCENE5_FRAMES, sScene5_Keys[0], sScene5_Scroll,
        sScene5_Layout, sStorm_Layouts, sScene5_Events, sStorm_Bg_Gfx, sizeof(sStorm_Bg_Gfx),
        {sStorm_Sky_Map, sStorm_Field_Map, sStorm_Rain_Map}, sStorm_Bg_Pal, 3,
        sScene5_ObjPals, sScene5_ObjPalTags, ARRAY_COUNT(sScene5_ObjPalTags),
    },
};

// ------------------------------------------------------------ the timeline

void Opening_Init(void)
{
    struct Opening *o = AllocZeroed(sizeof(*o));
    struct SpritePalette digitsPal;
    struct SpriteSheet anchor;

    sOpening = o;
    o->startVblank = gMain.vblankCounter2;
    o->scene = -1;
    o->loaded = -1;
    o->pendingSlot = NO_SLOT;
    gOpeningDroppedFrames = 0;
    SetVBlankCallback(VBlankCB_Opening);

    // Leave the GAME FREAK scene's layers and keep its letterbox window. BG3 (its
    // faded backdrop) stays until the first card replaces it at the first VBlank.
    HideBg(0);
    HideBg(BG_TOP);
    HideBg(BG_FRONT);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetBgControlAttributes(BG_BACK, 0, BG_MAP_BASE, 0, 0, 3, 0, 0);
    SetBgControlAttributes(BG_FRONT, 0, BG_MAP_BASE + 1, 0, 0, 2, 0, 0);
    SetBgControlAttributes(BG_TOP, 0, BG_MAP_EXTRA, 0, 0, 0, 0, 0);
    gPlttBufferUnfaded[0] = RGB_BLACK;
    gPlttBufferFaded[0] = RGB_BLACK;

    digitsPal.data = sDigits_Pal;
    digitsPal.tag = PALTAG_DIGITS;
    LoadSpritePalette(&digitsPal);
    anchor.data = sDigits_Gfx;
    anchor.size = TILE_SIZE_4BPP;
    anchor.tag = TAG_ANCHOR;
    LoadSpriteSheet(&anchor);
}

u8 Opening_Run(void)
{
    struct Opening *o = sOpening;
    u32 t = gMain.vblankCounter2 - o->startVblank;
    s8 k;

    if (t > o->lastT + 1)
        gOpeningDroppedFrames += t - o->lastT - 1;
    o->lastT = t;
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
    DestroyTracks(0);
    DestroyTracks(1);
    FreeSpritePaletteByTag(PALTAG_DIGITS);
    FreeSpriteTilesByTag(TAG_ANCHOR);
    Free(o);
    sOpening = NULL;
}

// ------------------------------------------------------------ layers

// Point the layers at a slot's maps and show them, at the next VBlank (maps: screen
// blocks for BG3, BG2, BG1, NO_SLOT to hide). The opening's code runs at the start of
// the frame, often still inside VBlank, where SetGpuReg writes at once: the new
// background would then show a frame before the sprites (OAM) and palettes set up on
// the same frame, which the VBlank callback uploads only at the next VBlank. So the
// switch, and every scroll, waits for that same VBlank.
static void ShowMaps(u8 charBase, u8 back, u8 front, u8 top)
{
    sOpening->pendingMaps[0] = back;
    sOpening->pendingMaps[1] = front;
    sOpening->pendingMaps[2] = top;
    sOpening->pendingSlot = charBase;
}

static u8 SlotMap(u8 slot, u8 map)
{
    switch (map)
    {
    case MAP_BACK:
        return BG_MAP_BASE + 2 * slot;
    case MAP_FRONT:
        return BG_MAP_BASE + 2 * slot + 1;
    case MAP_EXTRA:
        return BG_MAP_EXTRA + slot;
    }
    return NO_SLOT;
}

static void ShowLayout(u8 slot, const struct OpeningLayout *layout)
{
    ShowMaps(slot, SlotMap(slot, layout->back), SlotMap(slot, layout->front), SlotMap(slot, layout->top));
}

static void SetScroll(const struct OpeningScroll *scroll)
{
    sOpening->scroll = *scroll;
}

static void VBlankCB_Opening(void)
{
    static const u8 sBgs[3] = {BG_BACK, BG_FRONT, BG_TOP};
    struct Opening *o = sOpening;
    bool8 spritesBuilt = gShouldProcessSpriteCopyRequests;
    u8 i;

    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
    if (o == NULL || !spritesBuilt)
        return;     // the frame ran late: keep the layers as they are, with its sprites
    if (o->pendingSlot != NO_SLOT)
    {
        for (i = 0; i < 3; i++)
        {
            if (o->pendingMaps[i] != NO_SLOT)
            {
                SetBgControlAttributes(sBgs[i], o->pendingSlot, o->pendingMaps[i], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF);
                ShowBg(sBgs[i]);
            }
            else
            {
                HideBg(sBgs[i]);
            }
        }
        o->pendingSlot = NO_SLOT;
    }
    SetGpuReg(REG_OFFSET_BG3HOFS, o->scroll.backX);
    SetGpuReg(REG_OFFSET_BG3VOFS, o->scroll.backY);
    SetGpuReg(REG_OFFSET_BG2HOFS, o->scroll.frontX);
    SetGpuReg(REG_OFFSET_BG2VOFS, o->scroll.frontY);
    SetGpuReg(REG_OFFSET_BG1HOFS, o->scroll.topX);
    SetGpuReg(REG_OFFSET_BG1VOFS, o->scroll.topY);
}

// ------------------------------------------------------------ tracks

static u16 TrackFrameSize(const struct OpeningTrack *track)
{
    return track->width * track->height / 2;
}

// Make the sprites of a scene's tracks, hidden, in track set `set` (the scene's slot):
// one block of OBJ tiles holds one frame of each track. No tiles are copied until
// TrackShow asks for a frame; palettes are set when the scene begins (ActivateTracks).
static void CreateTracks(u8 set, const struct OpeningTrack *tracks, u8 count)
{
    struct OpeningTrackSet *ts = &sOpening->sets[set];
    u16 tiles = 0;
    u8 i;

    DestroyTracks(set);
    for (i = 0; i < count && i < MAX_TRACKS; i++)
    {
        ts->tileOffset[i] = tiles;
        tiles += TrackFrameSize(&tracks[i]) / TILE_SIZE_4BPP;
    }
    ts->tileStart = AllocSpriteTiles(tiles);
    if (ts->tileStart < 0)
        return;
    ts->tileCount = tiles;
    for (i = 0; i < count && i < MAX_TRACKS; i++)
    {
        struct SpriteTemplate *template = &ts->templates[i];
        u8 spriteId;

        template->tileTag = TAG_ANCHOR;
        template->paletteTag = TAG_NONE;
        template->oam = tracks[i].oam;
        template->anims = gDummySpriteAnimTable;
        template->images = NULL;
        template->affineAnims = gDummySpriteAffineAnimTable;
        template->callback = SpriteCallbackDummy;
        spriteId = CreateSprite(template, 0, 0, tracks[i].subpriority);
        if (spriteId != MAX_SPRITES)
        {
            gSprites[spriteId].invisible = TRUE;
            gSprites[spriteId].oam.tileNum = ts->tileStart + ts->tileOffset[i];
        }
        ts->tracks[i] = &tracks[i];
        ts->spriteIds[i] = spriteId;
        ts->shownFrame[i] = NO_FRAME;
    }
    ts->count = i;
}

// The scene begins: its sprites take their palettes (loaded just before).
static void ActivateTracks(u8 set)
{
    struct OpeningTrackSet *ts = &sOpening->sets[set];
    u8 i;

    for (i = 0; i < ts->count; i++)
    {
        if (ts->spriteIds[i] != MAX_SPRITES)
            gSprites[ts->spriteIds[i]].oam.paletteNum = IndexOfSpritePaletteTag(ts->tracks[i]->paletteTag);
    }
}

static void DestroyTracks(u8 set)
{
    struct OpeningTrackSet *ts = &sOpening->sets[set];
    u16 n;
    u8 i;

    for (i = 0; i < ts->count; i++)
    {
        if (ts->spriteIds[i] != MAX_SPRITES)
            DestroySprite(&gSprites[ts->spriteIds[i]]);
    }
    for (n = 0; n < ts->tileCount; n++)
        gSpriteTileAllocBitmap[(ts->tileStart + n) >> 3] &= ~(1 << ((ts->tileStart + n) & 7));
    ts->count = 0;
    ts->tileCount = 0;
}

static struct OpeningTrackSet *CurrentTracks(void)
{
    return &sOpening->sets[sOpening->scene & 1];
}

// Put track i at (x, y) (corner on screen) showing frame, with the KEY_* flags; a new
// frame's tiles are copied from ROM in the coming VBlank.
static void TrackShow(u8 i, s16 x, s16 y, u8 frame, u8 flags)
{
    struct OpeningTrackSet *ts = CurrentTracks();
    const struct OpeningTrack *track;
    struct Sprite *sprite;
    u16 size;

    if (i >= ts->count || ts->spriteIds[i] == MAX_SPRITES)
        return;
    track = ts->tracks[i];
    sprite = &gSprites[ts->spriteIds[i]];
    sprite->x = x + track->width / 2;
    sprite->y = y + track->height / 2;
    sprite->invisible = FALSE;
    sprite->subpriority = (flags & KEY_FRONT) ? track->frontSubpriority : track->subpriority;
    sprite->oam.matrixNum = ((flags & KEY_HFLIP) ? ST_OAM_HFLIP : 0) | ((flags & KEY_VFLIP) ? ST_OAM_VFLIP : 0);
    if (ts->shownFrame[i] != frame)
    {
        size = TrackFrameSize(track);
        RequestSpriteCopy((const u8 *)track->gfx + frame * size,
                          (u8 *)OBJ_VRAM0 + sprite->oam.tileNum * TILE_SIZE_4BPP, size);
        ts->shownFrame[i] = frame;
    }
}

static void TrackHide(u8 i)
{
    struct OpeningTrackSet *ts = CurrentTracks();

    if (i < ts->count && ts->spriteIds[i] != MAX_SPRITES)
        gSprites[ts->spriteIds[i]].invisible = TRUE;
}

// End of a scene: its sprites go and give their OBJ VRAM back.
static void Scene_End(u8 scene)
{
    DestroyTracks(scene & 1);
}

static const struct OpeningScroll sNoScroll = {0, 0, 0, 0, 0, 0};

// ------------------------------------------------------------ colour cards

// A card is one solid tile (colour 1 of the card palette) over the whole map.
static void Card_Load(u8 scene, u8 slot)
{
    CpuFill32(0, BG_CHAR_ADDR(slot), TILE_SIZE_4BPP);
    CpuFill32(0x11111111, (u8 *)BG_CHAR_ADDR(slot) + TILE_SIZE_4BPP, TILE_SIZE_4BPP);
    CpuFill16(1 | (PAL_CARD << 12), BG_SCREEN_ADDR(BG_MAP_BASE + 2 * slot), BG_SCREEN_SIZE);
    CreateTracks(slot, &sDigitTrack, 1);
}

static void Card_Begin(u8 scene, u8 slot)
{
    LoadPalette(&sCardColors[scene], BG_PLTT_ID(PAL_CARD) + 1, PLTT_SIZEOF(1));
    ActivateTracks(slot);
    ShowMaps(slot, BG_MAP_BASE + 2 * slot, NO_SLOT, NO_SLOT);
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
    TrackShow(0, (DISPLAY_WIDTH - 32) / 2, (DISPLAY_HEIGHT - 32) / 2, scene, 0);
    // The last scene fades to black before the title screen (F1440-1456)
    if (scene == NUM_SCENES - 1 && t == 62)
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
}

// ------------------------------------------------------------ table scenes

static void Table_Load(u8 scene, u8 slot)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];

    CpuFastCopy(ts->bgGfx, BG_CHAR_ADDR(slot), ts->bgGfxSize);
    if (ts->maps[0] != NULL)
        CpuFastCopy(ts->maps[0], BG_SCREEN_ADDR(SlotMap(slot, MAP_BACK)), BG_SCREEN_SIZE);
    if (ts->maps[1] != NULL)
        CpuFastCopy(ts->maps[1], BG_SCREEN_ADDR(SlotMap(slot, MAP_FRONT)), BG_SCREEN_SIZE);
    if (ts->maps[2] != NULL)
        CpuFastCopy(ts->maps[2], BG_SCREEN_ADDR(SlotMap(slot, MAP_EXTRA)), BG_SCREEN_SIZE);
    CreateTracks(slot, ts->tracks, ts->trackCount);
}

static void Table_Begin(u8 scene, u8 slot)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    struct SpritePalette pal;
    u8 i;

    LoadPalette(ts->bgPal, BG_PLTT_ID(ts->bgBank), PLTT_SIZE_4BPP);
    for (i = 0; i < ts->objPalCount; i++)
    {
        pal.data = ts->objPals[i];
        pal.tag = ts->objPalTags[i];
        LoadSpritePalette(&pal);
    }
    ActivateTracks(slot);
    sOpening->layout = 0xFF;
    sOpening->lastEventT = -1;
}

static u32 EventTarget(const struct OpeningTableScene *ts, u8 target)
{
    u32 mask = 0;
    u8 i;

    switch (target)
    {
    case TARGET_BG:
        return 1 << ts->bgBank;
    case TARGET_OBJ:
        for (i = 0; i < ts->objPalCount; i++)
            mask |= 1 << (16 + IndexOfSpritePaletteTag(ts->objPalTags[i]));
        return mask;
    }
    return PALETTES_ALL & ~1;
}

static void Table_Update(u8 scene, u16 t)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    const struct OpeningKey *keys;
    const struct OpeningEvent *ev;
    u8 i;

    if (t >= ts->frames)
        t = ts->frames - 1;
    // the events of every frame up to this one (even of a skipped frame)
    for (ev = ts->events; ev->t != 0xFFFF; ev++)
    {
        if ((s32)ev->t <= sOpening->lastEventT || ev->t > t)
            continue;
        if (ev->type == EVENT_BLEND)
            BlendPalettes(EventTarget(ts, ev->target), ev->coeff, ev->color);
        else if (ev->type == EVENT_CRY)
            PlayCry_Normal(SPECIES_PIKACHU, 0);
        else if (ev->type == EVENT_BLEND_RANGE)
            BlendPalette(BG_PLTT_ID(ts->bgBank) + (ev->target & 15), (ev->target >> 4) + 1, ev->coeff, ev->color);
    }
    sOpening->lastEventT = t;
    if (ts->layout[t] != sOpening->layout)
    {
        sOpening->layout = ts->layout[t];
        ShowLayout(scene & 1, &ts->layouts[sOpening->layout]);
    }
    SetScroll(&ts->scroll[t]);
    keys = ts->keys + t * ts->trackCount;
    for (i = 0; i < ts->trackCount; i++)
    {
        if (keys[i].flags & KEY_HIDE)
            TrackHide(i);
        else
            TrackShow(i, keys[i].x, keys[i].y, keys[i].frame, keys[i].flags);
    }
}

static void Table_End(u8 scene)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    u8 i;

    Scene_End(scene);
    for (i = 0; i < ts->objPalCount; i++)
        FreeSpritePaletteByTag(ts->objPalTags[i]);
}
