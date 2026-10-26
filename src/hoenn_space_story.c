#include "global.h"
#include "gflib.h"
#include "bg.h"
#include "event_data.h"
#include "field_fadetransition.h"
#include "field_player_avatar.h"
#include "fieldmap.h"
#include "help_system.h"
#include "hoenn_space_story.h"
#include "malloc.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "quest_log.h"
#include "scanline_effect.h"
#include "sound.h"
#include "task.h"
#include "trig.h"
#include "constants/flags.h"
#include "constants/maps.h"
#include "constants/quest_log.h"
#include "constants/songs.h"
#include "constants/species.h"
#include "constants/vars.h"

// DIAGNOSTIC STAGING ONLY: independent passenger craft and two-stage separation.
// Dedicated tank/SRB assets are selected; art/runtime approval remains separate.
// Return reuses the existing airplane runway/sky without changing those assets.
// Existing Earth/exhaust and five mission-map drafts retain their art-review limits.
// No new music, mutable global, map/header/save layout, or mission guard changes.
#define TAG_SPACE_TANK 0x7B10
#define TAG_SPACE_EXHAUST 0x7B11
#define TAG_SPACE_CRAFT 0x7B12
#define TAG_SPACE_SRB_LEFT 0x7B13
#define TAG_SPACE_SRB_RIGHT 0x7B14
#define FLIGHT_RESOURCE_ARG 14
#define SPACE_OUTBOUND_FRAMES 1800
#define SPACE_RETURN_FRAMES 1440
#define SPACE_CLOUD_BASE_TILE 48
#define SPACE_RUNWAY_PALETTE 3
#define SPACE_GEAR_COUNT 2
#define SPACE_TRANSITION_HALF 32

enum {UNIT_TANK, UNIT_SRB_LEFT, UNIT_SRB_RIGHT, UNIT_CRAFT, SPACE_UNIT_COUNT};
enum {EFFECT_MAIN, EFFECT_SRB_LEFT, EFFECT_SRB_RIGHT, EFFECT_RCS, SPACE_EFFECT_COUNT};
enum {SCENE_RUNNING, SCENE_FADE_OUT, SCENE_EXIT};
#define tState data[0]
#define tFrame data[1]
#define tReturning data[2]

static const u32 sTankTiles[] = INCBIN_U32("graphics/hoenn_space_story/exterior_v3/tank.4bpp");
static const u16 sTankPalette[] = INCBIN_U16("graphics/hoenn_space_story/exterior_v3/tank.gbapal");
static const u32 sBoosterTiles[] = INCBIN_U32("graphics/hoenn_space_story/exterior_v3/booster.4bpp");
static const u16 sBoosterPalette[] = INCBIN_U16("graphics/hoenn_space_story/exterior_v3/booster.gbapal");
static const u32 sCraftTiles[] = INCBIN_U32("graphics/hoenn_space_story/exterior_v3/orbiter.4bpp");
static const u16 sCraftPalette[] = INCBIN_U16("graphics/hoenn_space_story/exterior_v3/orbiter.gbapal");
static const u32 sExhaustTiles[] = INCBIN_U32("graphics/hoenn_space_story/exhaust.4bpp");
static const u16 sExhaustPalette[] = INCBIN_U16("graphics/hoenn_space_story/exhaust.gbapal");
static const u32 sEarthTiles[] = INCBIN_U32("graphics/hoenn_space_story/earth.4bpp");
static const u16 sEarthPalette[] = INCBIN_U16("graphics/hoenn_space_story/earth.gbapal");
static const u16 sEarthMap[] = INCBIN_U16("graphics/hoenn_space_story/earth_tilemap.bin");
static const u32 sGroundTiles[] = INCBIN_U32("graphics/hoenn_space_story/exterior_v3/launch_ground.4bpp");
static const u16 sGroundPalette[] = INCBIN_U16("graphics/hoenn_space_story/exterior_v3/launch_ground.gbapal");
static const u16 sGroundMap[] = INCBIN_U16("graphics/hoenn_space_story/exterior_v3/launch_ground_tilemap.bin");
static const u32 sRunwayTiles[] = INCBIN_U32("graphics/airplane/ground.4bpp");
static const u16 sRunwayPalette[] = INCBIN_U16("graphics/airplane/ground.gbapal");
static const u16 sRunwayMap[] = INCBIN_U16("graphics/airplane/ground_tilemap.bin");
static const u32 sLandingSkyTiles[] = INCBIN_U32("graphics/airplane/sky.4bpp");
static const u16 sLandingSkyPalette[] = INCBIN_U16("graphics/airplane/sky.gbapal");
static const u16 sLandingSkyMap[] = INCBIN_U16("graphics/airplane/sky_tilemap.bin");
static const u32 sCloudTiles[] = INCBIN_U32("graphics/airplane/clouds.4bpp");
static const u16 sCloudPalette[] = INCBIN_U16("graphics/airplane/clouds.gbapal");
static const u16 sCloudMap[] = INCBIN_U16("graphics/airplane/clouds_tilemap.bin");

static const struct BgTemplate sSpaceBgTemplates[] =
{
    {.bg = 1, .charBaseIndex = 0, .mapBaseIndex = 26, .screenSize = 2, .paletteMode = 0, .priority = 1},
    {.bg = 2, .charBaseIndex = 1, .mapBaseIndex = 28, .screenSize = 0, .paletteMode = 0, .priority = 0},
    {.bg = 3, .charBaseIndex = 2, .mapBaseIndex = 29, .screenSize = 0, .paletteMode = 0, .priority = 2},
};
static const struct SpriteSheet sUnitSheets[] =
{
    {sTankTiles, sizeof(sTankTiles), TAG_SPACE_TANK},
    {sBoosterTiles, sizeof(sBoosterTiles), TAG_SPACE_SRB_LEFT},
    {sBoosterTiles, sizeof(sBoosterTiles), TAG_SPACE_SRB_RIGHT},
    {sCraftTiles, sizeof(sCraftTiles), TAG_SPACE_CRAFT},
    {sExhaustTiles, sizeof(sExhaustTiles), TAG_SPACE_EXHAUST},
};
static const struct SpritePalette sUnitPalettes[] =
{
    {sTankPalette, TAG_SPACE_TANK},
    {sBoosterPalette, TAG_SPACE_SRB_LEFT},
    {sBoosterPalette, TAG_SPACE_SRB_RIGHT},
    {sCraftPalette, TAG_SPACE_CRAFT},
    {sExhaustPalette, TAG_SPACE_EXHAUST},
};
// Create nonaffine sprites, then explicitly allocate/own every actual matrix.
// This avoids InitSpriteAffineAnim's silent allocation-failure behavior.
static const struct OamData sPairOam =
{
    .affineMode = ST_OAM_AFFINE_OFF, .shape = SPRITE_SHAPE(64x64),
    .size = SPRITE_SIZE(64x64), .priority = 0,
};
static const struct OamData sEffectOam =
{
    .affineMode = ST_OAM_AFFINE_OFF, .shape = SPRITE_SHAPE(16x32),
    .size = SPRITE_SIZE(16x32), .priority = 0,
};
static const union AnimCmd sLauncherUpper[] = {ANIMCMD_FRAME(0, 1), ANIMCMD_END};
static const union AnimCmd sLauncherLower[] = {ANIMCMD_FRAME(64, 1), ANIMCMD_END};
static const union AnimCmd *const sLauncherAnims[] = {sLauncherUpper, sLauncherLower};
static const union AnimCmd sCraftL0[] = {ANIMCMD_FRAME(0, 1), ANIMCMD_END};
static const union AnimCmd sCraftL1[] = {ANIMCMD_FRAME(128, 1), ANIMCMD_END};
static const union AnimCmd sCraftL2[] = {ANIMCMD_FRAME(256, 1), ANIMCMD_END};
static const union AnimCmd sCraftR0[] = {ANIMCMD_FRAME(64, 1), ANIMCMD_END};
static const union AnimCmd sCraftR1[] = {ANIMCMD_FRAME(192, 1), ANIMCMD_END};
static const union AnimCmd sCraftR2[] = {ANIMCMD_FRAME(320, 1), ANIMCMD_END};
static const union AnimCmd *const sCraftLeftAnims[] = {sCraftL0, sCraftL1, sCraftL2};
static const union AnimCmd *const sCraftRightAnims[] = {sCraftR0, sCraftR1, sCraftR2};
static const struct OamData sGearOam =
{
    .affineMode = ST_OAM_AFFINE_OFF, .shape = SPRITE_SHAPE(8x16),
    .size = SPRITE_SIZE(8x16), .priority = 0,
};
// Landing gear uses the craft sheet's appended two tiles and existing palette/matrix.
static const union AnimCmd sGearAnim[] = {ANIMCMD_FRAME(384, 1), ANIMCMD_END};
static const union AnimCmd *const sGearAnims[] = {sGearAnim};
static const union AnimCmd sEffectAnim[] = {ANIMCMD_FRAME(0, 1), ANIMCMD_END};
static const union AnimCmd *const sEffectAnims[] = {sEffectAnim};
#define SPACE_TEMPLATE(tag, oamdata, animtable) {tag, tag, oamdata, animtable, NULL, gDummySpriteAffineAnimTable, SpriteCallbackDummy}
static const struct SpriteTemplate sTankTemplate = SPACE_TEMPLATE(TAG_SPACE_TANK, &sPairOam, sLauncherAnims);
static const struct SpriteTemplate sLeftSrbTemplate = SPACE_TEMPLATE(TAG_SPACE_SRB_LEFT, &sPairOam, sLauncherAnims);
static const struct SpriteTemplate sRightSrbTemplate = SPACE_TEMPLATE(TAG_SPACE_SRB_RIGHT, &sPairOam, sLauncherAnims);
static const struct SpriteTemplate sCraftLeftTemplate = SPACE_TEMPLATE(TAG_SPACE_CRAFT, &sPairOam, sCraftLeftAnims);
static const struct SpriteTemplate sCraftRightTemplate = SPACE_TEMPLATE(TAG_SPACE_CRAFT, &sPairOam, sCraftRightAnims);
static const struct SpriteTemplate sGearTemplate = SPACE_TEMPLATE(TAG_SPACE_CRAFT, &sGearOam, sGearAnims);
static const struct SpriteTemplate sEffectTemplate = SPACE_TEMPLATE(TAG_SPACE_EXHAUST, &sEffectOam, sEffectAnims);
struct SpaceMotionKey
{
    u16 frame;
    s16 x, y, angle;
    u16 inverseScale;
    u8 pose, visible;
};

struct SpaceMotionSample
{
    s16 x, y, angle;
    u16 inverseScale;
    u8 pose, visible;
};

struct SpaceMotionPair
{
    u8 first, second, matrix;
    bool8 horizontal;
};

static const s8 sCraftLocalPoseY[] = {0, 3, 5};
#define SPACE_CRAFT_ORIGIN_Y 40

static const struct SpaceMotionKey sOutbound_main_tank[] =
{
    {0, 110, 88, 0, 256, 0, TRUE},
    {120, 110, 88, 0, 256, 0, TRUE},
    {360, 105, 66, 0, 256, 0, TRUE},
    {480, 105, 62, 0, 256, 0, TRUE},
    {720, 105, 54, 0, 256, 0, TRUE},
    {839, 88, 196, 0, 288, 0, TRUE},
    {840, 88, 196, 0, 288, 0, FALSE},
    {1800, 88, 196, 0, 288, 0, FALSE},
};

static const struct SpaceMotionKey sOutbound_srb_left[] =
{
    {0, 92, 94, 0, 320, 0, TRUE},
    {120, 92, 94, 0, 320, 0, TRUE},
    {360, 87, 72, 0, 320, 0, TRUE},
    {479, 46, 194, -8, 352, 0, TRUE},
    {480, 46, 194, -8, 352, 0, FALSE},
    {1800, 46, 194, -8, 352, 0, FALSE},
};

static const struct SpaceMotionKey sOutbound_srb_right[] =
{
    {0, 128, 94, 0, 320, 0, TRUE},
    {120, 128, 94, 0, 320, 0, TRUE},
    {360, 123, 72, 0, 320, 0, TRUE},
    {479, 173, 194, 8, 352, 0, TRUE},
    {480, 173, 194, 8, 352, 0, FALSE},
    {1800, 173, 194, 8, 352, 0, FALSE},
};

static const struct SpaceMotionKey sOutbound_passenger[] =
{
    {0, 84, 88, 192, 320, 0, TRUE},
    {120, 84, 88, 192, 320, 0, TRUE},
    {360, 79, 66, 192, 320, 0, TRUE},
    {480, 79, 62, 192, 320, 0, TRUE},
    {720, 79, 54, 192, 320, 0, TRUE},
    {840, 79, 54, 192, 320, 0, TRUE},
    {1020, 102, 76, 256, 384, 0, TRUE},
    {1110, 114, 76, 256, 384, 0, TRUE},
    {1140, 118, 73, 253, 384, 1, TRUE},
    {1260, 142, 58, 256, 384, 1, TRUE},
    {1290, 142, 58, 258, 384, 2, TRUE},
    {1380, 120, 66, 256, 384, 0, TRUE},
    {1410, 117, 69, 259, 384, 2, TRUE},
    {1530, 100, 84, 256, 384, 2, TRUE},
    {1560, 100, 84, 253, 384, 1, TRUE},
    {1620, 112, 76, 256, 384, 0, TRUE},
    {1800, 112, 76, 256, 384, 0, TRUE},
};

static const struct SpaceMotionKey sReturn_main_tank[] =
{
    {0, 0, 0, 0, 256, 0, FALSE},
    {1440, 0, 0, 0, 256, 0, FALSE},
};

static const struct SpaceMotionKey sReturn_srb_left[] =
{
    {0, 0, 0, 0, 256, 0, FALSE},
    {1440, 0, 0, 0, 256, 0, FALSE},
};

static const struct SpaceMotionKey sReturn_srb_right[] =
{
    {0, 0, 0, 0, 256, 0, FALSE},
    {1440, 0, 0, 0, 256, 0, FALSE},
};

static const struct SpaceMotionKey sReturn_passenger[] =
{
    {0, 112, 76, 256, 384, 0, TRUE},
    {300, 116, 72, 260, 384, 0, TRUE},
    {660, 112, 82, 264, 352, 0, TRUE},
    {900, 108, 94, 262, 320, 0, TRUE},
    {1020, 112, 106, 258, 288, 0, TRUE},
    {1100, 118, 119, 252, 272, 0, TRUE},
    {1140, 122, 128, 252, 256, 0, TRUE},
    {1200, 128, 128, 252, 256, 0, TRUE},
    {1320, 135, 128, 256, 256, 0, TRUE},
    {1440, 138, 128, 256, 256, 0, TRUE},
};

static s16 SpaceMotion_Lerp(s16 a, s16 b, u16 weight)
{
    return a + ((s32)(b - a) * weight) / 256;
}

static void SpaceMotion_Sample(const struct SpaceMotionKey *keys, u16 count,
                              u16 frame, struct SpaceMotionSample *out)
{
    const struct SpaceMotionKey *a = keys;
    const struct SpaceMotionKey *b;
    u16 u, weight;
    u16 i;
    for (i = 1; i < count && frame >= keys[i].frame; i++)
        a = &keys[i];
    *out = (struct SpaceMotionSample){a->x, a->y, a->angle,
                                     a->inverseScale, a->pose, a->visible};
    if (i == count || frame <= a->frame)
        return;
    b = &keys[i];
    u = (u32)(frame - a->frame) * 256 / (b->frame - a->frame);
    // Max numerator 16,777,216 fitsu32. Do not replace by overflowing Q12 cubics.
    weight = ((u32)u * u * (768 - 2 * u) + 32768) >> 16;
    out->x = SpaceMotion_Lerp(a->x, b->x, weight);
    out->y = SpaceMotion_Lerp(a->y, b->y, weight);
    out->angle = SpaceMotion_Lerp(a->angle, b->angle, weight);
    out->inverseScale = SpaceMotion_Lerp(a->inverseScale, b->inverseScale, weight);
}

static void SpaceMotion_ApplyPair(const struct SpaceMotionPair *pair,
                                 const struct SpaceMotionSample *sample)
{
    struct Sprite *first = &gSprites[pair->first];
    struct Sprite *second = &gSprites[pair->second];
    u8 angle = sample->angle;
    s16 separation, firstOffset, secondOffset, localY = 0;
    first->invisible = second->invisible = !sample->visible;
    if (!sample->visible)
        return;
    // Raw inverse coefficient avoids the prior ConvertScaleParam reciprocal bug.
    SetOamMatrix(pair->matrix, Cos(angle, sample->inverseScale),
                 Sin(angle, sample->inverseScale),
                 -Sin(angle, sample->inverseScale), Cos(angle, sample->inverseScale));
    separation = (64 * 256 + sample->inverseScale / 2) / sample->inverseScale;
    firstOffset = -(separation / 2);
    secondOffset = firstOffset + separation;
    if (pair->horizontal)
    {
        // Midbody anchor from neutralframe, corrected pose offset before rotation.
        localY = (s32)(32 - SPACE_CRAFT_ORIGIN_Y + sCraftLocalPoseY[sample->pose])
                 * 256 / sample->inverseScale;
        first->x = sample->x + Cos(angle, firstOffset) - Sin(angle, localY);
        first->y = sample->y + Sin(angle, firstOffset) + Cos(angle, localY);
        second->x = sample->x + Cos(angle, secondOffset) - Sin(angle, localY);
        second->y = sample->y + Sin(angle, secondOffset) + Cos(angle, localY);
        // Separate left/right templates both have threeanims:
        // left offsets 0/128/256, right offsets64/192/320.
        if (first->animNum != sample->pose)
            StartSpriteAnim(first, sample->pose);
        if (second->animNum != sample->pose)
            StartSpriteAnim(second, sample->pose);
    }
    else
    {
        // Original launcher canvas is upright. Its native angle0 remains upright.
        first->x = sample->x - Sin(angle, firstOffset);
        first->y = sample->y + Cos(angle, firstOffset);
        second->x = sample->x - Sin(angle, secondOffset);
        second->y = sample->y + Cos(angle, secondOffset);
    }
}


struct SpaceOwnedResources
{
    u32 matrixMask;
    u8 sprites[14];
    u8 spriteCount;
    u8 loadedSheets, loadedPalettes;
};
struct SpaceFlight
{
    u16 tilemaps[4][32 * 32];
    struct SpaceOwnedResources owned;
    struct SpaceMotionPair units[SPACE_UNIT_COUNT];
    u8 effectSprites[SPACE_EFFECT_COUNT];
    u8 effectMatrices[SPACE_EFFECT_COUNT];
    bool8 spaceBackground;
    u8 gearSprites[SPACE_GEAR_COUNT];
};
typedef char SpaceFlightHeapBudget[(sizeof(struct SpaceFlight) <= 0x2200) ? 1 : -1];
typedef char SpaceSpriteTileBudget[((sizeof(sTankTiles) + sizeof(sBoosterTiles) * 2 + sizeof(sCraftTiles) + sizeof(sExhaustTiles)) <= 0x8000) ? 1 : -1];

static void CB2_SpaceFlightSetup(void);
static void Task_SpaceFlight(u8 taskId);

void HoennSpaceStory_GetPhase(void)
{
    u16 phase = VarGet(VAR_HOENN_SPACE_MISSION_PHASE);
    // The last scene has reloaded the real save; recorded playback is separate.
    if (gQuestLogState == QL_STATE_PLAYBACK)
    {
        gSpecialVar_Result = 0xFFFF;
        return;
    }
    gSpecialVar_Result = phase <= SPACE_MISSION_REPORTED ? phase : SPACE_MISSION_NOT_STARTED;
}

static bool8 SpaceMonIsJirachi(const struct BoxPokemon *source)
{
    struct BoxPokemon copy;

    if (source == NULL)
        return FALSE;
    // Validate a copy: the normal data reader marks invalid checksums as eggs.
    // Checking mission eligibility must not change the stored creature.
    copy = *source;
    return GetBoxMonData(&copy, MON_DATA_SPECIES_OR_EGG) == SPECIES_JIRACHI;
}

void HoennSpaceStory_CheckJirachiCaught(void)
{
    u8 i, box, slot;

    gSpecialVar_Result = TRUE;
    if (FlagGet(FLAG_HOENN_SPACE_JIRACHI_CAUGHT)
     || GetSetPokedexFlag(SpeciesToNationalPokedexNum(SPECIES_JIRACHI), FLAG_GET_CAUGHT))
        return;
    for (i = 0; i < gPlayerPartyCount && i < PARTY_SIZE; i++)
    {
        if (SpaceMonIsJirachi(&gPlayerParty[i].box))
            return;
    }
    // Use the storage API so the additional fourteen boxes are checked too.
    // SPECIES_OR_EGG excludes eggs and corrupted creatures from ownership.
    for (box = 0; box < TOTAL_BOXES_COUNT; box++)
    {
        for (slot = 0; slot < IN_BOX_COUNT; slot++)
        {
            if (SpaceMonIsJirachi(GetBoxedMonPtr(box, slot)))
                return;
        }
    }
    gSpecialVar_Result = FALSE;
}

void HoennSpaceStory_PlayFlight(void)
{
    gSpecialVar_Result = FALSE;
    if (gQuestLogState == QL_STATE_PLAYBACK || gQuestLogState == QL_STATE_PLAYBACK_LAST)
        return;
    if (!FlagGet(FLAG_HOENN_SPACE_CENTER_SECURED) || !FlagGet(FLAG_HOENN_SPACE_MISSION_ENROLLED))
        return;
    if (gSpecialVar_0x8004 == 0)
    {
        if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_HOENN_SPACEPORT_LAUNCH_PAD)
         || gSaveBlock1Ptr->location.mapNum != MAP_NUM(MAP_HOENN_SPACEPORT_LAUNCH_PAD))
            return;
    }
    else if (gSpecialVar_0x8004 != 1
          || gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_HOENN_SPACECRAFT_CABIN)
          || gSaveBlock1Ptr->location.mapNum != MAP_NUM(MAP_HOENN_SPACECRAFT_CABIN))
    {
        return;
    }
    gSpecialVar_Result = TRUE;
    gMain.state = 0;
    SetVBlankCallback(NULL);
    SetMainCallback1(NULL);
    HelpSystem_Disable();
    SetMainCallback2(CB2_SpaceFlightSetup);
}

static void SpaceFlightVBlank(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void SpaceFlightMain(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void WarpFromSpaceScene(bool8 returning, bool8 complete)
{
    if (complete)
    {
        if (FlagGet(FLAG_HOENN_SPACE_MISSION_REPORTED))
            VarSet(VAR_HOENN_SPACE_MISSION_PHASE, SPACE_MISSION_REPORTED);
        else if (returning)
            VarSet(VAR_HOENN_SPACE_MISSION_PHASE, FlagGet(FLAG_HOENN_SPACE_RECORDS_RECOVERED)
                   ? SPACE_MISSION_LANDED : SPACE_MISSION_BOARDING);
        else
            VarSet(VAR_HOENN_SPACE_MISSION_PHASE, FlagGet(FLAG_HOENN_SPACE_RECORDS_RECOVERED)
                   ? SPACE_MISSION_RECORDS_READY : FlagGet(FLAG_HOENN_SPACE_SYSTEMS_SECURED)
                   ? SPACE_MISSION_SYSTEMS_READY : SPACE_MISSION_IN_FLIGHT);
    }
    if (returning || !complete)
        SetWarpDestination(MAP_GROUP(MAP_HOENN_SPACEPORT_LAUNCH_PAD), MAP_NUM(MAP_HOENN_SPACEPORT_LAUNCH_PAD), -1, 15, 18);
    else
        SetWarpDestination(MAP_GROUP(MAP_HOENN_SPACECRAFT_CABIN), MAP_NUM(MAP_HOENN_SPACECRAFT_CABIN), -1, 10, 12);
    HelpSystem_Enable();
    ResetInitialPlayerAvatarState();
    gFieldCallback = FieldCB_DefaultWarpExit;
    WarpIntoMap();
    SetMainCallback2(CB2_LoadMap);
}

static void SpaceSceneCleanup(u8 taskId, bool8 complete)
{
    struct Task *task = &gTasks[taskId];
    struct SpaceFlight *scene = (struct SpaceFlight *)GetWordTaskArg(taskId, FLIGHT_RESOURCE_ARG);
    bool8 returning = task->tReturning;
    u8 i;
    SetVBlankCallback(NULL);
    for (i = 0; i < scene->owned.spriteCount; i++)
        DestroySprite(&gSprites[scene->owned.sprites[i]]);
    for (i = 0; i < 32; i++)
        if (scene->owned.matrixMask & (1u << i))
            FreeOamMatrix(i);
    scene->owned.matrixMask = 0;
    for (i = 0; i < ARRAY_COUNT(sUnitSheets); i++)
    {
        if (scene->owned.loadedSheets & (1u << i))
            FreeSpriteTilesByTag(sUnitSheets[i].tag);
        if (scene->owned.loadedPalettes & (1u << i))
            FreeSpritePaletteByTag(sUnitPalettes[i].tag);
    }
    for (i = 1; i <= 3; i++)
        UnsetBgTilemapBuffer(i);
    Free(scene);
    DestroyTask(taskId);
    WarpFromSpaceScene(returning, complete);
}

static u8 SpaceCreateOwnedSprite(struct SpaceFlight *scene, const struct SpriteTemplate *template)
{
    u8 id;
    if (scene->owned.spriteCount >= ARRAY_COUNT(scene->owned.sprites))
        return MAX_SPRITES; // Guard BEFORE creation: no untracked sprite on failure.
    id = CreateSprite(template, 0, 0, 1);
    if (id != MAX_SPRITES)
    {
        scene->owned.sprites[scene->owned.spriteCount++] = id;
        gSprites[id].invisible = TRUE;
    }
    return id;
}

static u8 SpaceOwnMatrix(struct SpaceFlight *scene)
{
    u8 matrix = AllocOamMatrix();
    if (matrix != 0xFF)
        scene->owned.matrixMask |= 1u << matrix;
    return matrix;
}

static void SpaceAttachMatrix(u8 id, u8 matrix)
{
    struct Sprite *sprite = &gSprites[id];
    sprite->oam.affineMode = ST_OAM_AFFINE_NORMAL;
    sprite->oam.matrixNum = matrix;
    CalcCenterToCornerVec(sprite, sprite->oam.shape, sprite->oam.size, sprite->oam.affineMode);
    // Manual matrices only. No native affine animation owns this matrix.
    sprite->affineAnimBeginning = FALSE;
    sprite->affineAnimPaused = TRUE;
}


static void SpaceSetPairBounds(const struct SpaceMotionPair *pair, u8 mode)
{
    struct Sprite *first = &gSprites[pair->first];
    struct Sprite *second = &gSprites[pair->second];
    // Identity-only ordinary OBJ: no rotation/scale, same center and pixels.
    // Restore the owned matrix number when affine rendering resumes.
    first->oam.matrixNum = second->oam.matrixNum = mode == ST_OAM_AFFINE_OFF ? 0 : pair->matrix;
    if (mode == ST_OAM_AFFINE_OFF)
    {
        first->hFlip = first->vFlip = FALSE;
        second->hFlip = second->vFlip = FALSE;
    }
    if (first->oam.affineMode != mode)
    {
        first->oam.affineMode = mode;
        CalcCenterToCornerVec(first, first->oam.shape, first->oam.size, mode);
    }
    if (second->oam.affineMode != mode)
    {
        second->oam.affineMode = mode;
        CalcCenterToCornerVec(second, second->oam.shape, second->oam.size, mode);
    }
}

static bool8 SpaceCreatePair(struct SpaceFlight *scene, u8 unit,
                            const struct SpriteTemplate *first,
                            const struct SpriteTemplate *second, bool8 horizontal)
{
    struct SpaceMotionPair *pair = &scene->units[unit];
    pair->matrix = SpaceOwnMatrix(scene);
    if (pair->matrix == 0xFF)
        return FALSE;
    pair->first = SpaceCreateOwnedSprite(scene, first);
    if (pair->first == MAX_SPRITES)
        return FALSE;
    pair->second = SpaceCreateOwnedSprite(scene, second);
    if (pair->second == MAX_SPRITES)
        return FALSE;
    pair->horizontal = horizontal;
    SpaceAttachMatrix(pair->first, pair->matrix);
    SpaceAttachMatrix(pair->second, pair->matrix);
    if (!horizontal)
        StartSpriteAnim(&gSprites[pair->second], 1);
    return TRUE;
}

static bool8 SpaceLoadActors(struct SpaceFlight *scene)
{
    u8 i;
    for (i = 0; i < ARRAY_COUNT(sUnitSheets); i++)
    {
        LoadSpriteSheet(&sUnitSheets[i]);
        if (GetSpriteTileStartByTag(sUnitSheets[i].tag) == 0xFFFF)
            return FALSE;
        scene->owned.loadedSheets |= 1u << i;
        LoadSpritePalette(&sUnitPalettes[i]);
        if (IndexOfSpritePaletteTag(sUnitPalettes[i].tag) == 0xFF)
            return FALSE;
        scene->owned.loadedPalettes |= 1u << i;
    }
    if (!SpaceCreatePair(scene, UNIT_TANK, &sTankTemplate, &sTankTemplate, FALSE)
     || !SpaceCreatePair(scene, UNIT_SRB_LEFT, &sLeftSrbTemplate, &sLeftSrbTemplate, FALSE)
     || !SpaceCreatePair(scene, UNIT_SRB_RIGHT, &sRightSrbTemplate, &sRightSrbTemplate, FALSE)
     || !SpaceCreatePair(scene, UNIT_CRAFT, &sCraftLeftTemplate, &sCraftRightTemplate, TRUE))
        return FALSE;
    // Keep both orbiter halves in front of the attached tank/SRB assembly.
    // Explicit subpriority avoids Y sorting hiding the fuselage or a wing.
    gSprites[scene->units[UNIT_CRAFT].first].subpriority = 0;
    gSprites[scene->units[UNIT_CRAFT].second].subpriority = 0;
    for (i = 0; i < SPACE_GEAR_COUNT; i++)
    {
        u8 id = SpaceCreateOwnedSprite(scene, &sGearTemplate);
        if (id == MAX_SPRITES)
            return FALSE;
        scene->gearSprites[i] = id;
        SpaceAttachMatrix(id, scene->units[UNIT_CRAFT].matrix);
        // Same-priority sprites are Y-sorted. Keep gear behind craft0 explicitly.
        gSprites[id].subpriority = 1;
        gSprites[id].oam.affineMode = ST_OAM_AFFINE_DOUBLE;
        CalcCenterToCornerVec(&gSprites[id], gSprites[id].oam.shape,
                              gSprites[id].oam.size, ST_OAM_AFFINE_DOUBLE);
    }
    for (i = 0; i < SPACE_EFFECT_COUNT; i++)
    {
        scene->effectMatrices[i] = SpaceOwnMatrix(scene);
        if (scene->effectMatrices[i] == 0xFF)
            return FALSE;
        scene->effectSprites[i] = SpaceCreateOwnedSprite(scene, &sEffectTemplate);
        if (scene->effectSprites[i] == MAX_SPRITES)
            return FALSE;
        SpaceAttachMatrix(scene->effectSprites[i], scene->effectMatrices[i]);
    }
    return TRUE;
}

static void ShowSpaceBackground(struct SpaceFlight *scene, bool8 returning, u16 frame)
{
    u16 center = returning ? 660 : 600;
    u16 start = center - SPACE_TRANSITION_HALF;
    u16 end = center + SPACE_TRANSITION_HALF;
    u16 mix;
    SetBgAttribute(3, BG_ATTR_PRIORITY, 2);
    if (!returning && frame >= start - SPACE_TRANSITION_HALF && frame < start)
    {
        // Dissolve the independently-scrolling clouds before hiding BG2.
        // BG1 is solid high-altitude sky throughout this lead-in interval.
        mix = (frame - (start - SPACE_TRANSITION_HALF)) * 16 / SPACE_TRANSITION_HALF;
        HideBg(3);
        ShowBg(1);
        ShowBg(2);
        SetGpuReg(REG_OFFSET_BLDCNT,
                  BLDCNT_TGT1_BG2 | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_BG1);
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(16 - mix, mix));
    }
    else if (frame < start)
    {
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        HideBg(returning ? 1 : 3);
        if (returning || frame < 240)
            HideBg(2);
        else
            ShowBg(2);
        ShowBg(returning ? 3 : 1);
    }
    else if (frame < end)
    {
        mix = (frame - start) * 16 / (end - start);
        // SetBgAttribute changes RAM only; ShowBg commits the BG control register.
        if (returning)
            SetBgAttribute(3, BG_ATTR_PRIORITY, 0);
        ShowBg(3);
        if (returning)
        {
            // Earth blends over the complete destination: runway or sky.
            ShowBg(1);
            ShowBg(2);
            SetGpuReg(REG_OFFSET_BLDCNT,
                      BLDCNT_TGT1_BG3 | BLDCNT_EFFECT_BLEND
                    | BLDCNT_TGT2_BG1 | BLDCNT_TGT2_BG2);
        }
        else
        {
            HideBg(2);
            ShowBg(1);
            SetGpuReg(REG_OFFSET_BLDCNT,
                      BLDCNT_TGT1_BG1 | BLDCNT_EFFECT_BLEND | BLDCNT_TGT2_BG3);
        }
        // Only BG targets blend. Craft/gear/effect OBJ palettes stay unchanged.
        SetGpuReg(REG_OFFSET_BLDALPHA, BLDALPHA_BLEND(16 - mix, mix));
    }
    else
    {
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        HideBg(returning ? 3 : 1);
        if (returning)
            ShowBg(2);
        else
            HideBg(2);
        ShowBg(returning ? 1 : 3);
    }
    scene->spaceBackground = returning ? frame < center : frame >= center;
}

static void SpacePlaceGear(struct SpaceFlight *scene,
                           const struct SpaceMotionSample *craft,
                           bool8 returning, u16 frame)
{
    static const s8 xOffsets[SPACE_GEAR_COUNT] = {-10, 31};
    u16 deploy = frame < 1020 ? 0 : frame < 1080 ? frame - 1020 : 60;
    s16 localY = (2 + deploy * 8 / 60) * 256 / craft->inverseScale;
    u8 i, angle = craft->angle;
    for (i = 0; i < SPACE_GEAR_COUNT; i++)
    {
        struct Sprite *sprite = &gSprites[scene->gearSprites[i]];
        s16 localX = xOffsets[i] * 256 / craft->inverseScale;
        sprite->invisible = !returning || frame < 1020 || !craft->visible;
        if (sprite->invisible)
            continue;
        sprite->x = craft->x + Cos(angle, localX) - Sin(angle, localY);
        sprite->y = craft->y + Sin(angle, localX) + Cos(angle, localY);
        // Existing craft matrix is shared; no new affine ownership is allocated.
    }
}

static void SpaceSampleAll(bool8 returning, u16 frame, struct SpaceMotionSample *samples)
{
    if (returning)
    {
        SpaceMotion_Sample(sReturn_main_tank, ARRAY_COUNT(sReturn_main_tank), frame, &samples[UNIT_TANK]);
        SpaceMotion_Sample(sReturn_srb_left, ARRAY_COUNT(sReturn_srb_left), frame, &samples[UNIT_SRB_LEFT]);
        SpaceMotion_Sample(sReturn_srb_right, ARRAY_COUNT(sReturn_srb_right), frame, &samples[UNIT_SRB_RIGHT]);
        SpaceMotion_Sample(sReturn_passenger, ARRAY_COUNT(sReturn_passenger), frame, &samples[UNIT_CRAFT]);
        if (frame >= 1140)
        {
            u16 rollout = frame - 1140;
            if (rollout > 300)
                rollout = 300;
            // Main gear touches first with the nose raised. A bounded 16px
            // rollout slows to rest; the native finite runway never scrolls X.
            samples[UNIT_CRAFT].x = 122 + ((u32)16 * rollout * (600 - rollout) + 45000) / 90000;
        }
    }
    else
    {
        SpaceMotion_Sample(sOutbound_main_tank, ARRAY_COUNT(sOutbound_main_tank), frame, &samples[UNIT_TANK]);
        SpaceMotion_Sample(sOutbound_srb_left, ARRAY_COUNT(sOutbound_srb_left), frame, &samples[UNIT_SRB_LEFT]);
        SpaceMotion_Sample(sOutbound_srb_right, ARRAY_COUNT(sOutbound_srb_right), frame, &samples[UNIT_SRB_RIGHT]);
        SpaceMotion_Sample(sOutbound_passenger, ARRAY_COUNT(sOutbound_passenger), frame, &samples[UNIT_CRAFT]);
    }
}

static const u16 sOutboundRcs[][2] =
{
    {840, 844},
    {900, 904},
    {960, 964},
    {1110, 1114},
    {1134, 1138},
    {1260, 1264},
    {1284, 1288},
    {1380, 1384},
    {1404, 1408},
    {1530, 1534},
    {1554, 1558},
};

static const u16 sReturnRcs[][2] =
{
    {0, 4},
    {60, 64},
    {120, 124},
};

static bool8 SpaceRcsActive(bool8 returning, u16 frame)
{
    const u16 (*ranges)[2] = returning ? sReturnRcs : sOutboundRcs;
    u8 count = returning ? ARRAY_COUNT(sReturnRcs) : ARRAY_COUNT(sOutboundRcs);
    u8 i;
    for (i = 0; i < count; i++)
        if (ranges[i][0] <= frame && frame < ranges[i][1])
            return TRUE;
    return FALSE;
}

static void SpacePlaceEffect(struct SpaceFlight *scene, u8 effect,
                             const struct SpaceMotionSample *unit,
                             s16 localX, s16 localY, s16 angle, u16 scale, bool8 visible)
{
    struct Sprite *sprite = &gSprites[scene->effectSprites[effect]];
    u8 heading = (u8)unit->angle;
    u8 effectAngle = (u8)angle;
    sprite->invisible = !visible || !unit->visible;
    if (sprite->invisible)
        return;
    localX = (s32)localX * 256 / unit->inverseScale;
    localY = (s32)localY * 256 / unit->inverseScale;
    sprite->x = unit->x + Cos(heading, localX) - Sin(heading, localY);
    sprite->y = unit->y + Sin(heading, localX) + Cos(heading, localY);
    SetOamMatrix(scene->effectMatrices[effect], Cos(effectAngle, scale), Sin(effectAngle, scale),
                 -Sin(effectAngle, scale), Cos(effectAngle, scale));
}

static void RenderSpaceFrame(struct SpaceFlight *scene, bool8 returning, u16 frame)
{
    struct SpaceMotionSample units[SPACE_UNIT_COUNT];
    u8 i;
    SpaceSampleAll(returning, frame, units);
    for (i = 0; i < SPACE_UNIT_COUNT; i++)
    {
        u8 mode = ST_OAM_AFFINE_NORMAL;
        // Tank alone has an exact identity transform during the early launch.
        // Ordinary OBJ costs less than affine; keep all other poses untouched.
        if (i == UNIT_TANK && (u8)units[i].angle == 0 && units[i].inverseScale == 256)
            mode = ST_OAM_AFFINE_OFF;
        else if (i == UNIT_CRAFT && (returning || frame >= 840))
            mode = ST_OAM_AFFINE_DOUBLE;
        SpaceSetPairBounds(&scene->units[i], mode);
        SpaceMotion_ApplyPair(&scene->units[i], &units[i]);
    }
    SpacePlaceGear(scene, &units[UNIT_CRAFT], returning, frame);
    ShowSpaceBackground(scene, returning, frame);
    ChangeBgX(3, 0, BG_COORD_SET);
    ChangeBgY(3, 0, BG_COORD_SET);
    if (!returning)
    {
        ChangeBgY(1, -(s32)(frame > 120 ? frame - 120 : 0) * 96, BG_COORD_SET);
        ChangeBgY(2, -(s32)frame * 192, BG_COORD_SET);
        ChangeBgX(2, (s32)frame * 32, BG_COORD_SET);
    }
    else
    {
        // Clamp before660: the blended approach must not underflow a u16.
        u16 descent = frame <= 660 ? 0 : frame < 1020 ? frame - 660 : 360;
        ChangeBgX(1, 0, BG_COORD_SET);
        ChangeBgY(1, (s32)descent * 90 * 256 / 360, BG_COORD_SET);
        ChangeBgX(2, 0, BG_COORD_SET);
        ChangeBgY(2, 0, BG_COORD_SET);
    }
    // Main enginethrust is separate from smallattitude pulses.
    // OMS engines in the reference video are NOT claimed to beRCS footage.
    SpacePlaceEffect(scene, EFFECT_MAIN, &units[UNIT_CRAFT], -64, 0,
                     units[UNIT_CRAFT].angle + 64, 256,
                     !returning && frame >= 30 && frame < 720 && (frame & 7) != 0);
    SpacePlaceEffect(scene, EFFECT_SRB_LEFT, &units[UNIT_SRB_LEFT], 0, 64,
                     0, 320, !returning && frame >= 30 && frame < 360 && (frame & 7) != 0);
    SpacePlaceEffect(scene, EFFECT_SRB_RIGHT, &units[UNIT_SRB_RIGHT], 0, 64,
                     0, 320, !returning && frame >= 30 && frame < 360 && (frame & 7) != 0);
    // Small aft pulse: source(24,32) relative to craft origin(64,40).
    // Rotate the exhaust to trail aft rather than forming a candle at the nose.
    SpacePlaceEffect(scene, EFFECT_RCS, &units[UNIT_CRAFT], -40, -8,
                     units[UNIT_CRAFT].angle + 64, 1280, SpaceRcsActive(returning, frame));
}

static void CB2_SpaceFlightSetup(void)
{
    u8 i, taskId;
    u16 tile;
    struct SpaceFlight *scene;
    struct Task *task;
    if (gMain.state == 0)
    {
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 0);
        CleanupOverworldWindowsAndTilemaps();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        ResetPaletteFade();
        FreeAllSpritePalettes();
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, (void *)OAM, OAM_SIZE);
        scene = AllocZeroed(sizeof(*scene));
        if (scene == NULL)
        {
            WarpFromSpaceScene(TRUE, FALSE);
            return;
        }
        taskId = CreateTask(Task_SpaceFlight, 8);
        if (taskId == TASK_NONE)
        {
            Free(scene);
            WarpFromSpaceScene(TRUE, FALSE);
            return;
        }
        SetWordTaskArg(taskId, FLIGHT_RESOURCE_ARG, (u32)scene);
        task = &gTasks[taskId];
        task->tReturning = gSpecialVar_0x8004 == 1;
        task->tState = SCENE_RUNNING;
        scene->spaceBackground = task->tReturning;
        gMain.state++;
        return;
    }
    taskId = FindTaskIdByFunc(Task_SpaceFlight);
    if (taskId == TASK_NONE)
    {
        WarpFromSpaceScene(TRUE, FALSE);
        return;
    }
    task = &gTasks[taskId];
    scene = (struct SpaceFlight *)GetWordTaskArg(taskId, FLIGHT_RESOURCE_ARG);
    switch (gMain.state)
    {
    case 1:
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sSpaceBgTemplates, ARRAY_COUNT(sSpaceBgTemplates));
        for (i = 0; i < 3; i++)
        {
            SetBgTilemapBuffer(i + 1, scene->tilemaps[i == 0 ? 0 : i + 1]);
            ChangeBgX(i + 1, 0, BG_COORD_SET);
            ChangeBgY(i + 1, 0, BG_COORD_SET);
        }
        // Ground0..0x4600; BG2 char1+tile48 starts0x4600; Earth char2
        // occupies0x8000..0xC860. No live background is replaced in flight.
        LoadBgTiles(1, task->tReturning ? sRunwayTiles : sGroundTiles,
                    task->tReturning ? sizeof(sRunwayTiles) : sizeof(sGroundTiles), 0);
        LoadBgTiles(2, task->tReturning ? sLandingSkyTiles : sCloudTiles,
                    task->tReturning ? sizeof(sLandingSkyTiles) : sizeof(sCloudTiles), SPACE_CLOUD_BASE_TILE);
        LoadBgTiles(3, sEarthTiles, sizeof(sEarthTiles), 0);
        CopyToBgTilemapBuffer(1, task->tReturning ? sRunwayMap : sGroundMap,
                              task->tReturning ? sizeof(sRunwayMap) : sizeof(sGroundMap), 0);
        CopyToBgTilemapBuffer(2, task->tReturning ? sLandingSkyMap : sCloudMap,
                              task->tReturning ? sizeof(sLandingSkyMap) : sizeof(sCloudMap), 0);
        // Rebase only tile indices; retain each map entry's flip/palette bits.
        for (tile = 0; tile < 32 * 32; tile++)
            scene->tilemaps[2][tile] = (scene->tilemaps[2][tile] & 0xFC00)
                                   | ((scene->tilemaps[2][tile] & 0x03FF) + SPACE_CLOUD_BASE_TILE);
        if (task->tReturning)
        {
            SetBgAttribute(2, BG_ATTR_PRIORITY, 3);
            // Original runway uses bank2; keep Earth2 resident and use bank3.
            for (tile = 0; tile < 32 * 32; tile++)
                scene->tilemaps[0][tile] = (scene->tilemaps[0][tile] & 0x0FFF)
                                       | (SPACE_RUNWAY_PALETTE << 12);
        }
        CopyToBgTilemapBuffer(3, sEarthMap, sizeof(sEarthMap), 0);
        LoadPalette(task->tReturning ? sLandingSkyPalette : sGroundPalette,
                    BG_PLTT_ID(0), PLTT_SIZE_4BPP);
        LoadPalette(sCloudPalette, BG_PLTT_ID(1), PLTT_SIZE_4BPP);
        LoadPalette(sEarthPalette, BG_PLTT_ID(2), PLTT_SIZE_4BPP);
        if (task->tReturning)
            LoadPalette(sRunwayPalette, BG_PLTT_ID(SPACE_RUNWAY_PALETTE), PLTT_SIZE_4BPP);
        gMain.state++;
        break;
    case 2:
        if (IsDma3ManagerBusyWithBgCopy())
            break;
        if (!SpaceLoadActors(scene))
        {
            // No heap-backed mapcopy has beenqueued yet on thisfailurepath.
            SpaceSceneCleanup(taskId, FALSE);
            return;
        }
        // Only successful setup may enqueue scene->tilemaps. No allocation or
        // actorcreation failure path remains after thispoint.
        for (i = 1; i <= 3; i++)
            CopyBgTilemapBufferToVram(i);
        RenderSpaceFrame(scene, task->tReturning, 0);
        BlendPalettes(PALETTES_ALL, 16, RGB_BLACK);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_MODE_0 | DISPCNT_OBJ_1D_MAP | DISPCNT_OBJ_ON);
        ShowBg(task->tReturning ? 3 : 1);
        SetVBlankCallback(SpaceFlightVBlank);
        PlayBGM(MUS_SILPH);
        SetMainCallback2(SpaceFlightMain);
        gMain.state = 0;
        break;
    }
}

static void Task_SpaceFlight(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    struct SpaceFlight *scene = (struct SpaceFlight *)GetWordTaskArg(taskId, FLIGHT_RESOURCE_ARG);
    if (task->tState == SCENE_RUNNING)
    {
        u16 length = task->tReturning ? SPACE_RETURN_FRAMES : SPACE_OUTBOUND_FRAMES;
        if (task->tFrame == 0 && gPaletteFade.active)
            return;
        RenderSpaceFrame(scene, task->tReturning, task->tFrame);
        if (!task->tReturning && (task->tFrame == 30 || task->tFrame == 120))
            PlaySE(SE_M_FIRE_PUNCH);
        if (!task->tReturning && (task->tFrame == 360 || task->tFrame == 720 || task->tFrame == 840))
            PlaySE(SE_M_FLY);
        task->tFrame++;
        if (task->tFrame >= length)
        {
            task->tState = SCENE_FADE_OUT;
            task->tFrame = 0;
        }
    }
    else if (task->tState == SCENE_FADE_OUT)
    {
        if (task->tFrame++ == 0)
        {
            Overworld_FadeOutMapMusic();
            BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        }
        else if (!gPaletteFade.active)
            task->tState = SCENE_EXIT;
    }
    else
    {
        SpaceSceneCleanup(taskId, TRUE);
    }
}

static const u32 sSpaceportTiles[] = INCBIN_U32("data/tilesets/secondary/ty_spaceport/tiles.4bpp");
static const u16 sSpaceportPalettes[][16] = INCBIN_U16("data/tilesets/secondary/ty_spaceport/palettes.gbapal");
static const u16 sSpaceportMetatiles[] = INCBIN_U16("data/tilesets/secondary/ty_spaceport/metatiles.bin");
static const u32 sSpaceportAttributes[] = INCBIN_U32("data/tilesets/secondary/ty_spaceport/metatile_attributes.bin");
const struct Tileset gTileset_HoennSpaceport =
{
    .isCompressed = FALSE, .isSecondary = TRUE, .isEmerald = TRUE,
    .tiles = sSpaceportTiles, .palettes = sSpaceportPalettes,
    .metatiles = sSpaceportMetatiles, .metatileAttributes = sSpaceportAttributes,
    .callback = NULL,
};

#include "data/tilesets/ty_space_style_v2.h"
