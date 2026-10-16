#ifndef GUARD_ROCKET_TRAINER_PORTRAIT_H
#define GUARD_ROCKET_TRAINER_PORTRAIT_H
#include "global.h"

#ifndef ROCKET_TRAINER_HIRES_ENABLED
// No approved native 96x96 art is present yet. Keep the existing 64x64 fallback.
#define ROCKET_TRAINER_HIRES_ENABLED 0
#endif

struct Sprite;
extern const u8 gRocketTrainerHiresEnabled;
bool8 TryCreateRocketTrainerPortrait(u16 trainerPicId, s16 x, s16 x2,
                                    s16 speed, u8 subpriority, u8 *spriteId);
bool8 TryDestroyRocketTrainerPortrait(struct Sprite *sprite);
s16 GetTrainerPortraitExitX(const struct Sprite *sprite);

#endif
