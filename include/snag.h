#ifndef GUARD_SNAG_H
#define GUARD_SNAG_H

#include "constants/snag.h"

// Trainer-battle snagging (v0.10.0, docs/v0.10.0-plan.md). A BALL thrown in a
// trainer battle catches like a wild one; the caught POKéMON keeps its data but
// gets the trainer as its original trainer name and the player's ID, and the
// isSnagged bit so it always obeys.

bool8 IsSnagBlockedBattle(void);
bool8 IsSnagRefusedMon(u16 trainerNum, u16 species);
u8 GetSnagOtName(u16 trainerNum, u16 species, u8 *dest);
u8 GetSnagGroup(u16 trainerNum);
u8 GetSnagSlot(u16 trainerNum, u16 species);
u32 SnagGetExcludedSlots(u16 trainerNum);
bool8 IsExcludedBySnag(u16 trainerNum, u16 species, u32 excluded);
void SnagRecordTaken(u16 trainerNum, u16 species);
bool8 IsSnaggedBoxMon(struct BoxPokemon *boxMon);
void SnagMakeTakenMon(struct Pokemon *mon, u16 trainerNum);
u8 GiveSnaggedMonToPlayer(struct Pokemon *mon);

#endif // GUARD_SNAG_H
