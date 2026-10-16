#ifndef GUARD_POKEDEX_AREA_MARKERS_H
#define GUARD_POKEDEX_AREA_MARKERS_H

void GetAreaMarkerSubsprite(s32 i, s32 dexArea, struct Subsprite * subsprites);
void DestroyPokedexAreaMarkers(u8 taskId);
u8 CreatePokedexAreaMarkers(u16 species, u16 tilesTag, u8 palIdx, u8 y, u8 region, u8 seviiIslands);
void GetHoennAreaMarkerSubsprite(s32 i, u16 mapSecId, struct Subsprite * subsprites);
void GetJohtoRoute29AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute30AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute31AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute32AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoUnionCaveAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute33AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoSlowpokeWellAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoIlexForestAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute34AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute35AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoNationalParkAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute36AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute37AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoBurnedTowerAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute38AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute39AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute40AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute41AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute42AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute43AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoMtMortarAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoLakeOfRageAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute44AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoIcePathAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoDragonDenAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute27AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoTohjoAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoRoute26AreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
void GetJohtoVictoryAreaMarkerSubsprite(s32 i, struct Subsprite *subsprites);
u8 GetNumPokedexAreaMarkers(u8 taskId);

#endif //GUARD_POKEDEX_AREA_MARKERS_H
