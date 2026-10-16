#include "global.h"
#include "pokedex.h"
#include "pokedex_screen.h"
#include "event_data.h"
#include "constants/flags_johto_story.h"
#include "data/pokemon/johto_dex_order.h"

u8 GetStoryRegionalDex(void)
{
    // Use only existing story progress; no new save fields or flag writes.
    if (FlagGet(FLAG_HOENN_BIRCH_RESCUED) || FlagGet(FLAG_HOENN_MET_STERN))
        return STORY_DEX_HOENN;
    if (FlagGet(FLAG_JOHTO_ARRIVAL_BRIEFED) || FlagGet(FLAG_JOHTO_MET_LAB_ASSISTANT))
        return STORY_DEX_JOHTO;
    return STORY_DEX_KANTO;
}

u16 GetRegionalDexCount(u8 region)
{
    switch (region)
    {
    case STORY_DEX_JOHTO:
        return JOHTO_DEX_COUNT;
    case STORY_DEX_HOENN:
        return HOENN_DEX_COUNT;
    default:
        return KANTO_DEX_COUNT;
    }
}

u16 RegionalDexToNational(u8 region, u16 regionalNo)
{
    if (regionalNo == 0 || regionalNo > GetRegionalDexCount(region))
        return NATIONAL_DEX_NONE;

    switch (region)
    {
    case STORY_DEX_JOHTO:
        return sJohtoToNationalOrder[regionalNo - 1];
    case STORY_DEX_HOENN:
        return HoennToNationalOrder(regionalNo);
    default:
        return regionalNo;
    }
}

u16 NationalToRegionalDex(u8 region, u16 nationalNo)
{
    u16 i;

    if (nationalNo == 0 || nationalNo > NATIONAL_DEX_COUNT)
        return 0;
    for (i = 1; i <= GetRegionalDexCount(region); i++)
        if (RegionalDexToNational(region, i) == nationalNo)
            return i;
    return 0;
}


// Unused
const u8 *GetPokedexCategoryName(u16 dexNum)
{
    return gPokedexEntries[dexNum].categoryName;
}

u16 GetPokedexHeightWeight(u16 dexNum, u8 data)
{
    switch (data)
    {
    case 0:  // height
        return gPokedexEntries[dexNum].height;
    case 1:  // weight
        return gPokedexEntries[dexNum].weight;
    default:
        return 1;
    }
}

s8 GetSetPokedexFlag(u16 nationalDexNo, u8 caseID)
{
    return DexScreen_GetSetPokedexFlag(nationalDexNo, caseID, 0);
}

u16 GetNationalPokedexCount(u8 caseID)
{
    u16 count = 0;
    u16 i;

    for (i = 0; i < NATIONAL_DEX_COUNT; i++)
    {
        switch (caseID)
        {
        case FLAG_GET_SEEN:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_SEEN))
                count++;
            break;
        case FLAG_GET_CAUGHT:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
                count++;
            break;
        }
    }
    return count;
}

/*
u16 GetHoennPokedexCount(u8 caseID)
{
    u16 count = 0;
    u16 i;

    for (i = 0; i < HOENN_DEX_COUNT; i++)
    {
        switch (caseID)
        {
        case FLAG_GET_SEEN:
            if (GetSetPokedexFlag(HoennToNationalOrder(i + 1), FLAG_GET_SEEN))
                count++;
            break;
        case FLAG_GET_CAUGHT:
            if (GetSetPokedexFlag(HoennToNationalOrder(i + 1), FLAG_GET_CAUGHT))
                count++;
            break;
        }
    }
    return count;
}
*/

u16 GetKantoPokedexCount(u8 caseID)
{
    u16 count = 0;
    u16 i;

    for (i = 0; i < KANTO_DEX_COUNT; i++)
    {
        switch (caseID)
        {
        case FLAG_GET_SEEN:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_SEEN))
                count++;
            break;
        case FLAG_GET_CAUGHT:
            if (GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
                count++;
            break;
        }
    }
    return count;
}

bool16 HasAllHoennMons(void)
{
    u16 i;

    // -2 excludes Jirachi and Deoxys
    for (i = 0; i < HOENN_DEX_COUNT - 2; i++)
    {
        if (!GetSetPokedexFlag(HoennToNationalOrder(i + 1), FLAG_GET_CAUGHT))
            return FALSE;
    }
    return TRUE;
}

bool16 HasAllKantoMons(void)
{
    u16 i;

    // -1 excludes Mew
    for (i = 0; i < KANTO_DEX_COUNT - 1; i++)
    {
        if (!GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
            return FALSE;
    }
    return TRUE;
}

bool16 HasAllMons(void)
{
    u16 i;

    // -1 excludes Mew
    for (i = 0; i < KANTO_DEX_COUNT - 1; i++)
    {
        if (!GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
            return FALSE;
    }

    // -3 excludes Lugia, Ho-Oh, and Celebi
    for (i = KANTO_DEX_COUNT; i < JOHTO_DEX_COUNT - 3; i++)
    {
        if (!GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
            return FALSE;
    }

    // -2 excludes Jirachi and Deoxys
    for (i = JOHTO_DEX_COUNT; i < NATIONAL_DEX_COUNT - 2; i++)
    {
        if (!GetSetPokedexFlag(i + 1, FLAG_GET_CAUGHT))
            return FALSE;
    }
    return TRUE;
}
