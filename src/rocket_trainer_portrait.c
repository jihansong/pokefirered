#include "global.h"
#include "gflib.h"
#include "battle_gfx_sfx_util.h"
#include "rocket_trainer_portrait.h"
#include "constants/trainers.h"

const u8 gRocketTrainerHiresEnabled = ROCKET_TRAINER_HIRES_ENABLED;

#if ROCKET_TRAINER_HIRES_ENABLED
#define ROCKET_PORTRAIT_TAG 0xD7A0
#define ROCKET_PORTRAIT_BYTES 0x1200
extern u8 gOamLimit;

// Tile order: 64x64, 32x64, 64x32, 32x32. Not a row-major 96px image.
static const u32 sRocketPortraitTiles[] = INCBIN_U32("graphics/trainers/front_pics/jessie_james_hires.4bpp");
static const u16 sRocketPortraitPalette[] = INCBIN_U16("graphics/trainers/palettes/jessie_james_hires.gbapal");
STATIC_ASSERT(sizeof(sRocketPortraitTiles) == ROCKET_PORTRAIT_BYTES, RocketPortraitTileSize);
STATIC_ASSERT(sizeof(sRocketPortraitPalette) == 32, RocketPortraitPaletteSize);

static const struct SpriteSheet sRocketSheet =
{
    sRocketPortraitTiles, ROCKET_PORTRAIT_BYTES, ROCKET_PORTRAIT_TAG
};
static const struct SpritePalette sRocketPalette =
{
    sRocketPortraitPalette, ROCKET_PORTRAIT_TAG
};
static const struct OamData sRocketOam =
{
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64),
    .priority = 2
};
static const struct Subsprite sRocketPieces[] =
{
    { .x = -48, .y = -48, .shape = SPRITE_SHAPE(64x64), .size = SPRITE_SIZE(64x64), .tileOffset = 0,   .priority = 2 },
    { .x =  16, .y = -48, .shape = SPRITE_SHAPE(32x64), .size = SPRITE_SIZE(32x64), .tileOffset = 64,  .priority = 2 },
    { .x = -48, .y =  16, .shape = SPRITE_SHAPE(64x32), .size = SPRITE_SIZE(64x32), .tileOffset = 96,  .priority = 2 },
    { .x =  16, .y =  16, .shape = SPRITE_SHAPE(32x32), .size = SPRITE_SIZE(32x32), .tileOffset = 128, .priority = 2 }
};
static const struct SubspriteTable sRocketPieceTable[] =
{
    { ARRAY_COUNT(sRocketPieces), sRocketPieces }
};
static const struct SpriteTemplate sRocketTemplate =
{
    .tileTag = ROCKET_PORTRAIT_TAG,
    .paletteTag = ROCKET_PORTRAIT_TAG,
    .oam = &sRocketOam,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_TrainerSlideIn
};

static bool8 HasRocketOamBudget(void)
{
    u16 used = 0;
    u8 i;
    for (i = 0; i < MAX_SPRITES; i++)
    {
        const struct Sprite *s = &gSprites[i];
        if (!s->inUse || s->invisible)
            continue;
        if (s->subspriteTables != NULL && s->subspriteMode != SUBSPRITES_OFF
            && s->subspriteTables[s->subspriteTableNum].subsprites != NULL)
            used += s->subspriteTables[s->subspriteTableNum].subspriteCount;
        else
            used++;
    }
    return used + ARRAY_COUNT(sRocketPieces) <= gOamLimit;
}
#endif

bool8 TryCreateRocketTrainerPortrait(u16 trainerPicId, s16 x, s16 x2,
                                    s16 speed, u8 subpriority, u8 *spriteId)
{
#if ROCKET_TRAINER_HIRES_ENABLED
    u8 id;
    if (trainerPicId != TRAINER_PIC_JESSIE_JAMES || spriteId == NULL
        || !HasRocketOamBudget())
        return FALSE;

    // Never take ownership of a tag allocated by another live sprite.
    if (GetSpriteTileStartByTag(ROCKET_PORTRAIT_TAG) != 0xFFFF
        || IndexOfSpritePaletteTag(ROCKET_PORTRAIT_TAG) != 0xFF)
        return FALSE;

    // LoadSpriteSheet returns zero both for a valid tile zero and allocation
    // failure. The tag lookup distinguishes those outcomes.
    LoadSpriteSheet(&sRocketSheet);
    if (GetSpriteTileStartByTag(ROCKET_PORTRAIT_TAG) == 0xFFFF)
        return FALSE;
    if (LoadSpritePalette(&sRocketPalette) == 0xFF)
    {
        FreeSpriteTilesByTag(ROCKET_PORTRAIT_TAG);
        return FALSE;
    }

    id = CreateSprite(&sRocketTemplate, x - 8, 56, subpriority);
    if (id == MAX_SPRITES)
    {
        FreeSpritePaletteByTag(ROCKET_PORTRAIT_TAG);
        FreeSpriteTilesByTag(ROCKET_PORTRAIT_TAG);
        return FALSE;
    }
    SetSubspriteTables(&gSprites[id], sRocketPieceTable);
    gSprites[id].subspriteMode = SUBSPRITES_IGNORE_PRIORITY;
    gSprites[id].x2 = x2;
    gSprites[id].data[0] = speed;
    *spriteId = id;
    return TRUE;
#else
    (void)trainerPicId;
    (void)x;
    (void)x2;
    (void)speed;
    (void)subpriority;
    (void)spriteId;
    return FALSE;
#endif
}

bool8 TryDestroyRocketTrainerPortrait(struct Sprite *sprite)
{
    (void)sprite;
#if ROCKET_TRAINER_HIRES_ENABLED
    if (sprite->inUse && sprite->template == &sRocketTemplate)
    {
        DestroySprite(sprite);
        FreeSpriteTilesByTag(ROCKET_PORTRAIT_TAG);
        FreeSpritePaletteByTag(ROCKET_PORTRAIT_TAG);
        return TRUE;
    }
#endif
    return FALSE;
}

s16 GetTrainerPortraitExitX(const struct Sprite *sprite)
{
    (void)sprite;
#if ROCKET_TRAINER_HIRES_ENABLED
    // 280 leaves eight pixels of a 96px image visible at the right edge.
    if (sprite->inUse && sprite->template == &sRocketTemplate)
        return 296;
#endif
    return 280;
}
