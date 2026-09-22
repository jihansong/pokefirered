#include "global.h"
#include "field_specials.h"
#include "event_data.h"
#include "wild_encounter.h"
#include "roamer.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokedex_area_markers.h"
#include "bug_contest.h"
#include "wild_pokemon_area.h"
#include "constants/region_map_sections.h"
#include "constants/maps.h"

extern const struct WildPokemonHeader gWildMonHeadersMorning[];
extern const struct WildPokemonHeader gWildMonHeadersNight[];

// Everything a species' area screen shows, found in one pass
struct SpeciesHabitats
{
    u32 dexAreas[(DEX_AREA_COUNT + 31) / 32];       // Kanto and Sevii markers
    u32 hoennMapSecs[(KANTO_MAPSEC_START + 31) / 32]; // Hoenn markers
    bool8 hoennAlteringCave; // pokeemerald's ALTERING CAVE shares FR/LG's MAPSEC
    u8 seviiIslands;         // bit n: lives on island n + 1
};

static s32 GetRoamerIndex(u16 species);
static s32 GetRoamerPokedexAreaMarkers(u16 species, struct Subsprite * subsprites);
static void FindSpeciesHabitats(u16 species, struct SpeciesHabitats * habitats);
static bool32 IsSpeciesOnMap(const struct WildPokemonHeader * data, s32 species);
static bool32 IsSpeciesInEncounterTable(const struct WildPokemonInfo * pokemon, s32 species, s32 count);
static u16 GetMapSecIdFromWildMonHeader(const struct WildPokemonHeader * header);
static bool32 FindDexAreaByMapSec(u16 mapSecId, const u16 (*lut)[2], s32 count, s32 * lutIdx_p, u16 * tableIdx_p);
static s32 GetDexAreaSeviiIsland(u16 dexArea);

static const u16 sDexAreas_Kanto[][2] = {
    { MAPSEC_PALLET_TOWN,         DEX_AREA_PALLET_TOWN },
    { MAPSEC_VIRIDIAN_CITY,       DEX_AREA_VIRIDIAN_CITY },
    { MAPSEC_PEWTER_CITY,         DEX_AREA_PEWTER_CITY },
    { MAPSEC_CERULEAN_CITY,       DEX_AREA_CERULEAN_CITY },
    { MAPSEC_LAVENDER_TOWN,       DEX_AREA_LAVENDER_TOWN },
    { MAPSEC_VERMILION_CITY,      DEX_AREA_VERMILION_CITY },
    { MAPSEC_CELADON_CITY,        DEX_AREA_CELADON_CITY },
    { MAPSEC_FUCHSIA_CITY,        DEX_AREA_FUCHSIA_CITY },
    { MAPSEC_CINNABAR_ISLAND,     DEX_AREA_CINNABAR_ISLAND },
    { MAPSEC_INDIGO_PLATEAU,      DEX_AREA_INDIGO_PLATEAU },
    { MAPSEC_SAFFRON_CITY,        DEX_AREA_SAFFRON_CITY },
    { MAPSEC_ROUTE_4_POKECENTER,  DEX_AREA_ROUTE_4 },
    { MAPSEC_ROUTE_10_POKECENTER, DEX_AREA_ROUTE_10 },
    { MAPSEC_ROUTE_1,             DEX_AREA_ROUTE_1 },
    { MAPSEC_ROUTE_2,             DEX_AREA_ROUTE_2 },
    { MAPSEC_ROUTE_3,             DEX_AREA_ROUTE_3 },
    { MAPSEC_ROUTE_4,             DEX_AREA_ROUTE_4 },
    { MAPSEC_ROUTE_5,             DEX_AREA_ROUTE_5 },
    { MAPSEC_ROUTE_6,             DEX_AREA_ROUTE_6 },
    { MAPSEC_ROUTE_7,             DEX_AREA_ROUTE_7 },
    { MAPSEC_ROUTE_8,             DEX_AREA_ROUTE_8 },
    { MAPSEC_ROUTE_9,             DEX_AREA_ROUTE_9 },
    { MAPSEC_ROUTE_10,            DEX_AREA_ROUTE_10 },
    { MAPSEC_ROUTE_11,            DEX_AREA_ROUTE_11 },
    { MAPSEC_ROUTE_12,            DEX_AREA_ROUTE_12 },
    { MAPSEC_ROUTE_13,            DEX_AREA_ROUTE_13 },
    { MAPSEC_ROUTE_14,            DEX_AREA_ROUTE_14 },
    { MAPSEC_ROUTE_15,            DEX_AREA_ROUTE_15 },
    { MAPSEC_ROUTE_16,            DEX_AREA_ROUTE_16 },
    { MAPSEC_ROUTE_17,            DEX_AREA_ROUTE_17 },
    { MAPSEC_ROUTE_18,            DEX_AREA_ROUTE_18 },
    { MAPSEC_ROUTE_19,            DEX_AREA_ROUTE_19 },
    { MAPSEC_ROUTE_20,            DEX_AREA_ROUTE_20 },
    { MAPSEC_ROUTE_21,            DEX_AREA_ROUTE_21 },
    { MAPSEC_ROUTE_22,            DEX_AREA_ROUTE_22 },
    { MAPSEC_ROUTE_23,            DEX_AREA_ROUTE_23 },
    { MAPSEC_ROUTE_24,            DEX_AREA_ROUTE_24 },
    { MAPSEC_ROUTE_25,            DEX_AREA_ROUTE_25 },
    { MAPSEC_VIRIDIAN_FOREST,     DEX_AREA_VIRIDIAN_FOREST },
    { MAPSEC_MT_MOON,             DEX_AREA_MT_MOON },
    { MAPSEC_S_S_ANNE,            DEX_AREA_VERMILION_CITY },
    { MAPSEC_UNDERGROUND_PATH,    DEX_AREA_SAFFRON_CITY },
    { MAPSEC_UNDERGROUND_PATH_2,  DEX_AREA_SAFFRON_CITY },
    { MAPSEC_DIGLETTS_CAVE,       DEX_AREA_DIGLETTS_CAVE },
    { MAPSEC_KANTO_VICTORY_ROAD,  DEX_AREA_VICTORY_ROAD },
    { MAPSEC_ROCKET_HIDEOUT,      DEX_AREA_CELADON_CITY },
    { MAPSEC_SILPH_CO,            DEX_AREA_SAFFRON_CITY },
    { MAPSEC_POKEMON_MANSION,     DEX_AREA_POKEMON_MANSION },
    { MAPSEC_KANTO_SAFARI_ZONE,   DEX_AREA_SAFARI_ZONE },
    { MAPSEC_POKEMON_LEAGUE,      DEX_AREA_VICTORY_ROAD },
    { MAPSEC_ROCK_TUNNEL,         DEX_AREA_ROCK_TUNNEL },
    { MAPSEC_SEAFOAM_ISLANDS,     DEX_AREA_SEAFOAM_ISLANDS },
    { MAPSEC_POKEMON_TOWER,       DEX_AREA_POKEMON_TOWER },
    { MAPSEC_CERULEAN_CAVE,       DEX_AREA_CERULEAN_CAVE },
    { MAPSEC_POWER_PLANT,         DEX_AREA_POWER_PLANT }
};

static const u16 sDexAreas_Sevii1[][2] = {
	{ MAPSEC_KINDLE_ROAD,    DEX_AREA_KINDLE_ROAD },
	{ MAPSEC_TREASURE_BEACH, DEX_AREA_TREASURE_BEACH },
	{ MAPSEC_ONE_ISLAND,     DEX_AREA_ONE_ISLAND },
	{ MAPSEC_MT_EMBER,       DEX_AREA_MT_EMBER }    
};

static const u16 sDexAreas_Sevii2[][2] = {
	{ MAPSEC_CAPE_BRINK, DEX_AREA_CAPE_BRINK },
	{ MAPSEC_TWO_ISLAND, DEX_AREA_TWO_ISLAND }    
};

static const u16 sDexAreas_Sevii3[][2] = {
	{ MAPSEC_BOND_BRIDGE,     DEX_AREA_BOND_BRIDGE },
	{ MAPSEC_THREE_ISLE_PORT, DEX_AREA_THREE_ISLE_PATH },
	{ MAPSEC_THREE_ISLAND,    DEX_AREA_THREE_ISLAND },
	{ MAPSEC_BERRY_FOREST,    DEX_AREA_BERRY_FOREST },
	{ MAPSEC_THREE_ISLE_PATH, DEX_AREA_THREE_ISLE_PATH }    
};

static const u16 sDexAreas_Sevii4[][2] = {
	{ MAPSEC_FOUR_ISLAND,  DEX_AREA_FOUR_ISLAND },
	{ MAPSEC_ICEFALL_CAVE, DEX_AREA_ICEFALL_CAVE }    
};

static const u16 sDexAreas_Sevii5[][2] = {
	{ MAPSEC_RESORT_GORGEOUS,  DEX_AREA_RESORT_GORGEOUS },
	{ MAPSEC_WATER_LABYRINTH,  DEX_AREA_WATER_LABYRINTH },
	{ MAPSEC_FIVE_ISLE_MEADOW, DEX_AREA_FIVE_ISLE_MEADOW },
	{ MAPSEC_MEMORIAL_PILLAR,  DEX_AREA_MEMORIAL_PILLAR },
	{ MAPSEC_FIVE_ISLAND,      DEX_AREA_FIVE_ISLAND },
	{ MAPSEC_ROCKET_WAREHOUSE, DEX_AREA_FIVE_ISLE_MEADOW },
	{ MAPSEC_LOST_CAVE,        DEX_AREA_LOST_CAVE }    
};

static const u16 sDexAreas_Sevii6[][2] = {
	{ MAPSEC_OUTCAST_ISLAND, DEX_AREA_OUTCAST_ISLAND },
	{ MAPSEC_GREEN_PATH,     DEX_AREA_GREEN_PATH },
	{ MAPSEC_WATER_PATH,     DEX_AREA_WATER_PATH },
	{ MAPSEC_RUIN_VALLEY,    DEX_AREA_RUIN_VALLEY },
	{ MAPSEC_DOTTED_HOLE,    DEX_AREA_DOTTED_HOLE },
	{ MAPSEC_PATTERN_BUSH,   DEX_AREA_PATTERN_BUSH },
	{ MAPSEC_ALTERING_CAVE,  DEX_AREA_ALTERING_CAVE }    
};

static const u16 sDexAreas_Sevii7[][2] = {
	{ MAPSEC_TRAINER_TOWER,   DEX_AREA_TRAINER_TOWER },
	{ MAPSEC_CANYON_ENTRANCE, DEX_AREA_CANYON_ENTRANCE },
	{ MAPSEC_SEVAULT_CANYON,  DEX_AREA_SEVAULT_CANYON },
	{ MAPSEC_TANOBY_RUINS,    DEX_AREA_TANOBY_RUINS },
	{ MAPSEC_MONEAN_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_LIPTOO_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_WEEPTH_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_DILFORD_CHAMBER, DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_SCUFIB_CHAMBER,  DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_RIXY_CHAMBER,    DEX_AREA_TANOBY_CHAMBER },
	{ MAPSEC_VIAPOIS_CHAMBER, DEX_AREA_TANOBY_CHAMBER }    
};

static const struct
{
    const u16 (*table)[2];
    s32 count;
} sSeviiDexAreas[] = {
    { sDexAreas_Sevii1, ARRAY_COUNT(sDexAreas_Sevii1) },
    { sDexAreas_Sevii2, ARRAY_COUNT(sDexAreas_Sevii2) },
    { sDexAreas_Sevii3, ARRAY_COUNT(sDexAreas_Sevii3) },
    { sDexAreas_Sevii4, ARRAY_COUNT(sDexAreas_Sevii4) },
    { sDexAreas_Sevii5, ARRAY_COUNT(sDexAreas_Sevii5) },
    { sDexAreas_Sevii6, ARRAY_COUNT(sDexAreas_Sevii6) },
    { sDexAreas_Sevii7, ARRAY_COUNT(sDexAreas_Sevii7) }
};

static const u16 sRoamerSpecies[] = {
    SPECIES_ENTEI,
    SPECIES_SUICUNE,
    SPECIES_RAIKOU,
    SPECIES_LATIAS,
    SPECIES_LATIOS,
};

// The Hidden Grottoes (field_specials.c), in order
static const u8 sGrottoDexAreas[] = {
    DEX_AREA_VIRIDIAN_FOREST,
    DEX_AREA_ROUTE_11,
    DEX_AREA_ROUTE_13,
    DEX_AREA_ROUTE_15,
};

#define HABITAT_SET(bits, n) ((bits)[(n) / 32] |= 1u << ((n) % 32))
#define HABITAT_HAS(bits, n) (((bits)[(n) / 32] >> ((n) % 32)) & 1)

static bool8 IsHoennWildMonHeader(const struct WildPokemonHeader * header)
{
    return header->mapGroup >= MAP_GROUP(MAP_PETALBURG_CITY);
}

// Every real habitat: the land, water, rock smash and fishing tables of all
// three times of day, all of the Altering Cave's sets, the Hidden Grottoes and
// the Bug-Catching Contest. Sevii Islands are recorded whether or not they are
// unlocked.
static void FindSpeciesHabitats(u16 species, struct SpeciesHabitats * habitats)
{
    s32 i, j;
    s32 tableIndex;
    u16 mapSecId;
    u16 dexArea;
    bool8 hoennAlteringCaveSeen = FALSE;
    const struct WildPokemonHeader * header;

    memset(habitats, 0, sizeof(*habitats));
    for (i = 0; gWildMonHeaders[i].mapGroup != MAP_GROUP(MAP_UNDEFINED); i++)
    {
        header = &gWildMonHeaders[i];
        if (header->mapGroup == MAP_GROUP(MAP_ALTERING_CAVE) && header->mapNum == MAP_NUM(MAP_ALTERING_CAVE))
        {
            // Only the first of pokeemerald's sets is ever used in Hoenn
            if (hoennAlteringCaveSeen)
                continue;
            hoennAlteringCaveSeen = TRUE;
        }
        if (!IsSpeciesOnMap(header, species)
         && !IsSpeciesOnMap(&gWildMonHeadersMorning[i], species)
         && !IsSpeciesOnMap(&gWildMonHeadersNight[i], species))
            continue;

        mapSecId = GetMapSecIdFromWildMonHeader(header);
        if (IsHoennWildMonHeader(header))
        {
            if (mapSecId < KANTO_MAPSEC_START)
                HABITAT_SET(habitats->hoennMapSecs, mapSecId);
            else if (mapSecId == MAPSEC_ALTERING_CAVE)
                habitats->hoennAlteringCave = TRUE;
            continue;
        }

        // In the vanilla game each MAPSEC only has at most one DEX_AREA.
        tableIndex = 0;
        while (FindDexAreaByMapSec(mapSecId, sDexAreas_Kanto, ARRAY_COUNT(sDexAreas_Kanto), &tableIndex, &dexArea))
            HABITAT_SET(habitats->dexAreas, dexArea);
        for (j = 0; j < ARRAY_COUNT(sSeviiDexAreas); j++)
        {
            tableIndex = 0;
            while (FindDexAreaByMapSec(mapSecId, sSeviiDexAreas[j].table, sSeviiDexAreas[j].count, &tableIndex, &dexArea))
            {
                HABITAT_SET(habitats->dexAreas, dexArea);
                habitats->seviiIslands |= 1 << j;
            }
        }
    }

    for (i = 0; i < ARRAY_COUNT(sGrottoDexAreas); i++)
    {
        if (IsHiddenGrottoSpecies(i, species))
            HABITAT_SET(habitats->dexAreas, sGrottoDexAreas[i]);
    }
    if (IsBugContestSpecies(species))
        HABITAT_SET(habitats->dexAreas, DEX_AREA_VIRIDIAN_FOREST);
    habitats->dexAreas[0] &= ~1u; // DEX_AREA_NONE has no marker
}

// Returns which area screen pages have markers for this species (bit per
// DEX_AREA_REGION_*) and the Sevii Islands it lives on.
u8 GetSpeciesPokedexAreaRegions(u16 species, u8 *seviiIslands)
{
    struct SpeciesHabitats habitats;
    u8 regions = 0;
    s32 i;

    *seviiIslands = 0;
    if (GetRoamerIndex(species) >= 0)
        return GetRoamerPokedexAreaMarkers(species, NULL) ? 1 << DEX_AREA_REGION_KANTO : 0;

    FindSpeciesHabitats(species, &habitats);
    for (i = 0; i < ARRAY_COUNT(habitats.dexAreas); i++)
    {
        if (habitats.dexAreas[i])
            regions |= 1 << DEX_AREA_REGION_KANTO;
    }
    for (i = 0; i < ARRAY_COUNT(habitats.hoennMapSecs); i++)
    {
        if (habitats.hoennMapSecs[i])
            regions |= 1 << DEX_AREA_REGION_HOENN;
    }
    if (habitats.hoennAlteringCave)
        regions |= 1 << DEX_AREA_REGION_HOENN;
    *seviiIslands = habitats.seviiIslands;
    return regions;
}

// Scans for the given species and populates 'subsprites' with the area markers
// of one page. Markers on Sevii Islands that are not drawn are left out.
// Returns the number of areas where the species was found.
s32 GetSpeciesPokedexAreaMarkers(u16 species, struct Subsprite * subsprites, u8 region, u8 seviiIslands)
{
    struct SpeciesHabitats habitats;
    s32 areaCount = 0;
    s32 i, island;

    if (GetRoamerIndex(species) >= 0)
        return region == DEX_AREA_REGION_KANTO ? GetRoamerPokedexAreaMarkers(species, subsprites) : 0;

    FindSpeciesHabitats(species, &habitats);
    if (region == DEX_AREA_REGION_HOENN)
    {
        for (i = 0; i < KANTO_MAPSEC_START; i++)
        {
            if (HABITAT_HAS(habitats.hoennMapSecs, i))
                GetHoennAreaMarkerSubsprite(areaCount++, i, subsprites);
        }
        if (habitats.hoennAlteringCave)
            GetHoennAreaMarkerSubsprite(areaCount++, MAPSEC_ALTERING_CAVE, subsprites);
        return areaCount;
    }

    for (i = DEX_AREA_NONE + 1; i < DEX_AREA_COUNT; i++)
    {
        if (!HABITAT_HAS(habitats.dexAreas, i))
            continue;
        island = GetDexAreaSeviiIsland(i);
        if (island >= 0 && !((seviiIslands >> island) & 1))
            continue;
        GetAreaMarkerSubsprite(areaCount++, i, subsprites);
    }
    return areaCount;
}

// The Sevii Island (0-6) a DEX_AREA is on, or -1 for Kanto
static s32 GetDexAreaSeviiIsland(u16 dexArea)
{
    s32 i, j;

    for (i = 0; i < ARRAY_COUNT(sSeviiDexAreas); i++)
    {
        for (j = 0; j < sSeviiDexAreas[i].count; j++)
        {
            if (sSeviiDexAreas[i].table[j][1] == dexArea)
                return i;
        }
    }
    return -1;
}

static s32 GetRoamerIndex(u16 species)
{
    s32 i;
    for (i = 0; i < ARRAY_COUNT(sRoamerSpecies); i++)
    {
        if (sRoamerSpecies[i] == species)
            return i;
    }

    return -1;
}

static s32 GetRoamerPokedexAreaMarkers(u16 species, struct Subsprite * subsprites)
{
    u16 mapSecId;
    s32 roamerIdx;
    u16 dexArea;
    s32 tableIndex;

    // Make sure that this is a roamer species that is roaming in this save.
    roamerIdx = GetRoamerIndex(species);
    if (roamerIdx < 0)
        return 0;

    mapSecId = GetRoamerLocationMapSectionIdBySpecies(species);
    tableIndex = 0;
    if (FindDexAreaByMapSec(mapSecId, sDexAreas_Kanto, ARRAY_COUNT(sDexAreas_Kanto), &tableIndex, &dexArea))
    {
        if (dexArea != DEX_AREA_NONE)
        {
            if (subsprites != NULL)
                GetAreaMarkerSubsprite(0, dexArea, subsprites);
            return 1;
        }
    }
    return 0;
}

static bool32 IsSpeciesOnMap(const struct WildPokemonHeader * data, s32 species)
{
    if (IsSpeciesInEncounterTable(data->landMonsInfo, species, LAND_WILD_COUNT))
        return TRUE;
    if (IsSpeciesInEncounterTable(data->waterMonsInfo, species, WATER_WILD_COUNT))
        return TRUE;
    // FR/LG read LAND_WILD_COUNT entries here, past the end of the fishing table
    if (IsSpeciesInEncounterTable(data->fishingMonsInfo, species, FISH_WILD_COUNT))
        return TRUE;
    if (IsSpeciesInEncounterTable(data->rockSmashMonsInfo, species, ROCK_WILD_COUNT))
        return TRUE;

    return FALSE;
}

static bool32 IsSpeciesInEncounterTable(const struct WildPokemonInfo * info, s32 species, s32 count)
{
    s32 i;
    if (info != NULL)
    {
        for (i = 0; i < count; i++)
        {
            if (info->wildPokemon[i].species == species)
                return TRUE;
        }
    }
    return FALSE;
}

static u16 GetMapSecIdFromWildMonHeader(const struct WildPokemonHeader * header)
{
    return Overworld_GetMapHeaderByGroupAndId(header->mapGroup, header->mapNum)->regionMapSectionId;
}

// Search a MAPSEC -> DEX_AREA table for the given mapsec.
// Assigns the DEX_AREA (if found) to 'dexArea', and the first unread table index to 'index'.
// Returns TRUE if DEX_AREA was found, FALSE otherwise.
static bool32 FindDexAreaByMapSec(u16 mapSecId, const u16 (*table)[2], s32 count, s32 * index, u16 * dexArea)
{
    s32 i;
    for (i = *index; i < count; i++)
    {
        if (table[i][0] == mapSecId)
        {
            *dexArea = table[i][1];
            *index = i + 1;
            return TRUE;
        }
    }
    return FALSE;
}
