#ifndef GUARD_COMPANION_MISTY_H
#define GUARD_COMPANION_MISTY_H
#define LOCALID_MISTY_COMPANION 253
struct ObjectEvent *GetMistyCompanionObject(void);
bool8 IsMistyCompanionObject(struct ObjectEvent *objectEvent);
void MistyCompanion_Update(void);
void MistyCompanion_OnMapLoad(void);
void MistyCompanion_OnPlayerMovement(u8 walkAction);
void MistyCompanion_OnObjectMovement(struct ObjectEvent *objectEvent, u8 movementActionId);
void HideMistyCompanion(void);
void ShowMistyCompanion(void);
u16 CanMistyJoin(void);
void MistyPreparePalletVisit(void);
void MistyJoin(void);
u16 MistyGetGrowthStage(void);
extern const u8 EventScript_TalkToMistyCompanion[];
#endif
