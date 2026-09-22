#ifndef GUARD_SURFING_PIKACHU_H
#define GUARD_SURFING_PIKACHU_H

void RecordSurfingMon(u32 partySlot);
u8 TryLoadSurfPikachuPalette(void);
void EndSurfPikachu(void);
void RefreshSurfPikachuPalette(struct Sprite *sprite);

#endif // GUARD_SURFING_PIKACHU_H
