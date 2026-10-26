#ifndef GUARD_POKEMON_STORAGE_SYSTEM_H
#define GUARD_POKEMON_STORAGE_SYSTEM_H

#include "global.h"
#include "pokemon.h"

#define LEGACY_BOXES_COUNT      14
#define TOTAL_BOXES_COUNT       28
#define EXTRA_BOXES_COUNT       (TOTAL_BOXES_COUNT - LEGACY_BOXES_COUNT)
#define IN_BOX_ROWS             5 // Number of rows, 6 Pokémon per row
#define IN_BOX_COLUMNS          6 // Number of columns, 5 Pokémon per column
#define IN_BOX_COUNT            (IN_BOX_ROWS * IN_BOX_COLUMNS)
#define BOX_NAME_LENGTH         8

/*
            COLUMNS
ROWS        0   1   2   3   4   5
            6   7   8   9   10  11
            12  13  14  15  16  17
            18  19  20  21  22  23
            24  25  26  27  28  29
*/

enum
{
    WALLPAPER_FOREST,
    WALLPAPER_CITY,
    WALLPAPER_DESERT,
    WALLPAPER_SAVANNA,
    WALLPAPER_CRAG,
    WALLPAPER_VOLCANO,
    WALLPAPER_SNOW,
    WALLPAPER_CAVE,
    WALLPAPER_BEACH,
    WALLPAPER_SEAFLOOR,
    WALLPAPER_RIVER,
    WALLPAPER_SKY,
    WALLPAPER_STARS,
    WALLPAPER_POKECENTER,
    WALLPAPER_TILES,
    WALLPAPER_SIMPLE,
    WALLPAPER_COUNT
};
#define MAX_DEFAULT_WALLPAPER WALLPAPER_SAVANNA

struct PokemonStorage
{
    /*0x0000*/ u8 currentBox;
    /*0x0004*/ struct BoxPokemon boxes[LEGACY_BOXES_COUNT][IN_BOX_COUNT];
    /*0x8344*/ u8 boxNames[LEGACY_BOXES_COUNT][BOX_NAME_LENGTH + 1];
    /*0x83C2*/ u8 boxWallpapers[LEGACY_BOXES_COUNT];
};

struct PokemonStorageExtra
{
    struct BoxPokemon boxes[EXTRA_BOXES_COUNT][IN_BOX_COUNT];
    u8 boxNames[EXTRA_BOXES_COUNT][BOX_NAME_LENGTH + 1];
    u8 boxWallpapers[EXTRA_BOXES_COUNT];
};

STATIC_ASSERT(sizeof(struct PokemonStorage) == 33744, LegacyPokemonStorageSize);
STATIC_ASSERT(offsetof(struct PokemonStorage, boxes) == 4, LegacyPokemonStorageBoxes);
STATIC_ASSERT(offsetof(struct PokemonStorage, boxNames) == 0x8344, LegacyPokemonStorageNames);
STATIC_ASSERT(offsetof(struct PokemonStorage, boxWallpapers) == 0x83C2, LegacyPokemonStorageWallpapers);
STATIC_ASSERT(sizeof(struct PokemonStorageExtra) == 33740, ExtraPokemonStorageSize);
STATIC_ASSERT(IN_BOX_COUNT == 30, PokemonStorageThirtySlotsPerBox);

u8 *GetPokemonStorageExtraData(void);
void InitPokemonStorageExtra(void);
u8 *GetBoxNamePtr(u8 boxNumber);
struct BoxPokemon *GetBoxedMonPtr(u8 boxId, u8 monPosition);
void SetBoxMonNickAt(u8 boxId, u8 monPosition, const u8 *newNick);
s16 CompactPartySlots(void);
u32 GetBoxMonDataAt(u8 boxId, u8 monPosition, s32 request);
void ZeroBoxMonAt(u8 boxId, u8 monPosition);
void CB2_ReturnToPokeStorage(void);
void ResetPokemonStorageSystem(void);
u8 StorageGetCurrentBox(void);
void DrawTextWindowAndBufferTiles(const u8 *string, void *dst, u8 zero1, u8 zero2, u8 *buffer, s32 bytesToBuffer);

#endif // GUARD_POKEMON_STORAGE_SYSTEM_H
