/* Compile separately with the target ARM compiler. Never link into the game. */
#include "global.h"
#include "pokemon_storage_system.h"
#include <stddef.h>

const u32 gSpaceAbiProbe[] = {
    sizeof(struct SaveBlock1),
    sizeof(struct SaveBlock2),
    sizeof(struct PokemonStorage),
    offsetof(struct SaveBlock1, playerParty),
    offsetof(struct SaveBlock1, flags),
    offsetof(struct SaveBlock2, hoennFlags),
    offsetof(struct SaveBlock2, hoennVars),
    offsetof(struct SaveBlock2, hoennTrainerFlags),
    sizeof(struct MapHeader),
    sizeof(struct MapLayout),
    sizeof(struct MapEvents),
    sizeof(struct ObjectEventTemplate),
    sizeof(struct WarpEvent),
    sizeof(struct Tileset),
    offsetof(struct ObjectEventTemplate, x),
    offsetof(struct ObjectEventTemplate, y),
    offsetof(struct ObjectEventTemplate, script),
    offsetof(struct ObjectEventTemplate, flagId),
};
