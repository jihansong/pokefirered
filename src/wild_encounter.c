#include "global.h"
#include "random.h"
#include "wild_encounter.h"
#include "field_specials.h"
#include "time_of_day.h"
#include "event_data.h"
#include "fieldmap.h"
#include "random.h"
#include "roamer.h"
#include "field_player_avatar.h"
#include "battle_setup.h"
#include "overworld.h"
#include "metatile_behavior.h"
#include "event_scripts.h"
#include "script.h"
#include "link.h"
#include "quest_log.h"
#include "item.h"
#include "bug_contest.h"
#include "task.h"
#include "sound.h"
#include "constants/songs.h"
#include "field_effect.h"
#include "event_object_movement.h"
#include "constants/field_effects.h"
#include "constants/map_types.h"
#include "constants/maps.h"
#include "constants/abilities.h"
#include "constants/items.h"

#define MAX_ENCOUNTER_RATE 1600

#define HEADER_NONE 0xFFFF

struct WildEncounterData
{
    u32 rngState;
    u16 prevMetatileBehavior;
    u16 encounterRateBuff;
    u8 stepsSinceLastEncounter;
    u8 abilityEffect;
    u16 leadMonHeldItem;
};

static EWRAM_DATA struct WildEncounterData sWildEncounterData = {};
static EWRAM_DATA bool8 sWildEncountersDisabled = FALSE;

static bool8 UnlockedTanobyOrAreNotInTanoby(void);
static u32 GenerateUnownPersonalityByLetter(u8 letter);
static bool8 IsWildLevelAllowedByRepel(u8 level);
static void ApplyFluteEncounterRateMod(u32 *rate);
static u8 GetFluteEncounterRateModType(void);
static void ApplyCleanseTagEncounterRateMod(u32 *rate);
static bool8 IsLeadMonHoldingCleanseTag(void);
static u16 WildEncounterRandom(void);
static void AddToWildEncounterRateBuff(u8 encouterRate);

#include "data/wild_encounters.h"

extern const struct WildPokemonHeader gWildMonHeadersMorning[];
extern const struct WildPokemonHeader gWildMonHeadersNight[];

// Morning and night tables (roadmap 2, event 9) are parallel copies of
// gWildMonHeaders in the same order, so header ids work across all three.
static const struct WildPokemonHeader *GetTimeOfDayWildMonHeaders(void)
{
    switch (GetTimeOfDay())
    {
    case TIME_MORNING:
        return gWildMonHeadersMorning;
    case TIME_NIGHT:
        return gWildMonHeadersNight;
    }
    return gWildMonHeaders;
}
// Looking the table up per access meant recomputing the time of day for every
// header the encounter check walked past, which cost several frames per step.
// Callers take the pointer once, and the map's header id is remembered until
// the player changes map.
#define gWildMonHeaders (GetTimeOfDayWildMonHeaders())

static u16 sCachedHeaderId;   // BSS: this file gets no .data section
static u8 sCachedHeaderMapGroup;
static u8 sCachedHeaderMapNum;
static u8 sCachedHeaderKey;
static bool8 sCachedHeaderValid;

static const u8 sUnownLetterSlots[][LAND_WILD_COUNT] = {
  //  A   A   A   A   A   A   A   A   A   A   A   ?
    { 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 27},
  //  C   C   C   D   D   D   H   H   H   U   U   O
    { 2,  2,  2,  3,  3,  3,  7,  7,  7, 20, 20, 14},
  //  N   N   N   N   S   S   S   S   I   I   E   E
    {13, 13, 13, 13, 18, 18, 18, 18,  8,  8,  4,  4},
  //  P   P   L   L   J   J   R   R   R   Q   Q   Q
    {15, 15, 11, 11,  9,  9, 17, 17, 17, 16, 16, 16},
  //  Y   Y   T   T   G   G   G   F   F   F   K   K
    {24, 24, 19, 19,  6,  6,  6,  5,  5,  5, 10, 10},
  //  V   V   V   W   W   W   X   X   M   M   B   B
    {21, 21, 21, 22, 22, 22, 23, 23, 12, 12,  1,  1},
  //  Z   Z   Z   Z   Z   Z   Z   Z   Z   Z   Z   !
    {25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 26},
};

void DisableWildEncounters(bool8 state)
{
    sWildEncountersDisabled = state;
}

static u8 ChooseWildMonIndex_Land(void)
{
    u8 rand = Random() % ENCOUNTER_CHANCE_LAND_MONS_TOTAL;

    if (rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_0)
        return 0;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_0 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_1)
        return 1;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_1 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_2)
        return 2;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_2 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_3)
        return 3;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_3 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_4)
        return 4;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_4 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_5)
        return 5;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_5 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_6)
        return 6;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_6 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_7)
        return 7;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_7 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_8)
        return 8;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_8 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_9)
        return 9;
    else if (rand >= ENCOUNTER_CHANCE_LAND_MONS_SLOT_9 && rand < ENCOUNTER_CHANCE_LAND_MONS_SLOT_10)
        return 10;
    else
        return 11;
}

static u8 ChooseWildMonIndex_WaterRock(void)
{
    u8 rand = Random() % ENCOUNTER_CHANCE_WATER_MONS_TOTAL;

    if (rand < ENCOUNTER_CHANCE_WATER_MONS_SLOT_0)
        return 0;
    else if (rand >= ENCOUNTER_CHANCE_WATER_MONS_SLOT_0 && rand < ENCOUNTER_CHANCE_WATER_MONS_SLOT_1)
        return 1;
    else if (rand >= ENCOUNTER_CHANCE_WATER_MONS_SLOT_1 && rand < ENCOUNTER_CHANCE_WATER_MONS_SLOT_2)
        return 2;
    else if (rand >= ENCOUNTER_CHANCE_WATER_MONS_SLOT_2 && rand < ENCOUNTER_CHANCE_WATER_MONS_SLOT_3)
        return 3;
    else
        return 4;
}

static u8 ChooseWildMonIndex_Fishing(u8 rod)
{
    u8 wildMonIndex = 0;
    u8 rand = Random() % max(max(ENCOUNTER_CHANCE_FISHING_MONS_OLD_ROD_TOTAL, ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_TOTAL),
                             ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_TOTAL);

    switch (rod)
    {
    case OLD_ROD:
        if (rand < ENCOUNTER_CHANCE_FISHING_MONS_OLD_ROD_SLOT_0)
            wildMonIndex = 0;
        else
            wildMonIndex = 1;
        break;
    case GOOD_ROD:
        if (rand < ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_SLOT_2)
            wildMonIndex = 2;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_SLOT_2 && rand < ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_SLOT_3)
            wildMonIndex = 3;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_SLOT_3 && rand < ENCOUNTER_CHANCE_FISHING_MONS_GOOD_ROD_SLOT_4)
            wildMonIndex = 4;
        break;
    case SUPER_ROD:
        if (rand < ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_5)
            wildMonIndex = 5;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_5 && rand < ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_6)
            wildMonIndex = 6;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_6 && rand < ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_7)
            wildMonIndex = 7;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_7 && rand < ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_8)
            wildMonIndex = 8;
        if (rand >= ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_8 && rand < ENCOUNTER_CHANCE_FISHING_MONS_SUPER_ROD_SLOT_9)
            wildMonIndex = 9;
        break;
    }
    return wildMonIndex;
}

static u8 ChooseWildMonLevel(const struct WildPokemon * info)
{
    u8 lo;
    u8 hi;
    u8 mod;
    u8 res;
    if (info->maxLevel >= info->minLevel)
    {
        lo = info->minLevel;
        hi = info->maxLevel;
    }
    else
    {
        lo = info->maxLevel;
        hi = info->minLevel;
    }
    mod = hi - lo + 1;
    res = Random() % mod;
    return lo + res;
}

static u16 ScanCurrentMapWildMonHeaderId(void)
{
    const struct WildPokemonHeader *headers = GetTimeOfDayWildMonHeaders();
    u16 i;

    for (i = 0; ; i++)
    {
        const struct WildPokemonHeader * wildHeader = &headers[i];
        if (wildHeader->mapGroup == MAP_GROUP(MAP_UNDEFINED))
            break;

        if (wildHeader->mapGroup == gSaveBlock1Ptr->location.mapGroup &&
            wildHeader->mapNum == gSaveBlock1Ptr->location.mapNum)
        {
            if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SIX_ISLAND_ALTERING_CAVE) &&
                gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SIX_ISLAND_ALTERING_CAVE))
            {
                i += GetAlteringCaveWildSet();
            }

            if (!UnlockedTanobyOrAreNotInTanoby())
                break;
            return i;
        }
    }

    return HEADER_NONE;
}

// The header id only changes when the player changes map, so the scan runs
// once per map instead of once per step.
static u16 GetCurrentMapWildMonHeaderId(void)
{
    // Besides the map, the id depends on the ALTERING CAVE's set of the day and
    // on whether the TANOBY RUINS are open, so both go into the cache key.
    u8 key = FlagGet(FLAG_SYS_UNLOCKED_TANOBY_RUINS);

    if (gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_SIX_ISLAND_ALTERING_CAVE)
     && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SIX_ISLAND_ALTERING_CAVE))
        key |= GetAlteringCaveWildSet() << 1;

    if (!sCachedHeaderValid
     || sCachedHeaderMapGroup != gSaveBlock1Ptr->location.mapGroup
     || sCachedHeaderMapNum != gSaveBlock1Ptr->location.mapNum
     || sCachedHeaderKey != key)
    {
        sCachedHeaderId = ScanCurrentMapWildMonHeaderId();
        sCachedHeaderMapGroup = gSaveBlock1Ptr->location.mapGroup;
        sCachedHeaderMapNum = gSaveBlock1Ptr->location.mapNum;
        sCachedHeaderKey = key;
        sCachedHeaderValid = TRUE;
    }
    return sCachedHeaderId;
}

static bool8 UnlockedTanobyOrAreNotInTanoby(void)
{
    if (FlagGet(FLAG_SYS_UNLOCKED_TANOBY_RUINS))
        return TRUE;
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_SEVEN_ISLAND_TANOBY_RUINS_DILFORD_CHAMBER))
        return TRUE;
    if (!(gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_MONEAN_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_LIPTOO_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_WEEPTH_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_DILFORD_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_SCUFIB_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_RIXY_CHAMBER)
    ||  gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_VIAPOIS_CHAMBER)
    ))
        return TRUE;
    return FALSE;
}

static void GenerateWildMon(u16 species, u8 level, u8 slot)
{
    u32 personality;
    s8 chamber;
    ZeroEnemyPartyMons();
    if (species != SPECIES_UNOWN)
    {
        CreateMonWithNature(&gEnemyParty[0], species, level, USE_RANDOM_IVS, Random() % NUM_NATURES);
    }
    else
    {
        chamber = gSaveBlock1Ptr->location.mapNum - MAP_NUM(MAP_SEVEN_ISLAND_TANOBY_RUINS_MONEAN_CHAMBER);
        personality = GenerateUnownPersonalityByLetter(sUnownLetterSlots[chamber][slot]);
        CreateMon(&gEnemyParty[0], species, level, USE_RANDOM_IVS, TRUE, personality, FALSE, 0);
    }
}

static u32 GenerateUnownPersonalityByLetter(u8 letter)
{
    u32 personality;
    do
    {
        personality = (Random() << 16) | Random();
    } while (GetUnownLetterByPersonalityLoByte(personality) != letter);
    return personality;
}

u8 GetUnownLetterByPersonalityLoByte(u32 personality)
{
    return GET_UNOWN_LETTER(personality);
}

enum
{
    WILD_AREA_LAND,
    WILD_AREA_WATER,
    WILD_AREA_ROCKS,
    WILD_AREA_FISHING,
};

#define WILD_CHECK_REPEL    0x1
#define WILD_CHECK_KEEN_EYE 0x2

static bool8 TryGenerateWildMon(const struct WildPokemonInfo * info, u8 area, u8 flags)
{
    u8 slot = 0;
    u8 level;
    if (area == WILD_AREA_LAND && TryGenerateBugContestMon())
        return TRUE;
    switch (area)
    {
    case WILD_AREA_LAND:
        slot = ChooseWildMonIndex_Land();
        break;
    case WILD_AREA_WATER:
        slot = ChooseWildMonIndex_WaterRock();
        break;
    case WILD_AREA_ROCKS:
        slot = ChooseWildMonIndex_WaterRock();
        break;
    }
    level = ChooseWildMonLevel(&info->wildPokemon[slot]);
    if (flags == WILD_CHECK_REPEL && !IsWildLevelAllowedByRepel(level))
    {
        return FALSE;
    }
    GenerateWildMon(info->wildPokemon[slot].species, level, slot);
    return TRUE;
}

static u16 GenerateFishingEncounter(const struct WildPokemonInfo * info, u8 rod)
{
    u8 slot = ChooseWildMonIndex_Fishing(rod);
    u8 level = ChooseWildMonLevel(&info->wildPokemon[slot]);
    GenerateWildMon(info->wildPokemon[slot].species, level, slot);
    return info->wildPokemon[slot].species;
}

static bool8 DoWildEncounterRateDiceRoll(u16 encounterRate)
{
    if (WildEncounterRandom() % MAX_ENCOUNTER_RATE < encounterRate)
        return TRUE;
    return FALSE;
}

static bool8 DoWildEncounterRateTest(u32 encounterRate, bool8 ignoreAbility)
{
    encounterRate *= 16;
    if (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_MACH_BIKE | PLAYER_AVATAR_FLAG_ACRO_BIKE))
        encounterRate = encounterRate * 80 / 100;
    encounterRate += sWildEncounterData.encounterRateBuff * 16 / 200;
    ApplyFluteEncounterRateMod(&encounterRate);
    ApplyCleanseTagEncounterRateMod(&encounterRate);
    if (!ignoreAbility)
    {
        switch (sWildEncounterData.abilityEffect)
        {
        case 1:
            encounterRate /= 2;
            break;
        case 2:
            encounterRate *= 2;
            break;
        }
    }
    if (encounterRate > MAX_ENCOUNTER_RATE)
        encounterRate = MAX_ENCOUNTER_RATE;
    return DoWildEncounterRateDiceRoll(encounterRate);
}

static u8 GetAbilityEncounterRateModType(void)
{
    sWildEncounterData.abilityEffect = 0;
    if (!GetMonData(&gPlayerParty[0], MON_DATA_SANITY_IS_EGG))
    {
        u8 ability = GetMonAbility(&gPlayerParty[0]);
        if (ability == ABILITY_STENCH)
            sWildEncounterData.abilityEffect = 1;
        else if (ability == ABILITY_ILLUMINATE)
            sWildEncounterData.abilityEffect = 2;
    }
    return sWildEncounterData.abilityEffect;
}

static bool8 DoGlobalWildEncounterDiceRoll(void)
{
    if ((Random() % 100) >= 60)
        return FALSE;
    return TRUE;
}

#define MISSINGNO_COAST_X         23
#define MISSINGNO_ENCOUNTER_RATE  20
#define MISSINGNO_LEVEL           80

// The Gen I MISSINGNO. glitch: once the old man in VIRIDIAN CITY has shown how
// to catch POKéMON, surfing up and down the east coast of CINNABAR ISLAND can
// turn up MISSINGNO. The first encounter adds one to the 6th item in the bag,
// in place of Gen I's +128 (without the save corruption).
static bool8 TryStartMissingNoEncounter(void)
{
    struct ItemSlot *slot;

    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_CINNABAR_ISLAND)
     || gSaveBlock1Ptr->location.mapNum != MAP_NUM(MAP_CINNABAR_ISLAND)
     || gSaveBlock1Ptr->pos.x != MISSINGNO_COAST_X
     || !TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_SURFING)
     || VarGet(VAR_MAP_SCENE_VIRIDIAN_CITY_OLD_MAN) < 2)
        return FALSE;
    if (DoWildEncounterRateTest(MISSINGNO_ENCOUNTER_RATE, FALSE) != TRUE)
        return FALSE;

    ZeroEnemyPartyMons();
    CreateMonWithNature(&gEnemyParty[0], SPECIES_MISSINGNO, MISSINGNO_LEVEL, USE_RANDOM_IVS, Random() % NUM_NATURES);
    if (!FlagGet(FLAG_MISSINGNO_ITEM_BONUS))
    {
        slot = &gSaveBlock1Ptr->bagPocket_Items[5];
        if (slot->itemId != ITEM_NONE && GetBagItemQuantity(&slot->quantity) < 999)
        {
            SetBagItemQuantity(&slot->quantity, GetBagItemQuantity(&slot->quantity) + 1);
            FlagSet(FLAG_MISSINGNO_ITEM_BONUS);
        }
    }
    StartWildBattle();
    return TRUE;
}

bool8 StandardWildEncounter(u32 currMetatileAttrs, u16 previousMetatileBehavior)
{
    u16 headerId;

    if (sWildEncountersDisabled == TRUE)
        return FALSE;

    headerId = GetCurrentMapWildMonHeaderId();
    if (headerId != HEADER_NONE)
    {
        if (ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_ENCOUNTER_TYPE) == TILE_ENCOUNTER_LAND)
        {
            if (gWildMonHeaders[headerId].landMonsInfo == NULL)
                return FALSE;
            else if (previousMetatileBehavior != ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR) && !DoGlobalWildEncounterDiceRoll())
                return FALSE;
            if (DoWildEncounterRateTest(gWildMonHeaders[headerId].landMonsInfo->encounterRate, FALSE) != TRUE)
            {
                AddToWildEncounterRateBuff(gWildMonHeaders[headerId].landMonsInfo->encounterRate);
                return FALSE;
            }

            else if (TryStartRoamerEncounter() == TRUE)
            {
                if (!IsWildLevelAllowedByRepel(GetEncounteredRoamerLevel()))
                {
                    return FALSE;
                }

                StartRoamerBattle();
                return TRUE;
            }
            else
            {

                // try a regular wild land encounter
                if (TryGenerateWildMon(gWildMonHeaders[headerId].landMonsInfo, WILD_AREA_LAND, WILD_CHECK_REPEL) == TRUE)
                {
                    StartWildBattle();
                    return TRUE;
                }
                else
                {
                    AddToWildEncounterRateBuff(gWildMonHeaders[headerId].landMonsInfo->encounterRate);
                }
            }
        }
        else if (ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_ENCOUNTER_TYPE) == TILE_ENCOUNTER_WATER
                 || (TestPlayerAvatarFlags(PLAYER_AVATAR_FLAG_SURFING) && MetatileBehavior_IsBridge(ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR)) == TRUE))
        {
            if (gWildMonHeaders[headerId].waterMonsInfo == NULL)
                return FALSE;
            else if (previousMetatileBehavior != ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR) && !DoGlobalWildEncounterDiceRoll())
                return FALSE;
            else if (DoWildEncounterRateTest(gWildMonHeaders[headerId].waterMonsInfo->encounterRate, FALSE) != TRUE)
            {
                AddToWildEncounterRateBuff(gWildMonHeaders[headerId].waterMonsInfo->encounterRate);
                return FALSE;
            }

            if (TryStartRoamerEncounter() == TRUE)
            {
                if (!IsWildLevelAllowedByRepel(GetEncounteredRoamerLevel()))
                {
                    return FALSE;
                }

                StartRoamerBattle();
                return TRUE;
            }
            else // try a regular surfing encounter
            {
                if (TryGenerateWildMon(gWildMonHeaders[headerId].waterMonsInfo, WILD_AREA_WATER, WILD_CHECK_REPEL) == TRUE)
                {
                    StartWildBattle();
                    return TRUE;
                }
                else
                {
                    AddToWildEncounterRateBuff(gWildMonHeaders[headerId].waterMonsInfo->encounterRate);
                }
            }
        }
    }

    return FALSE;
}

void RockSmashWildEncounter(void)
{
    u16 headerIdx = GetCurrentMapWildMonHeaderId();
    if (headerIdx == HEADER_NONE)
        gSpecialVar_Result = FALSE;
    else if (gWildMonHeaders[headerIdx].rockSmashMonsInfo == NULL)
        gSpecialVar_Result = FALSE;
    else if (DoWildEncounterRateTest(gWildMonHeaders[headerIdx].rockSmashMonsInfo->encounterRate, TRUE) != TRUE)
        gSpecialVar_Result = FALSE;
    else if (TryGenerateWildMon(gWildMonHeaders[headerIdx].rockSmashMonsInfo, WILD_AREA_ROCKS, WILD_CHECK_REPEL) == TRUE)
    {
        StartWildBattle();
        gSpecialVar_Result = TRUE;
    }
    else
        gSpecialVar_Result = FALSE;
}

bool8 SweetScentWildEncounter(void)
{
    s16 x, y;
    u16 headerId;

    PlayerGetDestCoords(&x, &y);
    headerId = GetCurrentMapWildMonHeaderId();
    if (headerId != HEADER_NONE)
    {
        if (MapGridGetMetatileAttributeAt(x, y, METATILE_ATTRIBUTE_ENCOUNTER_TYPE) == TILE_ENCOUNTER_LAND)
        {
            if (TryStartRoamerEncounter() == TRUE)
            {
                StartRoamerBattle();
                return TRUE;
            }

            if (gWildMonHeaders[headerId].landMonsInfo == NULL)
                return FALSE;

            TryGenerateWildMon(gWildMonHeaders[headerId].landMonsInfo, WILD_AREA_LAND, 0);

            StartWildBattle();
            return TRUE;
        }
        else if (MapGridGetMetatileAttributeAt(x, y, METATILE_ATTRIBUTE_ENCOUNTER_TYPE) == TILE_ENCOUNTER_WATER)
        {
            if (TryStartRoamerEncounter() == TRUE)
            {
                StartRoamerBattle();
                return TRUE;
            }

            if (gWildMonHeaders[headerId].waterMonsInfo == NULL)
                return FALSE;

            TryGenerateWildMon(gWildMonHeaders[headerId].waterMonsInfo, WILD_AREA_WATER, 0);
            StartWildBattle();
            return TRUE;
        }
    }

    return FALSE;
}

bool8 DoesCurrentMapHaveFishingMons(void)
{
    u16 headerIdx = GetCurrentMapWildMonHeaderId();
    if (headerIdx == HEADER_NONE)
        return FALSE;
    if (gWildMonHeaders[headerIdx].fishingMonsInfo == NULL)
        return FALSE;
    return TRUE;
}

void FishingWildEncounter(u8 rod)
{
    GenerateFishingEncounter(gWildMonHeaders[GetCurrentMapWildMonHeaderId()].fishingMonsInfo, rod);
    IncrementGameStat(GAME_STAT_FISHING_CAPTURES);
    StartWildBattle();
}

u16 GetLocalWildMon(bool8 *isWaterMon)
{
    u16 headerId;
    const struct WildPokemonInfo * landMonsInfo;
    const struct WildPokemonInfo * waterMonsInfo;

    *isWaterMon = FALSE;
    headerId = GetCurrentMapWildMonHeaderId();
    if (headerId == HEADER_NONE)
        return SPECIES_NONE;
    landMonsInfo = gWildMonHeaders[headerId].landMonsInfo;
    waterMonsInfo = gWildMonHeaders[headerId].waterMonsInfo;
    // Neither
    if (landMonsInfo == NULL && waterMonsInfo == NULL)
        return SPECIES_NONE;
        // Land Pokemon
    else if (landMonsInfo != NULL && waterMonsInfo == NULL)
        return landMonsInfo->wildPokemon[ChooseWildMonIndex_Land()].species;
        // Water Pokemon
    else if (landMonsInfo == NULL && waterMonsInfo != NULL)
    {
        *isWaterMon = TRUE;
        return waterMonsInfo->wildPokemon[ChooseWildMonIndex_WaterRock()].species;
    }
    // Either land or water Pokemon
    if ((Random() % 100) < 80)
    {
        return landMonsInfo->wildPokemon[ChooseWildMonIndex_Land()].species;
    }
    else
    {
        *isWaterMon = TRUE;
        return waterMonsInfo->wildPokemon[ChooseWildMonIndex_WaterRock()].species;
    }
}

u16 GetLocalWaterMon(void)
{
    u16 headerId = GetCurrentMapWildMonHeaderId();

    if (headerId != HEADER_NONE)
    {
        const struct WildPokemonInfo * waterMonsInfo = gWildMonHeaders[headerId].waterMonsInfo;

        if (waterMonsInfo)
            return waterMonsInfo->wildPokemon[ChooseWildMonIndex_WaterRock()].species;
    }
    return SPECIES_NONE;
}

bool8 UpdateRepelCounter(void)
{
    u16 steps;

    if (InUnionRoom() == TRUE)
        return FALSE;

    if (gQuestLogState == QL_STATE_PLAYBACK)
        return FALSE;

    steps = VarGet(VAR_REPEL_STEP_COUNT);

    if (steps != 0)
    {
        steps--;
        VarSet(VAR_REPEL_STEP_COUNT, steps);
        if (steps == 0)
        {
            ScriptContext_SetupScript(EventScript_RepelWoreOff);
            return TRUE;
        }
    }
    return FALSE;
}

static bool8 IsWildLevelAllowedByRepel(u8 wildLevel)
{
    u8 i;

    if (!VarGet(VAR_REPEL_STEP_COUNT))
        return TRUE;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (GetMonData(&gPlayerParty[i], MON_DATA_HP) && !GetMonData(&gPlayerParty[i], MON_DATA_IS_EGG))
        {
            u8 ourLevel = GetMonData(&gPlayerParty[i], MON_DATA_LEVEL);

            if (wildLevel < ourLevel)
                return FALSE;
            else
                return TRUE;
        }
    }

    return FALSE;
}

static void ApplyFluteEncounterRateMod(u32 *encounterRate)
{
    switch (GetFluteEncounterRateModType())
    {
    case 1:
        *encounterRate += *encounterRate / 2;
        break;
    case 2:
        *encounterRate = *encounterRate / 2;
        break;
    }
}

static u8 GetFluteEncounterRateModType(void)
{
    if (FlagGet(FLAG_SYS_WHITE_FLUTE_ACTIVE) == TRUE)
        return 1;
    else if (FlagGet(FLAG_SYS_BLACK_FLUTE_ACTIVE) == TRUE)
        return 2;
    else
        return 0;
}

static void ApplyCleanseTagEncounterRateMod(u32 *encounterRate)
{
    if (IsLeadMonHoldingCleanseTag())
        *encounterRate = *encounterRate * 2 / 3;
}

static bool8 IsLeadMonHoldingCleanseTag(void)
{
    if (sWildEncounterData.leadMonHeldItem == ITEM_CLEANSE_TAG)
        return TRUE;
    else
        return FALSE;
}

void SeedWildEncounterRng(u16 seed)
{
    sWildEncounterData.rngState = seed;
    ResetEncounterRateModifiers();
}

static u16 WildEncounterRandom(void)
{
    sWildEncounterData.rngState = ISO_RANDOMIZE2(sWildEncounterData.rngState);
    return sWildEncounterData.rngState >> 16;
}

static u8 GetMapBaseEncounterCooldown(u8 encounterType)
{
    u16 headerIdx = GetCurrentMapWildMonHeaderId();
    if (headerIdx == HEADER_NONE)
        return 0xFF;
    if (encounterType == TILE_ENCOUNTER_LAND)
    {
        if (gWildMonHeaders[headerIdx].landMonsInfo == NULL)
            return 0xFF;
        if (gWildMonHeaders[headerIdx].landMonsInfo->encounterRate >= 80)
            return 0;
        if (gWildMonHeaders[headerIdx].landMonsInfo->encounterRate < 10)
            return 8;
        return 8 - (gWildMonHeaders[headerIdx].landMonsInfo->encounterRate / 10);
    }
    if (encounterType == TILE_ENCOUNTER_WATER)
    {
        if (gWildMonHeaders[headerIdx].waterMonsInfo == NULL)
            return 0xFF;
        if (gWildMonHeaders[headerIdx].waterMonsInfo->encounterRate >= 80)
            return 0;
        if (gWildMonHeaders[headerIdx].waterMonsInfo->encounterRate < 10)
            return 8;
        return 8 - (gWildMonHeaders[headerIdx].waterMonsInfo->encounterRate / 10);
    }
    return 0xFF;
}

void ResetEncounterRateModifiers(void)
{
    sWildEncounterData.encounterRateBuff = 0;
    sWildEncounterData.stepsSinceLastEncounter = 0;
}

static bool8 HandleWildEncounterCooldown(u32 currMetatileAttrs)
{
    u8 encounterType = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_ENCOUNTER_TYPE);
    u32 minSteps;
    u32 encRate;
    if (encounterType == TILE_ENCOUNTER_NONE)
        return FALSE;
    minSteps = GetMapBaseEncounterCooldown(encounterType);
    if (minSteps == 0xFF)
        return FALSE;
    minSteps *= 256;
    encRate = 5 * 256;
    switch (GetFluteEncounterRateModType())
    {
    case 1:
        minSteps -= minSteps / 2;
        encRate += encRate / 2;
        break;
    case 2:
        minSteps *= 2;
        encRate /= 2;
        break;
    }
    sWildEncounterData.leadMonHeldItem = GetMonData(&gPlayerParty[0], MON_DATA_HELD_ITEM);
    if (IsLeadMonHoldingCleanseTag() == TRUE)
    {
        minSteps += minSteps / 3;
        encRate -= encRate / 3;
    }
    switch (GetAbilityEncounterRateModType())
    {
    case 1:
        minSteps *= 2;
        encRate /= 2;
        break;
    case 2:
        minSteps /= 2;
        encRate *= 2;
        break;
    }
    minSteps /= 256;
    encRate /= 256;
    if (sWildEncounterData.stepsSinceLastEncounter >= minSteps)
        return TRUE;
    sWildEncounterData.stepsSinceLastEncounter++;
    if ((Random() % 100) < encRate)
        return TRUE;
    return FALSE;
}

// BW-style field phenomena: rustling grass, water splashes and cave dust.
// Each step has a 1 in 256 chance to start one on a suitable tile in view; it
// lasts 8 steps. Stepping onto it starts a rare encounter at the area's
// highest wild level + 2: EEVEE or TAUROS in grass, DRATINI or MAGIKARP (shiny
// 1 in 64) on water, and in caves either CHANSEY or a RARE CANDY.
#define PHENOMENON_CHANCE    256
#define PHENOMENON_STEPS     8
#define PHENOMENON_SHINY_KARP 64

enum {
    PHENOMENON_NONE,
    PHENOMENON_GRASS,
    PHENOMENON_WATER,
    PHENOMENON_DUST,
};

EWRAM_DATA struct FieldPhenomenon gFieldPhenomenon = {0};

static void Task_FieldPhenomenonEffect(u8 taskId)
{
    s16 *timer = &gTasks[taskId].data[0];

    if (gFieldPhenomenon.type == PHENOMENON_NONE
     || gFieldPhenomenon.mapGroup != gSaveBlock1Ptr->location.mapGroup
     || gFieldPhenomenon.mapNum != gSaveBlock1Ptr->location.mapNum)
    {
        DestroyTask(taskId);
        return;
    }
    if ((*timer)++ % 16 != 0)
        return;

    gFieldEffectArguments[0] = gFieldPhenomenon.x + MAP_OFFSET;
    gFieldEffectArguments[1] = gFieldPhenomenon.y + MAP_OFFSET;
    gFieldEffectArguments[2] = 3;
    gFieldEffectArguments[3] = 2;
    switch (gFieldPhenomenon.type)
    {
    case PHENOMENON_GRASS:
        FieldEffectStart(FLDEFF_JUMP_TALL_GRASS);
        break;
    case PHENOMENON_WATER:
        FieldEffectStart(FLDEFF_JUMP_SMALL_SPLASH);
        break;
    case PHENOMENON_DUST:
        FieldEffectStart(FLDEFF_DUST);
        break;
    }
}

static void EnsureFieldPhenomenonTask(void)
{
    if (gFieldPhenomenon.type != PHENOMENON_NONE && !FuncIsActiveTask(Task_FieldPhenomenonEffect))
        CreateTask(Task_FieldPhenomenonEffect, 80);
}

static u8 GetPhenomenonTypeAt(u16 headerId, s16 x, s16 y)
{
    u8 behavior = MapGridGetMetatileBehaviorAt(x + MAP_OFFSET, y + MAP_OFFSET);
    u8 encounterType = MapGridGetMetatileAttributeAt(x + MAP_OFFSET, y + MAP_OFFSET, METATILE_ATTRIBUTE_ENCOUNTER_TYPE);

    if (MapGridGetCollisionAt(x + MAP_OFFSET, y + MAP_OFFSET)
     || GetObjectEventIdByXY(x + MAP_OFFSET, y + MAP_OFFSET) != OBJECT_EVENTS_COUNT)
        return PHENOMENON_NONE;
    if (encounterType == TILE_ENCOUNTER_WATER && gWildMonHeaders[headerId].waterMonsInfo != NULL)
        return PHENOMENON_WATER;
    if (encounterType == TILE_ENCOUNTER_LAND && gWildMonHeaders[headerId].landMonsInfo != NULL)
    {
        if (gMapHeader.mapType == MAP_TYPE_UNDERGROUND)
            return PHENOMENON_DUST;
        if (MetatileBehavior_IsTallGrass(behavior))
            return PHENOMENON_GRASS;
    }
    return PHENOMENON_NONE;
}

static void TryStartFieldPhenomenon(void)
{
    u16 headerId = GetCurrentMapWildMonHeaderId();
    u8 i, type;
    s16 x, y;

    if (headerId == HEADER_NONE || Random() % PHENOMENON_CHANCE != 0)
        return;
    for (i = 0; i < 24; i++)
    {
        x = gSaveBlock1Ptr->pos.x + (Random() % 13) - 6;
        y = gSaveBlock1Ptr->pos.y + (Random() % 9) - 4;
        if (abs(x - gSaveBlock1Ptr->pos.x) + abs(y - gSaveBlock1Ptr->pos.y) < 2)
            continue;
        type = GetPhenomenonTypeAt(headerId, x, y);
        if (type != PHENOMENON_NONE)
        {
            gFieldPhenomenon.type = type;
            gFieldPhenomenon.x = x;
            gFieldPhenomenon.y = y;
            gFieldPhenomenon.stepsLeft = PHENOMENON_STEPS;
            gFieldPhenomenon.mapGroup = gSaveBlock1Ptr->location.mapGroup;
            gFieldPhenomenon.mapNum = gSaveBlock1Ptr->location.mapNum;
            EnsureFieldPhenomenonTask();
            if (type == PHENOMENON_GRASS)
                PlaySE(SE_M_GUST);
            else if (type == PHENOMENON_WATER)
                PlaySE(SE_PUDDLE);
            else
                PlaySE(SE_M_SAND_ATTACK);
            return;
        }
    }
}

static u8 GetPhenomenonLevel(const struct WildPokemonInfo *info, u8 count)
{
    u8 i, level = 1;

    if (info == NULL)
        return 10;
    for (i = 0; i < count; i++)
    {
        if (info->wildPokemon[i].maxLevel > level)
            level = info->wildPokemon[i].maxLevel;
        if (info->wildPokemon[i].minLevel > level)
            level = info->wildPokemon[i].minLevel;
    }
    return min(level + 2, MAX_LEVEL);
}

static void CreateShinyWildMon(u16 species, u8 level)
{
    u32 otId = T1_READ_32(gSaveBlock2Ptr->playerTrainerId);
    u16 low = Random();
    u16 high = (otId >> 16) ^ (otId & 0xFFFF) ^ low;

    CreateMon(&gEnemyParty[0], species, level, USE_RANDOM_IVS, TRUE, ((u32)high << 16) | low, OT_ID_PLAYER_ID, 0);
}

static bool8 TryStartFieldPhenomenonEncounter(void)
{
    u16 headerId;
    u8 type = gFieldPhenomenon.type;
    u8 level;

    if (type == PHENOMENON_NONE)
        return FALSE;
    if (gFieldPhenomenon.mapGroup != gSaveBlock1Ptr->location.mapGroup
     || gFieldPhenomenon.mapNum != gSaveBlock1Ptr->location.mapNum)
    {
        gFieldPhenomenon.type = PHENOMENON_NONE;
        return FALSE;
    }
    if (gSaveBlock1Ptr->pos.x != gFieldPhenomenon.x || gSaveBlock1Ptr->pos.y != gFieldPhenomenon.y)
    {
        if (--gFieldPhenomenon.stepsLeft == 0)
            gFieldPhenomenon.type = PHENOMENON_NONE;
        else
            EnsureFieldPhenomenonTask();
        return FALSE;
    }

    gFieldPhenomenon.type = PHENOMENON_NONE;
    headerId = GetCurrentMapWildMonHeaderId();
    if (headerId == HEADER_NONE)
        return FALSE;
    ZeroEnemyPartyMons();
    switch (type)
    {
    case PHENOMENON_GRASS:
        level = GetPhenomenonLevel(gWildMonHeaders[headerId].landMonsInfo, LAND_WILD_COUNT);
        CreateMonWithNature(&gEnemyParty[0], (Random() % 2) ? SPECIES_EEVEE : SPECIES_TAUROS, level, USE_RANDOM_IVS, Random() % NUM_NATURES);
        break;
    case PHENOMENON_WATER:
        level = GetPhenomenonLevel(gWildMonHeaders[headerId].waterMonsInfo, WATER_WILD_COUNT);
        if (Random() % 2)
            CreateMonWithNature(&gEnemyParty[0], SPECIES_DRATINI, level, USE_RANDOM_IVS, Random() % NUM_NATURES);
        else if (Random() % PHENOMENON_SHINY_KARP == 0)
            CreateShinyWildMon(SPECIES_MAGIKARP, level);
        else
            CreateMonWithNature(&gEnemyParty[0], SPECIES_MAGIKARP, level, USE_RANDOM_IVS, Random() % NUM_NATURES);
        break;
    case PHENOMENON_DUST:
        if (Random() % 2)
        {
            ScriptContext_SetupScript(EventScript_FieldPhenomenonDustItem);
            return TRUE;
        }
        level = GetPhenomenonLevel(gWildMonHeaders[headerId].landMonsInfo, LAND_WILD_COUNT);
        CreateMonWithNature(&gEnemyParty[0], SPECIES_CHANSEY, level, USE_RANDOM_IVS, Random() % NUM_NATURES);
        break;
    }
    StartWildBattle();
    return TRUE;
}

bool8 TryStandardWildEncounter(u32 currMetatileAttrs)
{
    if (TryStartFieldPhenomenonEncounter() == TRUE)
    {
        sWildEncounterData.prevMetatileBehavior = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR);
        return TRUE;
    }
    if (gFieldPhenomenon.type == PHENOMENON_NONE)
        TryStartFieldPhenomenon();
    // CINNABAR ISLAND has no surfing table, so this comes before the cooldown
    if (ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_ENCOUNTER_TYPE) == TILE_ENCOUNTER_WATER
     && TryStartMissingNoEncounter() == TRUE)
    {
        sWildEncounterData.prevMetatileBehavior = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR);
        return TRUE;
    }
    if (!HandleWildEncounterCooldown(currMetatileAttrs))
    {
        sWildEncounterData.prevMetatileBehavior = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR);
        return FALSE;
    }
    else if (StandardWildEncounter(currMetatileAttrs, sWildEncounterData.prevMetatileBehavior) == TRUE)
    {
        sWildEncounterData.encounterRateBuff = 0;
        sWildEncounterData.stepsSinceLastEncounter = 0;
        sWildEncounterData.prevMetatileBehavior = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR);
        return TRUE;
    }
    else
    {
        sWildEncounterData.prevMetatileBehavior = ExtractMetatileAttribute(currMetatileAttrs, METATILE_ATTRIBUTE_BEHAVIOR);
        return FALSE;
    }
}

static void AddToWildEncounterRateBuff(u8 encounterRate)
{
    if (VarGet(VAR_REPEL_STEP_COUNT) == 0)
        sWildEncounterData.encounterRateBuff += encounterRate;
    else
        sWildEncounterData.encounterRateBuff = 0;
}
