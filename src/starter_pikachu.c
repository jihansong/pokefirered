#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "starter_pikachu.h"
#include "constants/battle.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/pokemon.h"
#include "constants/species.h"

// The PIKACHU the player receives in Oak's Lab. Like Yellow, it is identified by
// species and original trainer; the personality value also has to match so that a
// second PIKACHU the player catches themselves isn't mistaken for it.

// Mood each event pushes PIKACHU toward (Yellow's PikachuMoods). Moods above
// PIKACHU_MOOD_NEUTRAL only ever raise the current mood, moods below only lower it,
// and PIKACHU_MOOD_NEUTRAL itself leaves it alone.
static const u8 sMoodForEvent[] = {
    [PIKAMOOD_EVENT_LEVEL_UP]         = 0x8A,
    [PIKAMOOD_EVENT_USED_ITEM]        = 0x83,
    [PIKAMOOD_EVENT_USED_X_ITEM]      = PIKACHU_MOOD_NEUTRAL,
    [PIKAMOOD_EVENT_GYM_LEADER]       = PIKACHU_MOOD_NEUTRAL,
    [PIKAMOOD_EVENT_USED_TMHM]        = 0x94,
    [PIKAMOOD_EVENT_WALKING]          = PIKACHU_MOOD_NEUTRAL,
    [PIKAMOOD_EVENT_DEPOSITED]        = 0x62,
    [PIKAMOOD_EVENT_FAINTED]          = 0x6C,
    [PIKAMOOD_EVENT_POISON_FAINT]     = 0x62,
    [PIKAMOOD_EVENT_CARELESS_TRAINER] = 0x6C,
    [PIKAMOOD_EVENT_TRADED]           = 0,
};

// After every battle PIKACHU's mood is at least this.
#define MOOD_AFTER_BATTLE 0x82

static u32 GetPlayerTrainerId(void)
{
    return gSaveBlock2Ptr->playerTrainerId[0]
         | (gSaveBlock2Ptr->playerTrainerId[1] << 8)
         | (gSaveBlock2Ptr->playerTrainerId[2] << 16)
         | (gSaveBlock2Ptr->playerTrainerId[3] << 24);
}

static u32 GetStarterPikachuPersonality(void)
{
    return VarGet(VAR_STARTER_PIKACHU_PERSONALITY_LO) | (VarGet(VAR_STARTER_PIKACHU_PERSONALITY_HI) << 16);
}

// Called right after Oak's Lab gives the player PIKACHU, which is the last mon in the party.
void RecordStarterPikachu(void)
{
    u8 partyCount = CalculatePlayerPartyCount();
    u32 personality;

    if (partyCount == 0)
        return;
    personality = GetMonData(&gPlayerParty[partyCount - 1], MON_DATA_PERSONALITY, NULL);
    VarSet(VAR_STARTER_PIKACHU_PERSONALITY_LO, personality);
    VarSet(VAR_STARTER_PIKACHU_PERSONALITY_HI, personality >> 16);
    FlagSet(FLAG_RECEIVED_STARTER_PIKACHU);
    InitPikachuMood();
}

bool8 IsStarterPikachuBoxMon(struct BoxPokemon *boxMon)
{
    u8 otName[PLAYER_NAME_LENGTH + 1];

    if (!FlagGet(FLAG_RECEIVED_STARTER_PIKACHU))
        return FALSE;
    if (GetBoxMonData(boxMon, MON_DATA_SPECIES_OR_EGG, NULL) != SPECIES_PIKACHU)
        return FALSE;
    if (GetBoxMonData(boxMon, MON_DATA_PERSONALITY, NULL) != GetStarterPikachuPersonality())
        return FALSE;
    GetBoxMonData(boxMon, MON_DATA_OT_NAME, otName);
    if (IsOtherTrainer(GetBoxMonData(boxMon, MON_DATA_OT_ID, NULL), otName))
        return FALSE;
    return TRUE;
}

bool8 IsStarterPikachu(struct Pokemon *mon)
{
    return IsStarterPikachuBoxMon(&mon->box);
}

// Returns PARTY_SIZE if the starter PIKACHU isn't in the party.
u8 GetStarterPikachuPartySlot(void)
{
    u8 i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (IsStarterPikachu(&gPlayerParty[i]))
            return i;
    }
    return PARTY_SIZE;
}

bool8 IsStarterPikachuAliveInParty(void)
{
    u8 slot = GetStarterPikachuPartySlot();

    return slot != PARTY_SIZE && GetMonData(&gPlayerParty[slot], MON_DATA_HP, NULL) != 0;
}

// Stands in for Yellow's PIKACHU happiness. Returns 0 if the starter PIKACHU isn't in the party.
u16 GetStarterPikachuFriendship(void)
{
    u8 slot = GetStarterPikachuPartySlot();

    if (slot == PARTY_SIZE)
        return 0;
    return GetMonData(&gPlayerParty[slot], MON_DATA_FRIENDSHIP, NULL);
}

u8 GetPikachuMood(void)
{
    return VarGet(VAR_PIKACHU_MOOD);
}

u8 GetPikachuEmotionModifier(void)
{
    return VarGet(VAR_PIKACHU_EMOTION_MODIFIER);
}

static void SetPikachuMoodAndModifier(u8 mood, u8 modifier)
{
    VarSet(VAR_PIKACHU_MOOD, mood);
    VarSet(VAR_PIKACHU_EMOTION_MODIFIER, modifier);
}

void InitPikachuMood(void)
{
    SetPikachuMoodAndModifier(PIKACHU_MOOD_NEUTRAL, PIKACHU_MODIFIER_NONE);
}

// Yellow's ModifyPikachuHappiness, minus the happiness change.
void UpdatePikachuMood(struct Pokemon *mon, u8 event)
{
    u8 target, mood;

    if (event >= ARRAY_COUNT(sMoodForEvent))
        return;
    // Walking and gym battles count while PIKACHU is anywhere in the party;
    // everything else has to happen to PIKACHU itself.
    if (event == PIKAMOOD_EVENT_WALKING || event == PIKAMOOD_EVENT_GYM_LEADER)
    {
        if (!IsStarterPikachuAliveInParty())
            return;
    }
    else if (mon == NULL || !IsStarterPikachu(mon))
    {
        return;
    }

    target = sMoodForEvent[event];
    mood = GetPikachuMood();
    if (target == PIKACHU_MOOD_NEUTRAL)
        return;
    if (target > PIKACHU_MOOD_NEUTRAL)
    {
        if (mood >= target || GetPikachuEmotionModifier() != PIKACHU_MODIFIER_NONE)
            return;
    }
    else
    {
        if (mood < target)
            return;
    }
    VarSet(VAR_PIKACHU_MOOD, target);
}

void UpdatePikachuMoodForFriendshipEvent(struct Pokemon *mon, u8 friendshipEvent)
{
    switch (friendshipEvent)
    {
    case FRIENDSHIP_EVENT_GROW_LEVEL:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_LEVEL_UP);
        break;
    case FRIENDSHIP_EVENT_LEAGUE_BATTLE:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_GYM_LEADER);
        break;
    case FRIENDSHIP_EVENT_LEARN_TMHM:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_USED_TMHM);
        break;
    case FRIENDSHIP_EVENT_FAINT_SMALL:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_FAINTED);
        break;
    case FRIENDSHIP_EVENT_FAINT_OUTSIDE_BATTLE:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_POISON_FAINT);
        break;
    case FRIENDSHIP_EVENT_FAINT_LARGE:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_CARELESS_TRAINER);
        break;
    }
}

void UpdatePikachuMoodForItem(struct Pokemon *mon, u16 item)
{
    switch (item)
    {
    case ITEM_RARE_CANDY:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_LEVEL_UP);
        break;
    case ITEM_HP_UP:
    case ITEM_PROTEIN:
    case ITEM_IRON:
    case ITEM_CARBOS:
    case ITEM_CALCIUM:
    case ITEM_ZINC:
        UpdatePikachuMood(mon, PIKAMOOD_EVENT_USED_ITEM);
        break;
    }
}

void UpdatePikachuMoodForLearnedMove(struct Pokemon *mon, u16 move)
{
    if ((move == MOVE_THUNDERBOLT || move == MOVE_THUNDER) && IsStarterPikachu(mon))
        SetPikachuMoodAndModifier(0x85, PIKACHU_MODIFIER_LEARNED_THUNDER);
}

// Every step the mood drifts one point back toward neutral; once it gets there,
// PIKACHU forgets whatever it was reacting to.
void UpdatePikachuMoodOnStep(void)
{
    u8 mood = GetPikachuMood();

    if (mood < PIKACHU_MOOD_NEUTRAL)
        mood++;
    else if (mood > PIKACHU_MOOD_NEUTRAL)
        mood--;
    VarSet(VAR_PIKACHU_MOOD, mood);
    if (mood == PIKACHU_MOOD_NEUTRAL)
        VarSet(VAR_PIKACHU_EMOTION_MODIFIER, PIKACHU_MODIFIER_NONE);
}

void UpdatePikachuMoodAfterBattle(u8 battleOutcome)
{
    if (!IsStarterPikachuAliveInParty())
        return;
    if (battleOutcome == B_OUTCOME_CAUGHT)
        SetPikachuMoodAndModifier(0x85, PIKACHU_MODIFIER_CAUGHT_MON);
    if (GetPikachuMood() < MOOD_AFTER_BATTLE)
        VarSet(VAR_PIKACHU_MOOD, MOOD_AFTER_BATTLE);
}

void SetPikachuRefusedStoneMood(void)
{
    SetPikachuMoodAndModifier(0x82, PIKACHU_MODIFIER_REFUSED_STONE);
}

void SetPikachuFishingMood(void)
{
    if (IsStarterPikachuAliveInParty())
        SetPikachuMoodAndModifier(0x81, PIKACHU_MODIFIER_FISHING);
}
