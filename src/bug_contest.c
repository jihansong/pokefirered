#include "global.h"
#include "time_of_day.h"
#include "bug_contest.h"
#include "event_data.h"
#include "event_scripts.h"
#include "item.h"
#include "overworld.h"
#include "pokemon.h"
#include "random.h"
#include "script.h"
#include "string_util.h"
#include "strings.h"
#include "constants/items.h"
#include "constants/maps.h"
#include "constants/species.h"

// The Bug-Catching Contest, held in VIRIDIAN FOREST on Tuesdays, Thursdays and
// Saturdays of a week of 256-step days. Only the lead POKéMON enters; the rest
// of the party waits at the gate (saving is disabled meanwhile). The player
// gets 20 SAFARI BALLS in place of Sport Balls and has 20 minutes of play time.
// Encounters follow Crystal's contest table without WEEDLE's line, and scoring
// and the rival contestants follow Crystal's bug contest judging.

#define CONTEST_MINUTES   20
#define CONTEST_BALLS     20
#define NUM_CONTESTANTS   10

struct ContestEncounter
{
    u8 weight;
    u16 species;
    u8 minLevel;
    u8 maxLevel;
};

static const struct ContestEncounter sContestEncounters[] = {
    {20, SPECIES_CATERPIE,    7, 18},
    { 5, SPECIES_BUTTERFREE, 12, 15},
    {10, SPECIES_VENONAT,    10, 16},
    {10, SPECIES_PARAS,      10, 17},
    { 5, SPECIES_SCYTHER,    13, 14},
    { 5, SPECIES_PINSIR,     13, 14},
};

struct Contestant
{
    const u8 *name;
    u16 species[3];
    u16 score[3];
};

static const u8 sName_Don[] = _("BUG CATCHER DON");
static const u8 sName_Ed[] = _("BUG CATCHER ED");
static const u8 sName_Nick[] = _("COOLTRAINER NICK");
static const u8 sName_William[] = _("POKéFAN WILLIAM");
static const u8 sName_Benny[] = _("BUG CATCHER BENNY");
static const u8 sName_Barry[] = _("CAMPER BARRY");
static const u8 sName_Cindy[] = _("PICNICKER CINDY");
static const u8 sName_Josh[] = _("BUG CATCHER JOSH");
static const u8 sName_Samuel[] = _("YOUNGSTER SAMUEL");
static const u8 sName_Kipp[] = _("SCHOOL KID KIPP");

static const struct Contestant sContestants[NUM_CONTESTANTS] = {
    {sName_Don,     {SPECIES_KAKUNA, SPECIES_METAPOD, SPECIES_CATERPIE},      {300, 285, 226}},
    {sName_Ed,      {SPECIES_BUTTERFREE, SPECIES_BUTTERFREE, SPECIES_CATERPIE}, {286, 251, 237}},
    {sName_Nick,    {SPECIES_SCYTHER, SPECIES_BUTTERFREE, SPECIES_PINSIR},    {357, 349, 368}},
    {sName_William, {SPECIES_PINSIR, SPECIES_BUTTERFREE, SPECIES_VENONAT},    {332, 324, 321}},
    {sName_Benny,   {SPECIES_BUTTERFREE, SPECIES_WEEDLE, SPECIES_CATERPIE},   {318, 295, 285}},
    {sName_Barry,   {SPECIES_PINSIR, SPECIES_VENONAT, SPECIES_KAKUNA},        {366, 329, 314}},
    {sName_Cindy,   {SPECIES_BUTTERFREE, SPECIES_METAPOD, SPECIES_CATERPIE},  {341, 301, 264}},
    {sName_Josh,    {SPECIES_SCYTHER, SPECIES_BUTTERFREE, SPECIES_METAPOD},   {326, 292, 282}},
    {sName_Samuel,  {SPECIES_WEEDLE, SPECIES_PINSIR, SPECIES_CATERPIE},       {270, 282, 251}},
    {sName_Kipp,    {SPECIES_VENONAT, SPECIES_PARAS, SPECIES_KAKUNA},         {267, 254, 259}},
};

static const u8 sDayName_Sunday[] = _("SUNDAY");
static const u8 sDayName_Monday[] = _("MONDAY");
static const u8 sDayName_Tuesday[] = _("TUESDAY");
static const u8 sDayName_Wednesday[] = _("WEDNESDAY");
static const u8 sDayName_Thursday[] = _("THURSDAY");
static const u8 sDayName_Friday[] = _("FRIDAY");
static const u8 sDayName_Saturday[] = _("SATURDAY");

static const u8 *const sDayNames[] = {
    sDayName_Sunday, sDayName_Monday, sDayName_Tuesday, sDayName_Wednesday,
    sDayName_Thursday, sDayName_Friday, sDayName_Saturday,
};

struct ContestPlace
{
    s8 contestant; // -1 is the player
    u16 species;
    u16 score;
};

static EWRAM_DATA struct Pokemon sWaitingParty[PARTY_SIZE - 1] = {0};
static EWRAM_DATA u8 sWaitingPartyCount = 0;
static EWRAM_DATA struct ContestPlace sPlaces[3] = {0};

// Days come from the game clock (roadmap 2, event 9); day 0 is a Sunday
static u16 GetDayNumber(void)
{
    return GetGameClockDay();
}

static u16 GetPlayTimeMinutes(void)
{
    return gSaveBlock2Ptr->playTimeHours * 60 + gSaveBlock2Ptr->playTimeMinutes;
}

// VAR_RESULT: 0 not a contest day, 1 contest day, 2 already entered today.
// STR_VAR_1: today's day of the week.
void CheckBugContestDay(void)
{
    u8 weekday = GetDayNumber() % 7;

    StringCopy(gStringVar1, sDayNames[weekday]);
    if (weekday != 2 && weekday != 4 && weekday != 6)
        gSpecialVar_Result = 0;
    else if (VarGet(VAR_BUG_CONTEST_LAST_DAY) == GetDayNumber() + 1)
        gSpecialVar_Result = 2;
    else
        gSpecialVar_Result = 1;
}

// VAR_RESULT: TRUE if the contest started, FALSE if the balls didn't fit
void StartBugContest(void)
{
    u8 i;

    if (!CheckBagHasSpace(ITEM_SAFARI_BALL, CONTEST_BALLS))
    {
        gSpecialVar_Result = FALSE;
        return;
    }
    AddBagItem(ITEM_SAFARI_BALL, CONTEST_BALLS);
    sWaitingPartyCount = gPlayerPartyCount - 1;
    for (i = 1; i < PARTY_SIZE; i++)
    {
        sWaitingParty[i - 1] = gPlayerParty[i];
        ZeroMonData(&gPlayerParty[i]);
    }
    gPlayerPartyCount = 1;
    VarSet(VAR_BUG_CONTEST_STATE, BUG_CONTEST_ACTIVE);
    VarSet(VAR_BUG_CONTEST_START_TIME, GetPlayTimeMinutes());
    VarSet(VAR_BUG_CONTEST_LAST_DAY, GetDayNumber() + 1);
    VarSet(VAR_BUG_CONTEST_SWAP, 0);
    gSpecialVar_Result = TRUE;
}

bool8 IsBugContestActiveInForest(void)
{
    return VarGet(VAR_BUG_CONTEST_STATE) == BUG_CONTEST_ACTIVE
        && gSaveBlock1Ptr->location.mapGroup == MAP_GROUP(MAP_VIRIDIAN_FOREST)
        && gSaveBlock1Ptr->location.mapNum == MAP_NUM(MAP_VIRIDIAN_FOREST);
}

bool8 TryGenerateBugContestMon(void)
{
    u16 total = 0, roll;
    u8 i;

    if (!IsBugContestActiveInForest())
        return FALSE;
    for (i = 0; i < ARRAY_COUNT(sContestEncounters); i++)
        total += sContestEncounters[i].weight;
    roll = Random() % total;
    for (i = 0; i < ARRAY_COUNT(sContestEncounters) - 1; i++)
    {
        if (roll < sContestEncounters[i].weight)
            break;
        roll -= sContestEncounters[i].weight;
    }
    ZeroEnemyPartyMons();
    CreateMonWithNature(&gEnemyParty[0], sContestEncounters[i].species,
                        sContestEncounters[i].minLevel + Random() % (sContestEncounters[i].maxLevel - sContestEncounters[i].minLevel + 1),
                        USE_RANDOM_IVS, Random() % NUM_NATURES);
    return TRUE;
}

bool8 TryStartBugContestTimeUpScript(void)
{
    if (!IsBugContestActiveInForest())
        return FALSE;
    if ((u16)(GetPlayTimeMinutes() - VarGet(VAR_BUG_CONTEST_START_TIME)) < CONTEST_MINUTES)
        return FALSE;
    ScriptContext_SetupScript(BugContest_EventScript_TimeUp);
    return TRUE;
}

// A second catch has to replace the first; ViridianForest's frame script asks
void BugContest_AfterWildBattle(void)
{
    if (VarGet(VAR_BUG_CONTEST_STATE) == BUG_CONTEST_ACTIVE && gPlayerPartyCount > 2)
        VarSet(VAR_BUG_CONTEST_SWAP, 1);
}

// STR_VAR_1: the POKéMON caught earlier, STR_VAR_2: the new one
void BufferBugContestSwapNames(void)
{
    GetSpeciesName(gStringVar1, GetMonData(&gPlayerParty[1], MON_DATA_SPECIES));
    GetSpeciesName(gStringVar2, GetMonData(&gPlayerParty[2], MON_DATA_SPECIES));
}

// VAR_0x8004: TRUE keeps the new POKéMON, FALSE keeps the earlier one
void ResolveBugContestSwap(void)
{
    if (gSpecialVar_0x8004)
        gPlayerParty[1] = gPlayerParty[2];
    ZeroMonData(&gPlayerParty[2]);
    gPlayerPartyCount = CalculatePlayerPartyCount();
    VarSet(VAR_BUG_CONTEST_SWAP, 0);
}

// Crystal's ContestScore: 4 x max HP, the other five stats, a few IV bits,
// remaining HP / 8 and 1 point for a held item.
static u16 GetContestMonScore(struct Pokemon *mon)
{
    u16 score = 0;
    u8 atk = GetMonData(mon, MON_DATA_ATK_IV) >> 1;
    u8 def = GetMonData(mon, MON_DATA_DEF_IV) >> 1;
    u8 spe = GetMonData(mon, MON_DATA_SPEED_IV) >> 1;
    u8 spc = GetMonData(mon, MON_DATA_SPATK_IV) >> 1;
    u8 d;

    score += 4 * (GetMonData(mon, MON_DATA_MAX_HP) & 0xFF);
    score += GetMonData(mon, MON_DATA_ATK) & 0xFF;
    score += GetMonData(mon, MON_DATA_DEF) & 0xFF;
    score += GetMonData(mon, MON_DATA_SPEED) & 0xFF;
    score += GetMonData(mon, MON_DATA_SPATK) & 0xFF;
    score += GetMonData(mon, MON_DATA_SPDEF) & 0xFF;
    d = ((atk & 2) << 1) + ((def & 2) << 2);
    score += ((spe & 2) >> 1) + 2 * (spc & 2) + 2 * d;
    score += (GetMonData(mon, MON_DATA_HP) & 0xFF) >> 3;
    if (GetMonData(mon, MON_DATA_HELD_ITEM) != ITEM_NONE)
        score++;
    return score;
}

static void TryPlaceContestant(s8 contestant, u16 species, u16 score)
{
    u8 i, j;

    for (i = 0; i < 3; i++)
    {
        if (sPlaces[i].species == SPECIES_NONE || score > sPlaces[i].score)
        {
            for (j = 2; j > i; j--)
                sPlaces[j] = sPlaces[j - 1];
            sPlaces[i].contestant = contestant;
            sPlaces[i].species = species;
            sPlaces[i].score = score;
            return;
        }
    }
}

// VAR_RESULT: the player's place (1-3), or 0
void JudgeBugContest(void)
{
    u8 i, entry;

    for (i = 0; i < 3; i++)
        sPlaces[i].species = SPECIES_NONE;
    if (gPlayerPartyCount > 1)
        TryPlaceContestant(-1, GetMonData(&gPlayerParty[1], MON_DATA_SPECIES), GetContestMonScore(&gPlayerParty[1]));
    for (i = 0; i < NUM_CONTESTANTS; i++)
    {
        do
        {
            entry = Random() & 3;
        } while (entry == 3);
        TryPlaceContestant(i, sContestants[i].species[entry], sContestants[i].score[entry] + (Random() & 7));
    }
    gSpecialVar_Result = 0;
    for (i = 0; i < 3; i++)
    {
        if (sPlaces[i].contestant == -1 && sPlaces[i].species != SPECIES_NONE)
            gSpecialVar_Result = i + 1;
    }
}

// VAR_0x8005: place (1-3). STR_VAR_1: name, STR_VAR_2: POKéMON, STR_VAR_3: score
void BufferBugContestPlace(void)
{
    struct ContestPlace *place = &sPlaces[gSpecialVar_0x8005 - 1];

    if (place->contestant == -1)
        StringCopy(gStringVar1, gSaveBlock2Ptr->playerName);
    else
        StringCopy(gStringVar1, sContestants[place->contestant].name);
    GetSpeciesName(gStringVar2, place->species);
    ConvertIntToDecimalStringN(gStringVar3, place->score, STR_CONV_MODE_LEFT_ALIGN, 3);
}

// Returns the waiting POKéMON. The contest POKéMON goes after them, or to the
// PC if the party is full.
void EndBugContest(void)
{
    struct Pokemon caught;
    bool8 hasCaught = (gPlayerPartyCount > 1);
    u8 i;

    if (VarGet(VAR_BUG_CONTEST_STATE) == BUG_CONTEST_NONE)
        return;
    caught = gPlayerParty[1];
    for (i = 1; i < PARTY_SIZE; i++)
        ZeroMonData(&gPlayerParty[i]);
    for (i = 0; i < sWaitingPartyCount; i++)
        gPlayerParty[i + 1] = sWaitingParty[i];
    gPlayerPartyCount = CalculatePlayerPartyCount();
    if (hasCaught)
        GiveMonToPlayer(&caught);
    i = BagGetQuantityByItemId(ITEM_SAFARI_BALL);
    if (i != 0)
        RemoveBagItem(ITEM_SAFARI_BALL, i);
    VarSet(VAR_BUG_CONTEST_STATE, BUG_CONTEST_NONE);
    VarSet(VAR_BUG_CONTEST_SWAP, 0);
}

void BugContest_OnWhiteOut(void)
{
    EndBugContest();
}
