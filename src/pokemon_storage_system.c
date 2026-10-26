#include "global.h"
#include "gflib.h"
#include "pokemon_storage_system_internal.h"
#include "persistent_heap.h"
#include "string_util.h"
#include "strings.h"

STATIC_ASSERT(sizeof(struct PokemonStorageExtra) <= PERSISTENT_HEAP_PC_SIZE, ExtraPokemonStorageFitsPersistentHeap);

static struct PokemonStorageExtra *GetExtraStorage(void)
{
    return (struct PokemonStorageExtra *)GetPokemonStorageExtraData();
}

u8 *GetPokemonStorageExtraData(void)
{
    return gHeap + PERSISTENT_HEAP_PC_OFFSET;
}

void InitPokemonStorageExtra(void)
{
    u16 boxId;
    struct PokemonStorageExtra *extra = GetExtraStorage();

    CpuFill32(0, extra, sizeof(*extra));
    for (boxId = LEGACY_BOXES_COUNT; boxId < TOTAL_BOXES_COUNT; boxId++)
    {
        u8 *dest = StringCopy(GetBoxNamePtr(boxId), gText_Box);
        ConvertIntToDecimalStringN(dest, boxId + 1, STR_CONV_MODE_LEFT_ALIGN, 2);
        SetBoxWallpaper(boxId, boxId % (MAX_DEFAULT_WALLPAPER + 1));
    }
}

void BackupPokemonStorage(struct PokemonStorage * dest)
{
    *dest = *gPokemonStoragePtr;
}

void RestorePokemonStorage(struct PokemonStorage * src)
{
    *gPokemonStoragePtr = *src;
}

// Functions here are general utility functions.
u8 StorageGetCurrentBox(void)
{
    return gPokemonStoragePtr->currentBox;
}

void SetCurrentBox(u8 boxId)
{
    if (boxId < TOTAL_BOXES_COUNT)
        gPokemonStoragePtr->currentBox = boxId;
}

u32 GetBoxMonDataAt(u8 boxId, u8 boxPosition, s32 request)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        return GetBoxMonData(boxMon, request);
    else
        return 0;
}

void SetBoxMonDataAt(u8 boxId, u8 boxPosition, s32 request, const void *value)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        SetBoxMonData(boxMon, request, value);
}

u32 GetCurrentBoxMonData(u8 boxPosition, s32 request)
{
    return GetBoxMonDataAt(gPokemonStoragePtr->currentBox, boxPosition, request);
}

void SetCurrentBoxMonData(u8 boxPosition, s32 request, const void *value)
{
    SetBoxMonDataAt(gPokemonStoragePtr->currentBox, boxPosition, request, value);
}

void GetBoxMonNickAt(u8 boxId, u8 boxPosition, u8 *dst)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        GetBoxMonData(boxMon, MON_DATA_NICKNAME, dst);
    else
        *dst = EOS;
}

void SetBoxMonNickAt(u8 boxId, u8 boxPosition, const u8 *nick)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        SetBoxMonData(boxMon, MON_DATA_NICKNAME, nick);
}

u32 GetAndCopyBoxMonDataAt(u8 boxId, u8 boxPosition, s32 request, void *dst)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        return GetBoxMonData(boxMon, request, dst);
    else
        return 0;
}

void SetBoxMonAt(u8 boxId, u8 boxPosition, struct BoxPokemon * src)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        *boxMon = *src;
}

void CopyBoxMonAt(u8 boxId, u8 boxPosition, struct BoxPokemon * dst)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        *dst = *boxMon;
}

void CreateBoxMonAt(u8 boxId, u8 boxPosition, u16 species, u8 level, u8 fixedIV, u8 hasFixedPersonality, u32 personality, u8 otIDType, u32 otID)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
    {
        CreateBoxMon(boxMon,
                     species,
                     level,
                     fixedIV,
                     hasFixedPersonality, personality,
                     otIDType, otID);
    }
}

void ZeroBoxMonAt(u8 boxId, u8 boxPosition)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        ZeroBoxMonData(boxMon);
}

void BoxMonAtToMon(u8 boxId, u8 boxPosition, struct Pokemon * dst)
{
    struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, boxPosition);

    if (boxMon != NULL)
        BoxMonToMon(boxMon, dst);
}

struct BoxPokemon * GetBoxedMonPtr(u8 boxId, u8 boxPosition)
{
    if (boxPosition >= IN_BOX_COUNT || boxId >= TOTAL_BOXES_COUNT)
        return NULL;
    if (boxId < LEGACY_BOXES_COUNT)
        return &gPokemonStoragePtr->boxes[boxId][boxPosition];
    return &GetExtraStorage()->boxes[boxId - LEGACY_BOXES_COUNT][boxPosition];
}

u8 *GetBoxNamePtr(u8 boxId)
{
    if (boxId < LEGACY_BOXES_COUNT)
        return gPokemonStoragePtr->boxNames[boxId];
    else if (boxId < TOTAL_BOXES_COUNT)
        return GetExtraStorage()->boxNames[boxId - LEGACY_BOXES_COUNT];
    else
        return NULL;
}

u8 GetBoxWallpaper(u8 boxId)
{
    if (boxId < LEGACY_BOXES_COUNT)
        return gPokemonStoragePtr->boxWallpapers[boxId];
    else if (boxId < TOTAL_BOXES_COUNT)
        return GetExtraStorage()->boxWallpapers[boxId - LEGACY_BOXES_COUNT];
    else
        return 0;
}

void SetBoxWallpaper(u8 boxId, u8 wallpaperId)
{
    if (boxId < TOTAL_BOXES_COUNT && wallpaperId < WALLPAPER_COUNT)
    {
        if (boxId < LEGACY_BOXES_COUNT)
            gPokemonStoragePtr->boxWallpapers[boxId] = wallpaperId;
        else
            GetExtraStorage()->boxWallpapers[boxId - LEGACY_BOXES_COUNT] = wallpaperId;
    }
}

s16 SeekToNextMonInBox(struct BoxPokemon * boxMons, s8 curIndex, u8 maxIndex, u8 flags)
{
    // flags:
    // bit 0: Allow eggs
    // bit 1: Search backwards
    s16 i;
    s16 adder;
    if (flags == 0 || flags == 1)
        adder = 1;
    else
        adder = -1;

    if (flags == 1 || flags == 3)
    {
        for (i = curIndex + adder; i >= 0 && i <= maxIndex; i += adder)
        {
            if (GetBoxMonData(&boxMons[i], MON_DATA_SPECIES) != SPECIES_NONE)
                return i;
        }
    }
    else
    {
        for (i = curIndex + adder; i >= 0 && i <= maxIndex; i += adder)
        {
            if (GetBoxMonData(&boxMons[i], MON_DATA_SPECIES) != SPECIES_NONE
                && !GetBoxMonData(&boxMons[i], MON_DATA_IS_EGG))
                return i;
        }
    }

    return -1;
}
