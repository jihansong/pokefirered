#include "global.h"
#include "random.h"
#include "overworld.h"
#include "event_data.h"
#include "constants/maps.h"
#include "constants/region_map_sections.h"

// Despite having a variable to track it, the roamer is
// hard-coded to only ever be in map group 3
#define ROAMER_MAP_GROUP 3

enum
{
    MAP_GRP, // map group
    MAP_NUM, // map number
};

#define ROAMER (&gSaveBlock1Ptr->roamer)

// Roamer 0 is the legendary beast in the save block. Roamers 1 and 2 are
// LATIAS and LATIOS from the Enigma Stone event (HGSS), packed into vars.
#define NUM_ROAMERS 3
#define ROAMER_VARS_PER_SLOT 10

EWRAM_DATA u8 sLocationHistory[3][2] = {};
EWRAM_DATA u8 sRoamerLocation[NUM_ROAMERS][2] = {};
static EWRAM_DATA u8 sEncounteredRoamer = 0;

#define ___ MAP_NUM(MAP_UNDEFINED) // For empty spots in the location table

// Note: There are two potential softlocks that can occur with this table if its maps are
//       changed in particular ways. They can be avoided by ensuring the following:
//       - There must be at least 2 location sets that start with a different map,
//         i.e. every location set cannot start with the same map. This is because of
//         the while loop in RoamerMoveToOtherLocationSet.
//       - Each location set must have at least 3 unique maps. This is because of
//         the while loop in RoamerMove. In this loop the first map in the set is
//         ignored, and an additional map is ignored if the roamer was there recently.
//       - Additionally, while not a softlock, it's worth noting that if for any
//         map in the location table there is not a location set that starts with
//         that map then the roamer will be significantly less likely to move away
//         from that map when it lands there.
static const u8 sRoamerLocations[][7] = {
    {MAP_NUM(MAP_ROUTE1), MAP_NUM(MAP_ROUTE2), MAP_NUM(MAP_ROUTE21_NORTH), MAP_NUM(MAP_ROUTE22), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE2), MAP_NUM(MAP_ROUTE1), MAP_NUM(MAP_ROUTE3), MAP_NUM(MAP_ROUTE22), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE3), MAP_NUM(MAP_ROUTE2), MAP_NUM(MAP_ROUTE4), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE4), MAP_NUM(MAP_ROUTE3), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE9), MAP_NUM(MAP_ROUTE24), ___, ___},
    {MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE4), MAP_NUM(MAP_ROUTE6), MAP_NUM(MAP_ROUTE7), MAP_NUM(MAP_ROUTE8), MAP_NUM(MAP_ROUTE9), MAP_NUM(MAP_ROUTE24)},
    {MAP_NUM(MAP_ROUTE6), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE7), MAP_NUM(MAP_ROUTE8), MAP_NUM(MAP_ROUTE11), ___, ___},
    {MAP_NUM(MAP_ROUTE7), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE6), MAP_NUM(MAP_ROUTE8), MAP_NUM(MAP_ROUTE16), ___, ___},
    {MAP_NUM(MAP_ROUTE8), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE6), MAP_NUM(MAP_ROUTE7), MAP_NUM(MAP_ROUTE10), MAP_NUM(MAP_ROUTE12), ___},
    {MAP_NUM(MAP_ROUTE9), MAP_NUM(MAP_ROUTE4), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE10), MAP_NUM(MAP_ROUTE24), ___, ___},
    {MAP_NUM(MAP_ROUTE10), MAP_NUM(MAP_ROUTE8), MAP_NUM(MAP_ROUTE9), MAP_NUM(MAP_ROUTE12), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE11), MAP_NUM(MAP_ROUTE6), MAP_NUM(MAP_ROUTE12), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE12), MAP_NUM(MAP_ROUTE10), MAP_NUM(MAP_ROUTE11), MAP_NUM(MAP_ROUTE13), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE13), MAP_NUM(MAP_ROUTE12), MAP_NUM(MAP_ROUTE14), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE14), MAP_NUM(MAP_ROUTE13), MAP_NUM(MAP_ROUTE15), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE15), MAP_NUM(MAP_ROUTE14), MAP_NUM(MAP_ROUTE18), MAP_NUM(MAP_ROUTE19), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE16), MAP_NUM(MAP_ROUTE7), MAP_NUM(MAP_ROUTE17), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE17), MAP_NUM(MAP_ROUTE16), MAP_NUM(MAP_ROUTE18), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE18), MAP_NUM(MAP_ROUTE15), MAP_NUM(MAP_ROUTE17), MAP_NUM(MAP_ROUTE19), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE19), MAP_NUM(MAP_ROUTE15), MAP_NUM(MAP_ROUTE18), MAP_NUM(MAP_ROUTE20), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE20), MAP_NUM(MAP_ROUTE19), MAP_NUM(MAP_ROUTE21_NORTH), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE21_NORTH), MAP_NUM(MAP_ROUTE1), MAP_NUM(MAP_ROUTE20), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE22), MAP_NUM(MAP_ROUTE1), MAP_NUM(MAP_ROUTE2), MAP_NUM(MAP_ROUTE23), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE23), MAP_NUM(MAP_ROUTE22), MAP_NUM(MAP_ROUTE2), ___, ___, ___, ___},
    {MAP_NUM(MAP_ROUTE24), MAP_NUM(MAP_ROUTE4), MAP_NUM(MAP_ROUTE5), MAP_NUM(MAP_ROUTE9), ___, ___, ___},
    {MAP_NUM(MAP_ROUTE25), MAP_NUM(MAP_ROUTE24), MAP_NUM(MAP_ROUTE9), ___, ___, ___, ___},
    {___, ___, ___, ___, ___, ___, ___}
};

#undef ___
#define NUM_LOCATION_SETS (ARRAY_COUNT(sRoamerLocations) - 1)
#define NUM_LOCATIONS_PER_SET (ARRAY_COUNT(sRoamerLocations[0]))

static void ReadRoamer(u8 slot, struct Roamer *roamer)
{
    u16 base;

    if (slot == 0)
    {
        *roamer = *ROAMER;
        return;
    }
    base = VAR_LATI_ROAMER_DATA_START + (slot - 1) * ROAMER_VARS_PER_SLOT;
    *roamer = (struct Roamer){};
    roamer->ivs = VarGet(base) | ((u32)VarGet(base + 1) << 16);
    roamer->personality = VarGet(base + 2) | ((u32)VarGet(base + 3) << 16);
    roamer->species = VarGet(base + 4);
    roamer->hp = VarGet(base + 5);
    roamer->level = VarGet(base + 6);
    roamer->status = VarGet(base + 6) >> 8;
    roamer->cool = VarGet(base + 7);
    roamer->beauty = VarGet(base + 7) >> 8;
    roamer->cute = VarGet(base + 8);
    roamer->smart = VarGet(base + 8) >> 8;
    roamer->tough = VarGet(base + 9);
    roamer->active = VarGet(base + 9) >> 8;
}

static void WriteRoamer(u8 slot, const struct Roamer *roamer)
{
    u16 base;

    if (slot == 0)
    {
        *ROAMER = *roamer;
        return;
    }
    base = VAR_LATI_ROAMER_DATA_START + (slot - 1) * ROAMER_VARS_PER_SLOT;
    VarSet(base, roamer->ivs);
    VarSet(base + 1, roamer->ivs >> 16);
    VarSet(base + 2, roamer->personality);
    VarSet(base + 3, roamer->personality >> 16);
    VarSet(base + 4, roamer->species);
    VarSet(base + 5, roamer->hp);
    VarSet(base + 6, roamer->level | (roamer->status << 8));
    VarSet(base + 7, roamer->cool | (roamer->beauty << 8));
    VarSet(base + 8, roamer->cute | (roamer->smart << 8));
    VarSet(base + 9, roamer->tough | (roamer->active << 8));
}

static bool8 IsRoamerActive(u8 slot)
{
    struct Roamer roamer;

    ReadRoamer(slot, &roamer);
    return roamer.active;
}

void ClearRoamerData(void)
{
    u32 i;
    *ROAMER = (struct Roamer){};
    for (i = 0; i < NUM_ROAMERS; i++)
    {
        sRoamerLocation[i][MAP_GRP] = 0;
        sRoamerLocation[i][MAP_NUM] = 0;
    }
    for (i = 0; i < ARRAY_COUNT(sLocationHistory); i++)
    {
        sLocationHistory[i][MAP_GRP] = 0;
        sLocationHistory[i][MAP_NUM] = 0;
    }
}

static const u16 sRoamerSpecies[] = {
    SPECIES_ENTEI,
    SPECIES_SUICUNE,
    SPECIES_RAIKOU,
};

void ChooseRoamerSpecies(void)
{
    VarSet(VAR_ROAMER_SPECIES, Random() % ARRAY_COUNT(sRoamerSpecies));
}

u16 GetRoamerSpecies(void)
{
    u16 idx = VarGet(VAR_ROAMER_SPECIES);

    if (idx >= ARRAY_COUNT(sRoamerSpecies))
        idx = 0;
    return sRoamerSpecies[idx];
}

static void CreateRoamer(u8 slot, u16 species, u8 level)
{
    struct Pokemon *mon = &gEnemyParty[0];
    struct Roamer roamer = {};

    CreateMon(mon, species, level, USE_RANDOM_IVS, FALSE, 0, OT_ID_PLAYER_ID, 0);
    roamer.species = species;
    roamer.level = level;
    roamer.status = 0;
    roamer.active = TRUE;
    roamer.ivs = GetMonData(mon, MON_DATA_IVS);
    roamer.personality = GetMonData(mon, MON_DATA_PERSONALITY);
    roamer.hp = GetMonData(mon, MON_DATA_MAX_HP);
    roamer.cool = GetMonData(mon, MON_DATA_COOL);
    roamer.beauty = GetMonData(mon, MON_DATA_BEAUTY);
    roamer.cute = GetMonData(mon, MON_DATA_CUTE);
    roamer.smart = GetMonData(mon, MON_DATA_SMART);
    roamer.tough = GetMonData(mon, MON_DATA_TOUGH);
    WriteRoamer(slot, &roamer);
    sRoamerLocation[slot][MAP_GRP] = ROAMER_MAP_GROUP;
    sRoamerLocation[slot][MAP_NUM] = sRoamerLocations[Random() % NUM_LOCATION_SETS][0];
}

void CreateInitialRoamerMon(void)
{
    CreateRoamer(0, GetRoamerSpecies(), 50);
}

void InitRoamer(void)
{
    ClearRoamerData();
    CreateInitialRoamerMon();
}

// Special: LATIAS and LATIOS start roaming Kanto at Lv35, as in HGSS.
void StartLatiRoamers(void)
{
    CreateRoamer(1, SPECIES_LATIAS, 35);
    CreateRoamer(2, SPECIES_LATIOS, 35);
}

void UpdateLocationHistoryForRoamer(void)
{
    sLocationHistory[2][MAP_GRP] = sLocationHistory[1][MAP_GRP];
    sLocationHistory[2][MAP_NUM] = sLocationHistory[1][MAP_NUM];

    sLocationHistory[1][MAP_GRP] = sLocationHistory[0][MAP_GRP];
    sLocationHistory[1][MAP_NUM] = sLocationHistory[0][MAP_NUM];

    sLocationHistory[0][MAP_GRP] = gSaveBlock1Ptr->location.mapGroup;
    sLocationHistory[0][MAP_NUM] = gSaveBlock1Ptr->location.mapNum;
}

static void MoveRoamerToOtherLocationSet(u8 slot)
{
    u8 mapNum = 0;

    if (!IsRoamerActive(slot))
        return;

    sRoamerLocation[slot][MAP_GRP] = ROAMER_MAP_GROUP;

    // Choose a location set that starts with a map
    // different from the roamer's current map
    while (1)
    {
        mapNum = sRoamerLocations[Random() % NUM_LOCATION_SETS][0];
        if (sRoamerLocation[slot][MAP_NUM] != mapNum)
        {
            sRoamerLocation[slot][MAP_NUM] = mapNum;
            return;
        }
    }
}

void RoamerMoveToOtherLocationSet(void)
{
    u8 slot;

    for (slot = 0; slot < NUM_ROAMERS; slot++)
        MoveRoamerToOtherLocationSet(slot);
}

static void MoveRoamer(u8 slot)
{
    u8 locSet = 0;

    if ((Random() % 16) == 0)
    {
        MoveRoamerToOtherLocationSet(slot);
    }
    else
    {
        if (!IsRoamerActive(slot))
            return;

        while (locSet < NUM_LOCATION_SETS)
        {
            // Find the location set that starts with the roamer's current map
            if (sRoamerLocation[slot][MAP_NUM] == sRoamerLocations[locSet][0])
            {
                u8 mapNum;
                while (1)
                {
                    // Choose a new map (excluding the first) within this set
                    // Also exclude a map if the roamer was there 2 moves ago
                    mapNum = sRoamerLocations[locSet][(Random() % (NUM_LOCATIONS_PER_SET - 1)) + 1];
                    if (!(sLocationHistory[2][MAP_GRP] == ROAMER_MAP_GROUP
                       && sLocationHistory[2][MAP_NUM] == mapNum)
                       && mapNum != MAP_NUM(MAP_UNDEFINED))
                        break;
                }
                sRoamerLocation[slot][MAP_NUM] = mapNum;
                return;
            }
            locSet++;
        }
    }
}

void RoamerMove(void)
{
    u8 slot;

    for (slot = 0; slot < NUM_ROAMERS; slot++)
        MoveRoamer(slot);
}

static bool8 IsRoamerSlotAt(u8 slot, u8 mapGroup, u8 mapNum)
{
    return IsRoamerActive(slot) && mapGroup == sRoamerLocation[slot][MAP_GRP] && mapNum == sRoamerLocation[slot][MAP_NUM];
}

bool8 IsRoamerAt(u8 mapGroup, u8 mapNum)
{
    u8 slot;

    for (slot = 0; slot < NUM_ROAMERS; slot++)
    {
        if (IsRoamerSlotAt(slot, mapGroup, mapNum))
            return TRUE;
    }
    return FALSE;
}

void CreateRoamerMonInstance(void)
{
    u32 status;
    struct Pokemon *mon = &gEnemyParty[0];
    struct Roamer roamer;

    ReadRoamer(sEncounteredRoamer, &roamer);
    ZeroEnemyPartyMons();
    CreateMonWithIVsPersonality(mon, roamer.species, roamer.level, roamer.ivs, roamer.personality);
    status = roamer.status;
    SetMonData(mon, MON_DATA_STATUS, &status);
    SetMonData(mon, MON_DATA_HP, &roamer.hp);
    SetMonData(mon, MON_DATA_COOL, &roamer.cool);
    SetMonData(mon, MON_DATA_BEAUTY, &roamer.beauty);
    SetMonData(mon, MON_DATA_CUTE, &roamer.cute);
    SetMonData(mon, MON_DATA_SMART, &roamer.smart);
    SetMonData(mon, MON_DATA_TOUGH, &roamer.tough);
}

bool8 TryStartRoamerEncounter(void)
{
    u8 mapGroup = gSaveBlock1Ptr->location.mapGroup;
    u8 mapNum = gSaveBlock1Ptr->location.mapNum;
    u8 here[NUM_ROAMERS];
    u8 count = 0;
    u8 slot;

    for (slot = 0; slot < NUM_ROAMERS; slot++)
    {
        if (IsRoamerSlotAt(slot, mapGroup, mapNum))
            here[count++] = slot;
    }
    if (count != 0 && (Random() % 4) == 0)
    {
        sEncounteredRoamer = here[Random() % count];
        CreateRoamerMonInstance();
        return TRUE;
    }
    return FALSE;
}

void UpdateRoamerHPStatus(struct Pokemon *mon)
{
    struct Roamer roamer;

    ReadRoamer(sEncounteredRoamer, &roamer);
    roamer.hp = GetMonData(mon, MON_DATA_HP);
    roamer.status = GetMonData(mon, MON_DATA_STATUS);
    WriteRoamer(sEncounteredRoamer, &roamer);

    MoveRoamerToOtherLocationSet(sEncounteredRoamer);
}

void SetRoamerInactive(void)
{
    struct Roamer roamer;

    ReadRoamer(sEncounteredRoamer, &roamer);
    roamer.active = FALSE;
    WriteRoamer(sEncounteredRoamer, &roamer);
}

void GetRoamerLocation(u8 *mapGroup, u8 *mapNum)
{
    *mapGroup = sRoamerLocation[0][MAP_GRP];
    *mapNum = sRoamerLocation[0][MAP_NUM];
}

u16 GetRoamerLocationMapSectionId(void)
{
    if (!ROAMER->active)
        return MAPSEC_NONE;
    return Overworld_GetMapHeaderByGroupAndId(sRoamerLocation[0][MAP_GRP], sRoamerLocation[0][MAP_NUM])->regionMapSectionId;
}

// Where the active roamer of this species is, or MAPSEC_NONE
u16 GetRoamerLocationMapSectionIdBySpecies(u16 species)
{
    struct Roamer roamer;
    u8 slot;

    for (slot = 0; slot < NUM_ROAMERS; slot++)
    {
        ReadRoamer(slot, &roamer);
        if (roamer.active && roamer.species == species)
            return Overworld_GetMapHeaderByGroupAndId(sRoamerLocation[slot][MAP_GRP], sRoamerLocation[slot][MAP_NUM])->regionMapSectionId;
    }
    return MAPSEC_NONE;
}

u8 GetEncounteredRoamerLevel(void)
{
    struct Roamer roamer;

    ReadRoamer(sEncounteredRoamer, &roamer);
    return roamer.level;
}
