#include "global.h"
#include "gflib.h"
#include "companion_misty.h"
#include "event_object_movement.h"
#include "field_effect.h"
#include "field_player_avatar.h"
#include "constants/field_effects.h"

// A private tag and dynamic image tiles avoid the reserved overworld OBJ slots.
#define MISTY_HEART_PAL_TAG 0xD7F1
#define MISTY_HEART_FRAMES 48

static void SpriteCB_MistyHeart(struct Sprite *sprite);

static const u32 sMistyHeartTiles[] =
{
    0x00000000, 0x00111000, 0x01222100, 0x12333210,
    0x22333210, 0x22332210, 0x22222100, 0x22222100,
    0x00000000, 0x00001110, 0x00012221, 0x00123332,
    0x00123333, 0x00122332, 0x00012222, 0x00012222,
    0x22221000, 0x22210000, 0x22100000, 0x21000000,
    0x10000000, 0x00000000, 0x00000000, 0x00000000,
    0x00001222, 0x00000122, 0x00000012, 0x00000001,
    0x00000000, 0x00000000, 0x00000000, 0x00000000,
};

static const u16 sMistyHeartColors[16] =
{
    RGB(0, 0, 0), RGB(12, 2, 7), RGB(31, 8, 17), RGB(31, 22, 26),
};

static const struct SpritePalette sMistyHeartPalette =
{
    .data = sMistyHeartColors,
    .tag = MISTY_HEART_PAL_TAG,
};

static const struct OamData sMistyHeartOam =
{
    .shape = SPRITE_SHAPE(16x16),
    .size = SPRITE_SIZE(16x16),
    .priority = 0,
};

static const union AnimCmd sMistyHeartAnim[] =
{
    ANIMCMD_FRAME(0, MISTY_HEART_FRAMES),
    ANIMCMD_END,
};

static const union AnimCmd *const sMistyHeartAnims[] = {sMistyHeartAnim};
static const struct SpriteFrameImage sMistyHeartImages[] =
{
    {.data = (const u8 *)sMistyHeartTiles, .size = sizeof(sMistyHeartTiles)},
};

static const struct SpriteTemplate sMistyHeartTemplate =
{
    .tileTag = TAG_NONE,
    .paletteTag = MISTY_HEART_PAL_TAG,
    .oam = &sMistyHeartOam,
    .anims = sMistyHeartAnims,
    .images = sMistyHeartImages,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_MistyHeart,
};

u8 FldEff_MistyHeart(void)
{
    struct ObjectEvent *misty = GetMistyCompanionObject();
    u8 i, spriteId, paletteNum;

    // An absent/hidden companion must not leave waitfieldeffect waiting forever.
    if (misty == NULL || misty->invisible || misty->offScreen
        || misty->spriteId >= MAX_SPRITES
        || !gSprites[misty->spriteId].inUse || gSprites[misty->spriteId].invisible
        || gPlayerAvatar.objectEventId >= OBJECT_EVENTS_COUNT)
    {
        FieldEffectActiveListRemove(FLDEFF_MISTY_HEART);
        return 0;
    }
    // A second call shares the active lifetime rather than leaking another icon.
    for (i = 0; i < MAX_SPRITES; i++)
        if (gSprites[i].inUse && gSprites[i].callback == SpriteCB_MistyHeart)
        {
            FieldEffectActiveListRemove(FLDEFF_MISTY_HEART);
            return 0;
        }
    if (IndexOfSpritePaletteTag(MISTY_HEART_PAL_TAG) != 0xFF)
    {
        FieldEffectActiveListRemove(FLDEFF_MISTY_HEART);
        return 0;
    }
    paletteNum = LoadSpritePalette(&sMistyHeartPalette);
    if (paletteNum == 0xFF)
    {
        FieldEffectActiveListRemove(FLDEFF_MISTY_HEART);
        return 0;
    }
    spriteId = CreateSpriteAtEnd(&sMistyHeartTemplate, 0, 0, 0);
    if (spriteId == MAX_SPRITES)
    {
        FreeSpritePaletteByTag(MISTY_HEART_PAL_TAG);
        FieldEffectActiveListRemove(FLDEFF_MISTY_HEART);
        return 0;
    }
    gSprites[spriteId].coordOffsetEnabled = TRUE;
    gSprites[spriteId].data[1] = misty - gObjectEvents;
    gSprites[spriteId].data[2] = gPlayerAvatar.objectEventId;
    gSprites[spriteId].data[3] = gSaveBlock1Ptr->location.mapNum;
    gSprites[spriteId].data[4] = gSaveBlock1Ptr->location.mapGroup;
    SpriteCB_MistyHeart(&gSprites[spriteId]);
    return 0;
}

static void SpriteCB_MistyHeart(struct Sprite *sprite)
{
    struct ObjectEvent *misty, *player;
    struct Sprite *from, *to;
    s16 t;

    if (++sprite->data[0] > MISTY_HEART_FRAMES
        || gSaveBlock1Ptr->location.mapNum != sprite->data[3]
        || gSaveBlock1Ptr->location.mapGroup != sprite->data[4])
    {
        FieldEffectStop(sprite, FLDEFF_MISTY_HEART);
        return;
    }
    misty = &gObjectEvents[sprite->data[1]];
    player = &gObjectEvents[sprite->data[2]];
    if (!IsMistyCompanionObject(misty) || !player->active || !player->isPlayer
        || misty->invisible || misty->spriteId >= MAX_SPRITES
        || player->spriteId >= MAX_SPRITES
        || !gSprites[misty->spriteId].inUse || !gSprites[player->spriteId].inUse)
    {
        FieldEffectStop(sprite, FLDEFF_MISTY_HEART);
        return;
    }
    from = &gSprites[misty->spriteId];
    to = &gSprites[player->spriteId];
    t = sprite->data[0];
    if (t > 32) t = 32;
    sprite->x = from->x + (to->x - from->x) * t / 32;
    sprite->y = from->y + (to->y - from->y) * t / 32 - 24 - sprite->data[0] / 3;
    sprite->x2 = from->x2 + (to->x2 - from->x2) * t / 32;
    sprite->y2 = from->y2 + (to->y2 - from->y2) * t / 32;
    sprite->invisible = sprite->data[0] >= 40 && (sprite->data[0] & 2);
}
