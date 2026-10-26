#include "global.h"
#include "battle_setup.h"
#include "event_data.h"
#include "hoenn_villain_story.h"
#include "quest_log.h"
#include "constants/flags.h"
#include "constants/maps.h"
#include "constants/opponents.h"
#include "constants/vars.h"

static void SetHideFlag(u16 flag, bool8 hidden)
{
    if (hidden)
        FlagSet(flag);
    else
        FlagClear(flag);
}

static bool8 IsOnMap(u16 map)
{
    return gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(map)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(map);
}

void HoennVillain_SetupObjects(void)
{
    bool8 legacy;
    bool8 pyreHidden;
    bool8 magmaHidden;
    bool8 interviewHidden;
    bool8 harborHidden;
    bool8 aquaHidden;

    if (QL_IS_PLAYBACK_STATE)
        return;

    legacy = !FlagGet(FLAG_HOENN_VILLAIN_CHAPTER_STARTED)
        && (FlagGet(FLAG_HOENN_BADGE07_GET)
            || FlagGet(FLAG_HOENN_SPACE_CENTER_SECURED)
            || FlagGet(FLAG_HOENN_SEAFLOOR_CLEARED)
            || FlagGet(FLAG_HOENN_RAYQUAZA_AWAKENED)
            || FlagGet(FLAG_HOENN_LEAGUE_CLEAR));
    pyreHidden = legacy || FlagGet(FLAG_HOENN_MT_PYRE_ORBS_STOLEN);
    magmaHidden = legacy || !FlagGet(FLAG_HOENN_GOT_MAGMA_EMBLEM)
        || FlagGet(FLAG_HOENN_MAGMA_HIDEOUT_CLEARED);
    interviewHidden = legacy || !FlagGet(FLAG_HOENN_MAGMA_HIDEOUT_CLEARED)
        || FlagGet(FLAG_HOENN_HARBOR_INTERVIEW_DONE)
        || FlagGet(FLAG_HOENN_SUBMARINE_STOLEN);
    harborHidden = legacy || !FlagGet(FLAG_HOENN_HARBOR_INTERVIEW_DONE)
        || !FlagGet(FLAG_HOENN_MAGMA_HIDEOUT_CLEARED)
        || FlagGet(FLAG_HOENN_SUBMARINE_STOLEN);
    aquaHidden = legacy || !FlagGet(FLAG_HOENN_SUBMARINE_STOLEN)
        || (FlagGet(FLAG_HOENN_AQUA_HIDEOUT_CLEARED)
            && FlagGet(FLAG_HOENN_SEAFLOOR_CLEARED));

    // Derive visibility only. Never backfill victory, phase or reward receipts
    // for older advanced saves, and never skip an enrolled chapter later on.
    SetHideFlag(FLAG_HIDE_HOENN_MT_PYRE_AQUA, pyreHidden);
    SetHideFlag(FLAG_HIDE_HOENN_MAGMA_HIDEOUT_RAID, magmaHidden);
    SetHideFlag(FLAG_HIDE_HOENN_MAGMA_GROUDON_SLEEPING,
        magmaHidden || FlagGet(FLAG_HOENN_MAGMA_GROUDON_AWAKENED));
    SetHideFlag(FLAG_HIDE_HOENN_MAGMA_GROUDON_AWAKE, TRUE);
    SetHideFlag(FLAG_HIDE_HOENN_SLATEPORT_INTERVIEW, interviewHidden);
    SetHideFlag(FLAG_HIDE_HOENN_HARBOR_SUBMARINE_RAID, harborHidden);
    SetHideFlag(FLAG_HIDE_HOENN_AQUA_HIDEOUT_RAID, aquaHidden);
    SetHideFlag(FLAG_HIDE_HOENN_AQUA_HIDEOUT_SUBMARINE,
        aquaHidden || FlagGet(FLAG_HOENN_AQUA_HIDEOUT_CLEARED));

    // TEMP8 is owned only by these maps; no puzzle temporary state is reused.
    if (IsOnMap(MAP_MT_PYRE_SUMMIT))
        VarSet(VAR_TEMP_8, pyreHidden ? 1 : 0);
    else if (IsOnMap(MAP_SLATEPORT_CITY_HARBOR))
        VarSet(VAR_TEMP_8, harborHidden ? 1 : 0);
    else if (IsOnMap(MAP_AQUA_HIDEOUT_B2F))
        VarSet(VAR_TEMP_8, aquaHidden || FlagGet(FLAG_HOENN_AQUA_HIDEOUT_CLEARED) ? 1 : 0);
}
