#include "global.h"
#include "battle_setup.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "field_player_avatar.h"
#include "fieldmap.h"
#include "hoenn_mountain_story.h"
#include "quest_log.h"
#include "constants/flags.h"
#include "constants/maps.h"
#include "constants/opponents.h"
#include "constants/vars.h"

struct MountainSceneActor
{
    u8 mapGroup;
    u8 mapNum;
    u8 localId;
    u16 hideFlag;
};

#define SCENE_ACTOR(map, local, flag) {MAP_GROUP(map), MAP_NUM(map), local, flag}

// Appended story actors and Wally's existing home actor. No sprite is rebuilt;
// only a missing visible actor or an obsolete hidden actor is reconciled.
static const struct MountainSceneActor sSceneActors[] =
{
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 5, FLAG_HIDE_HOENN_METEOR_MAGMA),
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 6, FLAG_HIDE_HOENN_METEOR_MAGMA),
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 7, FLAG_HIDE_HOENN_METEOR_AQUA),
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 8, FLAG_HIDE_HOENN_METEOR_AQUA),
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 9, FLAG_HIDE_HOENN_METEOR_AQUA),
    SCENE_ACTOR(MAP_METEOR_FALLS_1F_1R, 10, FLAG_HIDE_HOENN_METEOR_COZMO),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 1, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 2, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 3, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 4, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 5, FLAG_HIDE_HOENN_CHIMNEY_AQUA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 6, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 7, FLAG_HIDE_HOENN_CHIMNEY_AQUA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 8, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 9, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_MT_CHIMNEY, 10, FLAG_HIDE_HOENN_CHIMNEY_MAGMA),
    SCENE_ACTOR(MAP_FALLARBOR_TOWN_COZMOS_HOUSE, 2, FLAG_HIDE_HOENN_COZMO_HOME),
    SCENE_ACTOR(MAP_MAUVILLE_CITY, 8, FLAG_HIDE_HOENN_MAUVILLE_WALLY),
    SCENE_ACTOR(MAP_MAUVILLE_CITY, 9, FLAG_HIDE_HOENN_MAUVILLE_WALLY),
    SCENE_ACTOR(MAP_VERDANTURF_TOWN_WANDAS_HOUSE, 3, FLAG_HIDE_HOENN_WALLY_VERDANTURF),
    SCENE_ACTOR(MAP_VERDANTURF_TOWN_WANDAS_HOUSE, 5, FLAG_HIDE_HOENN_WALLY_UNCLE_VERDANTURF),
};

static bool8 IsOnSceneMap(u16 map)
{
    return gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(map)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(map);
}

static bool8 HasHoennBadgeAtLeast(u8 first)
{
    static const u16 badgeFlags[] =
    {
        FLAG_HOENN_BADGE01_GET, FLAG_HOENN_BADGE02_GET,
        FLAG_HOENN_BADGE03_GET, FLAG_HOENN_BADGE04_GET,
        FLAG_HOENN_BADGE05_GET, FLAG_HOENN_BADGE06_GET,
        FLAG_HOENN_BADGE07_GET, FLAG_HOENN_BADGE08_GET,
    };
    u8 i;

    for (i = first - 1; i < ARRAY_COUNT(badgeFlags); i++)
        if (FlagGet(badgeFlags[i]))
            return TRUE;
    return FALSE;
}

static bool8 IsMountainLegacy(void)
{
    return !FlagGet(FLAG_HOENN_MOUNTAIN_CHAPTER_STARTED)
        && (HasHoennBadgeAtLeast(4)
         || HasTrainerBeenFought(TRAINER_HOENN_MAXIE_MT_CHIMNEY));
}

static bool8 IsWallyLegacy(void)
{
    return !FlagGet(FLAG_HOENN_MAUVILLE_WALLY_CHAPTER_STARTED)
        && (HasHoennBadgeAtLeast(3)
         || HasTrainerBeenFought(TRAINER_HOENN_WATTSON_1));
}

static u8 GetMountainPhase(void)
{
    if (FlagGet(FLAG_HOENN_MT_CHIMNEY_CLEARED))
        return 2;
    if (IsMountainLegacy())
        return 3;
    if (FlagGet(FLAG_HOENN_METEOR_FALLS_SCENE_DONE))
        return 1;
    return 0;
}

static u8 GetWallyPhase(void)
{
    if (FlagGet(FLAG_HOENN_MAUVILLE_WALLY_SCENE_DONE))
        return 2;
    if (IsWallyLegacy())
        return 3;
    if (VarGet(VAR_HOENN_SCENE_WALLY) >= 2)
        return 1;
    return 0;
}

static void SetSceneActorHidden(u16 flag, bool8 hidden)
{
    if (hidden)
        FlagSet(flag);
    else
        FlagClear(flag);
}

void HoennMountain_SetupObjects(void)
{
    u8 mountainPhase;
    u8 wallyPhase;
    bool8 mountainMap = IsOnSceneMap(MAP_METEOR_FALLS_1F_1R)
        || IsOnSceneMap(MAP_MT_CHIMNEY)
        || IsOnSceneMap(MAP_MT_CHIMNEY_CABLE_CAR_STATION)
        || IsOnSceneMap(MAP_FALLARBOR_TOWN_COZMOS_HOUSE)
        || IsOnSceneMap(MAP_LAVARIDGE_TOWN_GYM_1F);
    bool8 wallyMap = IsOnSceneMap(MAP_MAUVILLE_CITY)
        || IsOnSceneMap(MAP_VERDANTURF_TOWN_WANDAS_HOUSE);

    if (QL_IS_PLAYBACK_STATE)
        return;

    // Enrol on a low-progress visit, including before Wally catches Ralts.
    // Later badges must not turn a new participant into a legacy bypass.
    if (mountainMap && !IsMountainLegacy())
    {
        FlagSet(FLAG_HOENN_MOUNTAIN_CHAPTER_STARTED);
        FlagSet(FLAG_HOENN_VILLAIN_CHAPTER_STARTED);
    }
    if (wallyMap && !IsWallyLegacy())
        FlagSet(FLAG_HOENN_MAUVILLE_WALLY_CHAPTER_STARTED);

    mountainPhase = GetMountainPhase();
    wallyPhase = GetWallyPhase();
    SetSceneActorHidden(FLAG_HIDE_HOENN_METEOR_MAGMA, mountainPhase != 0);
    SetSceneActorHidden(FLAG_HIDE_HOENN_METEOR_AQUA, TRUE);
    SetSceneActorHidden(FLAG_HIDE_HOENN_METEOR_COZMO, mountainPhase >= 2);
    SetSceneActorHidden(FLAG_HIDE_HOENN_CHIMNEY_MAGMA, mountainPhase != 1);
    SetSceneActorHidden(FLAG_HIDE_HOENN_CHIMNEY_AQUA, mountainPhase != 1);
    SetSceneActorHidden(FLAG_HIDE_HOENN_CHIMNEY_METEORITE,
        mountainPhase < 2 || FlagGet(FLAG_HOENN_METEORITE_RECOVERED)
        || FlagGet(FLAG_HOENN_METEORITE_RETURNED));
    SetSceneActorHidden(FLAG_HIDE_HOENN_COZMO_HOME, mountainPhase < 2);
    SetSceneActorHidden(FLAG_HIDE_HOENN_MAUVILLE_WALLY, wallyPhase != 1);
    SetSceneActorHidden(FLAG_HIDE_HOENN_WALLY_UNCLE_VERDANTURF,
        wallyPhase != 2 || VarGet(VAR_HOENN_SCENE_WALLY) < 2);

    // The previous chapter still owns its original catching state and actors.
    // Only the new participant's journey temporarily moves Wally out of the house.
    if (FlagGet(FLAG_HOENN_MAUVILLE_WALLY_CHAPTER_STARTED)
     && VarGet(VAR_HOENN_SCENE_WALLY) >= 2)
        SetSceneActorHidden(FLAG_HIDE_HOENN_WALLY_VERDANTURF, wallyPhase != 2);
}

void HoennMountain_GetPhase(void)
{
    gSpecialVar_Result = GetMountainPhase();
}

void HoennMauvilleWally_GetPhase(void)
{
    gSpecialVar_Result = GetWallyPhase();
}

static bool8 SceneActorIsNearPlayer(u8 localId)
{
    s16 x, y;
    u8 i;

    PlayerGetDestCoords(&x, &y);
    x -= MAP_OFFSET;
    y -= MAP_OFFSET;
    for (i = 0; i < gMapHeader.events->objectEventCount; i++)
    {
        const struct ObjectEventTemplate *template = &gMapHeader.events->objectEvents[i];
        if (template->localId == localId)
            return template->x >= x - 8 && template->x <= x + 8
                && template->y >= y - 7 && template->y <= y + 7;
    }
    return FALSE;
}

void HoennMountain_RefreshActors(void)
{
    u8 i;
    u8 objectEventId;

    if (QL_IS_PLAYBACK_STATE)
        return;
    HoennMountain_SetupObjects();

    // MAP_SCRIPT_ON_RETURN_TO_FIELD is after native saved-object spawning.
    // Do not call this from ON_RESUME: sprites have been reset at that point.
    for (i = 0; i < ARRAY_COUNT(sSceneActors); i++)
    {
        const struct MountainSceneActor *actor = &sSceneActors[i];
        if (actor->mapGroup != gSaveBlock1Ptr->location.mapGroup
         || actor->mapNum != gSaveBlock1Ptr->location.mapNum)
            continue;
        if (FlagGet(actor->hideFlag))
        {
            if (!TryGetObjectEventIdByLocalIdAndMap(actor->localId, actor->mapNum, actor->mapGroup, &objectEventId))
                RemoveObjectEventByLocalIdAndMap(actor->localId, actor->mapNum, actor->mapGroup);
        }
        else if (SceneActorIsNearPlayer(actor->localId)
              && TryGetObjectEventIdByLocalIdAndMap(actor->localId, actor->mapNum, actor->mapGroup, &objectEventId))
        {
            TrySpawnObjectEvent(actor->localId, actor->mapNum, actor->mapGroup);
        }
    }
}
