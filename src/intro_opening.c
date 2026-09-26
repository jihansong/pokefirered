#include "global.h"
#include "gflib.h"
#include "m4a.h"
#include "sound.h"
#include "blend_palette.h"
#include "intro_opening.h"
#include "constants/songs.h"
#include "constants/species.h"

/*
    The Thunder Yellow opening, plan B (docs/anim/opening-storyboard-B.md): five cuts
    made only of official graphics already in this repository (field maps and sprites,
    trainer and POKeMON pictures, the FR/LG intro's forest, battle backgrounds, battle
    animation and weather sprites). The pictures are FR/LG's own; this file only plays
    them: it places, scrolls and times them and blends palettes.

    It starts on the frame FR/LG's Gengar/Nidorino fight did (F706 after power on,
    frame 0 below). MUS_INTRO_FIGHT starts on frame 20 as before; its bars start on
    frames 59, 136, 212, 289, 365, 442, 519 and 595. Every cut is on a bar, and on the
    first beat of bar 8 (frame 595, F1301) the opening hands over to the title screen,
    whose music takes over from there.

      #  frames    F          bars  cut
      1    0-135   706- 841   0-1   Pallet Town at dawn, setting off
      2  136-211   842- 917   2     the POKe BALL PIKACHU hates
      3  212-364   918-1070   3-4   rain and SPEAROW
      4  365-518  1071-1224   5-6   THUNDERBOLT
      5  519-594  1225-1300   7     the clear sky and HO-OH, fade to black
         595      1301              to the title screen

    (F is the frame the code sets a picture up; a screen capture shows it one frame
    later, storyboard 3.7.)

    The clock is the VBlank counter, not the number of calls, so a slow frame can not
    push the pictures off the music. Frames the opening had to skip are counted in
    gOpeningDroppedFrames for QA (it must stay 0).

    Every cut is a table made by tools/make_intro_opening_b.py: per frame, every sprite
    track's place, frame and flags; the scroll of the layers; palette events.

    Cuts. The picture keeps FR/LG's letterbox (window 1, rows 32-127, opened by the
    GAME FREAK scene). A cut draws on up to three 64x32-tile layers, BG3 behind
    (priority 3), BG2 (priority 2, behind the sprites) and BG1 (priority 0, in front of
    them, e.g. the tops of trees), from one of two slots: slot 0 is char block 0 with
    screen blocks 16-21, slot 1 char block 1 with screen blocks 22-27; cuts alternate.
    The next cut's tiles and maps go into the free slot a few frames before it; at the
    cut its palettes and sprites are set up, and the switch of the layers to its slot
    waits for the VBlank callback, so that all of it reaches the screen together and no
    frame is blank or mixed. The layers' scroll goes the same way: set during the
    frame, written in the VBlank that also uploads that frame's sprites; and only when
    that frame's sprites were built (a late frame repeats, it never shows half a cut).

    Sprites. A cut is a set of tracks; each track is one sprite that plays a strip of
    same-sized frames from ROM (uncompressed 4bpp, frames one after another). A track
    holds OBJ VRAM for one frame only: when its frame changes, the new frame's tiles are
    copied from ROM in the next VBlank (ProcessSpriteCopyRequests, before the OAM that
    shows them takes effect). A cut's sprites are made, hidden, when its graphics are
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
    EVENT_OBJ_BLEND,    // BlendPalette on one of the cut's sprite palettes (target: its
                        // index in objPalTags)
};

enum {
    TARGET_BG,          // the cut's BG palettes
    TARGET_OBJ,         // the cut's sprite palettes
    TARGET_ALL,         // every palette but BG palette 0 (the backdrop's)
};

// One sprite of a cut: its frames in ROM, its size and draw order (lower in front).
struct OpeningTrack
{
    const u32 *gfx;
    const struct OamData *oam;
    u16 paletteTag;
    u8 width, height;
    u8 subpriority;
    u8 frontSubpriority;    // with KEY_FRONT
};

struct OpeningTableScene
{
    const struct OpeningTrack *tracks;
    u8 trackCount;
    u16 frames;
    const struct OpeningKey *keys;          // frames x trackCount
    const struct OpeningScroll *scroll;
    const struct OpeningEvent *events;      // in time order, ended by t = 0xFFFF
    const u32 *bgGfx;
    u16 bgGfxSize;
    const u16 *maps[3];                     // BG3, BG2, BG1: 64x32 (4 KB) each, or NULL
    const u16 *bgPal;                       // bgPalCount palettes, loaded from BG_PAL_FIRST
    u8 bgPalCount;
    const u16 *const *objPals;
    const u16 *objPalTags;
    u8 objPalCount;
};

#define MUSIC_START   20
#define PRELOAD_LEAD  4     // frames before a cut the next cut's graphics are loaded

#define NUM_SCENES    5
#define MAX_TRACKS    32

#define BG_BACK       3
#define BG_FRONT      2
#define BG_TOP        1
#define BG_MAP_FIRST  16    // + 6 * slot + 2 * layer: two screen blocks per 64x32 map
#define BG_MAP_SIZE   (2 * BG_SCREEN_SIZE)
#define BG_PAL_FIRST  1     // the cuts' BG palettes; palette 0 keeps the black backdrop

#define TAG_ANCHOR 0x1400  // one tile, so the cuts' sprites count as sheet sprites

extern u8 gSpriteTileAllocBitmap[];
extern bool8 gShouldProcessSpriteCopyRequests;

static const struct OamData sOam_64x64 = {
    .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64),
    .priority = 1,
};

static const struct OamData sOam_32x32 = {
    .shape = SPRITE_SHAPE(32x32),
    .size = SPRITE_SIZE(32x32),
    .priority = 1,
};

static const struct OamData sOam_16x32 = {
    .shape = SPRITE_SHAPE(16x32),
    .size = SPRITE_SIZE(16x32),
    .priority = 1,
};

static const struct OamData sOam_16x16 = {
    .shape = SPRITE_SHAPE(16x16),
    .size = SPRITE_SIZE(16x16),
    .priority = 1,
};

static const struct OamData sOam_8x8 = {
    .shape = SPRITE_SHAPE(8x8),
    .size = SPRITE_SIZE(8x8),
    .priority = 1,
};

// The cuts: graphics, tracks, keys, scroll and events (tools/make_intro_opening_b.py)
#include "data/intro_opening_b.h"

static const u32 sAnchorTile[TILE_SIZE_4BPP / 4] = {0};

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
    s8 scene;       // index of the cut on screen, -1 before the first
    s8 loaded;      // index of the cut whose graphics wait in the free slot
    bool8 musicStarted;
    u8 pendingSlot;     // slot the layers switch to at the next VBlank, NO_SLOT if none
    u8 pendingShow;     // which of BG3, BG2, BG1 (bits 0-2) show from that slot
    s32 lastEventT;     // last cut frame whose events were run
    struct OpeningScroll scroll; // written to the layers at the next VBlank
    struct OpeningTrackSet sets[2];     // by slot: the cut on screen, the next one
};

#define NO_SLOT  0xFF
#define NO_FRAME 0xFF

static EWRAM_DATA struct Opening *sOpening = NULL;
EWRAM_DATA u16 gOpeningDroppedFrames = 0;   // frames the opening skipped (QA: must be 0)

static void VBlankCB_Opening(void);
static void DestroyTracks(u8 set);
static void Table_Load(u8 scene, u8 slot);
static void Table_Begin(u8 scene, u8 slot);
static void Table_Update(u8 scene, u16 t);
static void Table_End(u8 scene);

// ------------------------------------------------------------ the timeline

void Opening_Init(void)
{
    struct Opening *o = AllocZeroed(sizeof(*o));
    struct SpriteSheet anchor;

    sOpening = o;
    o->startVblank = gMain.vblankCounter2;
    o->scene = -1;
    o->loaded = -1;
    o->pendingSlot = NO_SLOT;
    gOpeningDroppedFrames = 0;
    SetVBlankCallback(VBlankCB_Opening);

    // Leave the GAME FREAK scene's layers and keep its letterbox window. BG3 (its
    // faded backdrop) stays until the first cut replaces it at the first VBlank.
    HideBg(0);
    HideBg(BG_TOP);
    HideBg(BG_FRONT);
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetBgControlAttributes(BG_FRONT, 0, BG_MAP_FIRST + 2, 1, 0, 2, 0, 0);
    SetBgControlAttributes(BG_TOP, 0, BG_MAP_FIRST + 4, 1, 0, 0, 0, 0);
    gPlttBufferUnfaded[0] = RGB_BLACK;
    gPlttBufferFaded[0] = RGB_BLACK;

    anchor.data = sAnchorTile;
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

    for (k = NUM_SCENES - 1; k > 0 && t < sSceneStarts[k]; k--)
        ;

    if (k != o->scene)
    {
        if (o->scene >= 0)
            Table_End(o->scene);
        if (o->loaded != k)
            Table_Load(k, k & 1);
        o->loaded = -1;
        o->scene = k;
        Table_Begin(k, k & 1);
    }
    Table_Update(k, t - sSceneStarts[k]);

    if (k + 1 < NUM_SCENES && o->loaded != k + 1 && t + PRELOAD_LEAD >= sSceneStarts[k + 1])
    {
        Table_Load(k + 1, (k + 1) & 1);
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
        Table_End(o->scene);
    DestroyTracks(0);
    DestroyTracks(1);
    FreeSpriteTilesByTag(TAG_ANCHOR);
    Free(o);
    sOpening = NULL;
}

// ------------------------------------------------------------ layers

static u8 SlotMap(u8 slot, u8 layer)
{
    return BG_MAP_FIRST + 6 * slot + 2 * layer;
}

// Point the layers at a slot's maps and show those the cut has, at the next VBlank.
// The opening's code runs at the start of the frame, often still inside VBlank, where
// SetGpuReg writes at once: the new background would then show a frame before the
// sprites (OAM) and palettes set up on the same frame, which the VBlank callback
// uploads only at the next VBlank. So the switch, and every scroll, waits for that
// same VBlank.
static void ShowSlot(u8 slot, u8 show)
{
    sOpening->pendingShow = show;
    sOpening->pendingSlot = slot;
}

static void VBlankCB_Opening(void)
{
    static const u8 sBgs[3] = {BG_BACK, BG_FRONT, BG_TOP};
    static const u8 sPriorities[3] = {3, 2, 0};
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
            if (o->pendingShow & (1 << i))
            {
                SetBgControlAttributes(sBgs[i], o->pendingSlot, SlotMap(o->pendingSlot, i), 1, 0, sPriorities[i], 0xFF, 0xFF);
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

// Make the sprites of a cut's tracks, hidden, in track set `set` (the cut's slot):
// one block of OBJ tiles holds one frame of each track. No tiles are copied until
// TrackShow asks for a frame; palettes are set when the cut begins (ActivateTracks).
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

// The cut begins: its sprites take their palettes (loaded just before).
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

// ------------------------------------------------------------ table cuts

static void Table_Load(u8 scene, u8 slot)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    u8 i;

    CpuFastCopy(ts->bgGfx, BG_CHAR_ADDR(slot), ts->bgGfxSize);
    for (i = 0; i < 3; i++)
    {
        if (ts->maps[i] != NULL)
            CpuFastCopy(ts->maps[i], BG_SCREEN_ADDR(SlotMap(slot, i)), BG_MAP_SIZE);
    }
    CreateTracks(slot, ts->tracks, ts->trackCount);
}

static void Table_Begin(u8 scene, u8 slot)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    struct SpritePalette pal;
    u8 i, show = 0;

    LoadPalette(ts->bgPal, BG_PLTT_ID(BG_PAL_FIRST), ts->bgPalCount * PLTT_SIZE_4BPP);
    for (i = 0; i < ts->objPalCount; i++)
    {
        pal.data = ts->objPals[i];
        pal.tag = ts->objPalTags[i];
        LoadSpritePalette(&pal);
    }
    ActivateTracks(slot);
    for (i = 0; i < 3; i++)
    {
        if (ts->maps[i] != NULL)
            show |= 1 << i;
    }
    ShowSlot(slot, show);
    sOpening->lastEventT = -1;
}

static u32 EventTarget(const struct OpeningTableScene *ts, u8 target)
{
    u32 mask = 0;
    u8 i;

    switch (target)
    {
    case TARGET_BG:
        return ((1 << ts->bgPalCount) - 1) << BG_PAL_FIRST;
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
        else if (ev->type == EVENT_OBJ_BLEND)
            BlendPalette(OBJ_PLTT_ID(IndexOfSpritePaletteTag(ts->objPalTags[ev->target])), 16, ev->coeff, ev->color);
    }
    sOpening->lastEventT = t;
    sOpening->scroll = ts->scroll[t];
    keys = ts->keys + t * ts->trackCount;
    for (i = 0; i < ts->trackCount; i++)
    {
        if (keys[i].flags & KEY_HIDE)
            TrackHide(i);
        else
            TrackShow(i, keys[i].x, keys[i].y, keys[i].frame, keys[i].flags);
    }
}

// End of a cut: its sprites go and give their OBJ VRAM back, its palettes go.
static void Table_End(u8 scene)
{
    const struct OpeningTableScene *ts = &sTableScenes[scene];
    u8 i;

    DestroyTracks(scene & 1);
    for (i = 0; i < ts->objPalCount; i++)
        FreeSpritePaletteByTag(ts->objPalTags[i]);
}
