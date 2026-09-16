#ifndef GUARD_STARTER_PIKACHU_H
#define GUARD_STARTER_PIKACHU_H

// Events that change the starter PIKACHU's mood (Yellow's PIKAHAPPY_* constants).
// Its happiness is the PIKACHU's own friendship value, which FR/LG already updates
// for these events, so only the mood is tracked separately.
enum {
    PIKAMOOD_EVENT_LEVEL_UP,
    PIKAMOOD_EVENT_USED_ITEM,
    PIKAMOOD_EVENT_USED_X_ITEM,
    PIKAMOOD_EVENT_GYM_LEADER,
    PIKAMOOD_EVENT_USED_TMHM,
    PIKAMOOD_EVENT_WALKING,
    PIKAMOOD_EVENT_DEPOSITED,
    PIKAMOOD_EVENT_FAINTED,
    PIKAMOOD_EVENT_POISON_FAINT,
    PIKAMOOD_EVENT_CARELESS_TRAINER,
    PIKAMOOD_EVENT_TRADED,
};

// Values for VAR_PIKACHU_EMOTION_MODIFIER. While one is set, talking to PIKACHU
// plays a fixed reaction to what just happened instead of a mood-based one.
enum {
    PIKACHU_MODIFIER_NONE,
    PIKACHU_MODIFIER_CAUGHT_MON,
    PIKACHU_MODIFIER_FISHING,
    PIKACHU_MODIFIER_UNUSED,
    PIKACHU_MODIFIER_REFUSED_STONE,
    PIKACHU_MODIFIER_LEARNED_THUNDER,
};

#define PIKACHU_MOOD_NEUTRAL 128

void RecordStarterPikachu(void);
bool8 IsStarterPikachu(struct Pokemon *mon);
bool8 IsStarterPikachuBoxMon(struct BoxPokemon *boxMon);
u8 GetStarterPikachuPartySlot(void);
bool8 IsStarterPikachuAliveInParty(void);
u16 GetStarterPikachuFriendship(void);
u8 GetPikachuMood(void);
u8 GetPikachuEmotionModifier(void);
void InitPikachuMood(void);
void UpdatePikachuMood(struct Pokemon *mon, u8 event);
void UpdatePikachuMoodForFriendshipEvent(struct Pokemon *mon, u8 friendshipEvent);
void UpdatePikachuMoodForItem(struct Pokemon *mon, u16 item);
void UpdatePikachuMoodForLearnedMove(struct Pokemon *mon, u16 move);
void UpdatePikachuMoodOnStep(void);
void UpdatePikachuMoodAfterBattle(u8 battleOutcome);
void SetPikachuFishingMood(void);

#endif // GUARD_STARTER_PIKACHU_H
