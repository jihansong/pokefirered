#ifndef GUARD_WILD_POKEMON_AREA_H
#define GUARD_WILD_POKEMON_AREA_H

// Pages of the Pokédex area screen
enum {
    DEX_AREA_REGION_KANTO, // Kanto and the Sevii Islands
    DEX_AREA_REGION_HOENN,
    DEX_AREA_REGION_COUNT
};

// Where cell (0, 0) of the Hoenn area map sits, in tiles
#define HOENN_AREA_MAP_LEFT 13
#define HOENN_AREA_MAP_TOP  6

u8 GetSpeciesPokedexAreaRegions(u16 species, u8 *seviiIslands);
s32 GetSpeciesPokedexAreaMarkers(u16 species, struct Subsprite * subsprites, u8 region, u8 seviiIslands);

#endif //GUARD_WILD_POKEMON_AREA_H
