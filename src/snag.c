#include "global.h"
#include "battle.h"
#include "characters.h"
#include "event_data.h"
#include "overworld.h"
#include "pokemon.h"
#include "snag.h"
#include "string_util.h"
#include "constants/battle.h"
#include "constants/flags.h"
#include "constants/opponents.h"
#include "constants/species.h"
#include "constants/trainers.h"

// Trainer-battle snagging (v0.10.0, docs/v0.10.0-plan.md sections 3-5): who
// can't be snagged from, what a snagged POKéMON's data becomes, and which
// evolution families the rival and JESSIE & JAMES stop bringing once taken.

struct SnagFamily
{
    u16 species;
    u8 slot;
};

// Every species in the Kanto rival's and Tournament BLUE's parties, by family.
// A family taken once is left out of all their later parties, evolved or not.
// tools/qa/snagcheck.py reads these tables from the ROM and fails when a party
// has a species that isn't here.
static const struct SnagFamily sRivalFamilies[] =
{
    {SPECIES_SPEAROW,    SNAG_SLOT_RIVAL_SPEAROW},
    {SPECIES_FEAROW,     SNAG_SLOT_RIVAL_SPEAROW},
    {SPECIES_RATTATA,    SNAG_SLOT_RIVAL_RATTATA},
    {SPECIES_RATICATE,   SNAG_SLOT_RIVAL_RATTATA},
    {SPECIES_SANDSHREW,  SNAG_SLOT_RIVAL_SANDSHREW},
    {SPECIES_SANDSLASH,  SNAG_SLOT_RIVAL_SANDSHREW},
    {SPECIES_EEVEE,      SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_JOLTEON,    SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_FLAREON,    SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_VAPOREON,   SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_ESPEON,     SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_UMBREON,    SNAG_SLOT_RIVAL_EEVEE},
    {SPECIES_SHELLDER,   SNAG_SLOT_RIVAL_SHELLDER},
    {SPECIES_CLOYSTER,   SNAG_SLOT_RIVAL_SHELLDER},
    {SPECIES_VULPIX,     SNAG_SLOT_RIVAL_VULPIX},
    {SPECIES_NINETALES,  SNAG_SLOT_RIVAL_VULPIX},
    {SPECIES_MAGNEMITE,  SNAG_SLOT_RIVAL_MAGNEMITE},
    {SPECIES_MAGNETON,   SNAG_SLOT_RIVAL_MAGNEMITE},
    {SPECIES_ABRA,       SNAG_SLOT_RIVAL_ABRA},
    {SPECIES_KADABRA,    SNAG_SLOT_RIVAL_ABRA},
    {SPECIES_ALAKAZAM,   SNAG_SLOT_RIVAL_ABRA},
    {SPECIES_EXEGGCUTE,  SNAG_SLOT_RIVAL_EXEGGCUTE},
    {SPECIES_EXEGGUTOR,  SNAG_SLOT_RIVAL_EXEGGCUTE},
    {SPECIES_PIDGEY,     SNAG_SLOT_RIVAL_PIDGEY},
    {SPECIES_PIDGEOTTO,  SNAG_SLOT_RIVAL_PIDGEY},
    {SPECIES_PIDGEOT,    SNAG_SLOT_RIVAL_PIDGEY},
    {SPECIES_RHYHORN,    SNAG_SLOT_RIVAL_RHYHORN},
    {SPECIES_RHYDON,     SNAG_SLOT_RIVAL_RHYHORN},
    {SPECIES_GROWLITHE,  SNAG_SLOT_RIVAL_GROWLITHE},
    {SPECIES_ARCANINE,   SNAG_SLOT_RIVAL_GROWLITHE},
    {SPECIES_SQUIRTLE,   SNAG_SLOT_RIVAL_SQUIRTLE},
    {SPECIES_WARTORTLE,  SNAG_SLOT_RIVAL_SQUIRTLE},
    {SPECIES_BLASTOISE,  SNAG_SLOT_RIVAL_SQUIRTLE},
    {SPECIES_NONE},
};

// JESSIE & JAMES's species, MEOWTH aside (it refuses the BALL).
static const struct SnagFamily sRocketFamilies[] =
{
    {SPECIES_EKANS,      SNAG_SLOT_ROCKET_EKANS},
    {SPECIES_ARBOK,      SNAG_SLOT_ROCKET_EKANS},
    {SPECIES_KOFFING,    SNAG_SLOT_ROCKET_KOFFING},
    {SPECIES_WEEZING,    SNAG_SLOT_ROCKET_KOFFING},
    {SPECIES_MAGIKARP,   SNAG_SLOT_ROCKET_MAGIKARP},
    {SPECIES_GYARADOS,   SNAG_SLOT_ROCKET_MAGIKARP},
    {SPECIES_BELLSPROUT, SNAG_SLOT_ROCKET_BELLSPROUT},
    {SPECIES_WEEPINBELL, SNAG_SLOT_ROCKET_BELLSPROUT},
    {SPECIES_VICTREEBEL, SNAG_SLOT_ROCKET_BELLSPROUT},
    {SPECIES_LICKITUNG,  SNAG_SLOT_ROCKET_LICKITUNG},
    {SPECIES_WYNAUT,     SNAG_SLOT_ROCKET_WOBBUFFET},
    {SPECIES_WOBBUFFET,  SNAG_SLOT_ROCKET_WOBBUFFET},
    {SPECIES_NONE},
};

static const u8 sText_Jessie[] = _("JESSIE");
static const u8 sText_James[] = _("JAMES");

// Battles where the trainer still blocks the BALL: link and Union Room, the
// record facilities (Trainer Tower, Battle Tower, e-Reader), the scripted
// tutorials (Oak's Lab, POKé DUDE, the old man) and secret bases.
bool8 IsSnagBlockedBattle(void)
{
    if (gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_TRAINER_TOWER | BATTLE_TYPE_BATTLE_TOWER
                          | BATTLE_TYPE_EREADER_TRAINER | BATTLE_TYPE_FIRST_BATTLE
                          | BATTLE_TYPE_POKEDUDE | BATTLE_TYPE_OLD_MAN_TUTORIAL))
        return TRUE;
    if (gTrainerBattleOpponent_A == TRAINER_UNION_ROOM || gTrainerBattleOpponent_A == TRAINER_SECRET_BASE)
        return TRUE;
    return FALSE;
}

// Only JESSIE & JAMES's MEOWTH refuses: it won't leave its team. Legendaries in
// trainers' parties can be snagged (user decision, 2026-09-26).
bool8 IsSnagRefusedMon(u16 trainerNum, u16 species)
{
    return GetSnagGroup(trainerNum) == SNAG_GROUP_ROCKET && species == SPECIES_MEOWTH;
}

// Whose later parties remember what was taken: the Kanto rival (Hoenn's rivals
// and champions use the same classes but are ordinary trainers), Tournament
// BLUE, and JESSIE & JAMES (by their picture; the class is shared with grunts).
u8 GetSnagGroup(u16 trainerNum)
{
    if (trainerNum == TRAINER_UNION_ROOM || trainerNum == TRAINER_SECRET_BASE)
        return SNAG_GROUP_NONE;
    if (gTrainers[trainerNum].trainerPic == TRAINER_PIC_JESSIE_JAMES)
        return SNAG_GROUP_ROCKET;
    if (trainerNum == TRAINER_TOURNEY_BLUE)
        return SNAG_GROUP_RIVAL;
    if (trainerNum < HOENN_TRAINERS_START
     && (gTrainers[trainerNum].trainerClass == TRAINER_CLASS_RIVAL_EARLY
      || gTrainers[trainerNum].trainerClass == TRAINER_CLASS_RIVAL_LATE
      || gTrainers[trainerNum].trainerClass == TRAINER_CLASS_CHAMPION))
        return SNAG_GROUP_RIVAL;
    return SNAG_GROUP_NONE;
}

// The family slot of SPECIES in TRAINERNUM's group, or SNAG_SLOT_NONE.
u8 GetSnagSlot(u16 trainerNum, u16 species)
{
    const struct SnagFamily *family;

    switch (GetSnagGroup(trainerNum))
    {
    case SNAG_GROUP_RIVAL:
        family = sRivalFamilies;
        break;
    case SNAG_GROUP_ROCKET:
        family = sRocketFamilies;
        break;
    default:
        return SNAG_SLOT_NONE;
    }
    for (; family->species != SPECIES_NONE; family++)
    {
        if (family->species == species)
            return family->slot;
    }
    return SNAG_SLOT_NONE;
}

// The slots already taken from TRAINERNUM's group, one bit per slot (0 for
// everyone else, whose teams stay the same).
u32 SnagGetExcludedSlots(u16 trainerNum)
{
    u32 excluded = 0;
    u8 slot, first, end;

    switch (GetSnagGroup(trainerNum))
    {
    case SNAG_GROUP_RIVAL:
        first = SNAG_SLOTS_RIVAL_FIRST;
        end = SNAG_SLOTS_RIVAL_END;
        break;
    case SNAG_GROUP_ROCKET:
        first = SNAG_SLOTS_ROCKET_FIRST;
        end = SNAG_SLOTS_ROCKET_END;
        break;
    default:
        return 0;
    }
    for (slot = first; slot < end; slot++)
    {
        if (FlagGet(SNAG_FLAGS_START + slot))
            excluded |= 1u << slot;
    }
    return excluded;
}

bool8 IsExcludedBySnag(u16 trainerNum, u16 species, u32 excluded)
{
    u8 slot = GetSnagSlot(trainerNum, species);

    return slot != SNAG_SLOT_NONE && (excluded & (1u << slot));
}

// Called the moment the POKéMON is taken, win or lose, so blacking out and
// fighting again can't bring it back.
void SnagRecordTaken(u16 trainerNum, u16 species)
{
    u8 slot = GetSnagSlot(trainerNum, species);

    if (slot != SNAG_SLOT_NONE)
        FlagSet(SNAG_FLAGS_START + slot);
}

bool8 IsSnaggedBoxMon(struct BoxPokemon *boxMon)
{
    return GetBoxMonData(boxMon, MON_DATA_SNAGGED, NULL);
}

// The original trainer name for a POKéMON snagged from TRAINERNUM, at most
// PLAYER_NAME_LENGTH characters, padded with EOS (DEST holds
// PLAYER_NAME_LENGTH + 1). Returns the original trainer's gender.
//   the Kanto rival and Tournament BLUE: the rival's name, as battle text shows it
//   JESSIE & JAMES: whoever the POKéMON belongs to in the anime
//   "RON & MYA", "TATE&LIZA": the first name
//   "LT.SURGE", "LT. SURGE": SURGE
//   anything longer: its first 7 characters
u8 GetSnagOtName(u16 trainerNum, u16 species, u8 *dest)
{
    const u8 *name = gTrainers[trainerNum].trainerName;
    u8 gender = (gTrainers[trainerNum].encounterMusic_gender & F_TRAINER_FEMALE) ? FEMALE : MALE;
    s32 i;

    for (i = 0; i < PLAYER_NAME_LENGTH + 1; i++)
        dest[i] = EOS;

    switch (GetSnagGroup(trainerNum))
    {
    case SNAG_GROUP_RIVAL:
        // the player named the rival: no rules, just the length
        name = GetExpandedPlaceholder(PLACEHOLDER_ID_RIVAL);
        for (i = 0; i < PLAYER_NAME_LENGTH && name[i] != EOS; i++)
            dest[i] = name[i];
        return gender;
    case SNAG_GROUP_ROCKET:
        switch (GetSnagSlot(trainerNum, species))
        {
        case SNAG_SLOT_ROCKET_EKANS:
        case SNAG_SLOT_ROCKET_LICKITUNG:
        case SNAG_SLOT_ROCKET_WOBBUFFET:
            StringCopy(dest, sText_Jessie);
            return FEMALE;
        default:
            StringCopy(dest, sText_James);
            return MALE;
        }
    default:
        if (name[0] == CHAR_L && name[1] == CHAR_T && name[2] == CHAR_PERIOD)
        {
            name += 3;
            while (*name == CHAR_SPACE)
                name++;
        }
        break;
    }

    for (i = 0; i < PLAYER_NAME_LENGTH && name[i] != EOS && name[i] != CHAR_AMPERSAND; i++)
        dest[i] = name[i];
    while (i > 0 && dest[i - 1] == CHAR_SPACE)
        dest[--i] = EOS;
    return gender;
}

// The snagged POKéMON's own data (plan 3.1): the trainer as its original
// trainer, met here at its current level, and the isSnagged bit. Everything
// else (IVs, moves and PP, HP, status, held item, BALL) stays as it was. The
// original trainer ID becomes the player's in GiveSnaggedMonToPlayer.
void SnagMakeTakenMon(struct Pokemon *mon, u16 trainerNum)
{
    u8 otName[PLAYER_NAME_LENGTH + 1];
    u8 otGender = GetSnagOtName(trainerNum, GetMonData(mon, MON_DATA_SPECIES, NULL), otName);
    u8 metLocation = GetCurrentRegionMapSectionId();
    u8 metLevel = GetMonData(mon, MON_DATA_LEVEL, NULL);
    bool8 snagged = TRUE;

    SetMonData(mon, MON_DATA_OT_NAME, otName);
    SetMonData(mon, MON_DATA_OT_GENDER, &otGender);
    SetMonData(mon, MON_DATA_MET_LOCATION, &metLocation);
    SetMonData(mon, MON_DATA_MET_LEVEL, &metLevel);
    SetMonData(mon, MON_DATA_SNAGGED, &snagged);
}

// Like GiveMonToPlayer, but only the original trainer ID becomes the player's:
// the name stays the trainer's. Returns MON_GIVEN_TO_PARTY, MON_GIVEN_TO_PC or
// MON_CANT_GIVE.
u8 GiveSnaggedMonToPlayer(struct Pokemon *mon)
{
    s32 i;

    SetBoxMonOtIdReencrypt(&mon->box, T1_READ_32(gSaveBlock2Ptr->playerTrainerId));

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (GetMonData(&gPlayerParty[i], MON_DATA_SPECIES, NULL) == SPECIES_NONE)
            break;
    }
    if (i >= PARTY_SIZE)
        return SendMonToPC(mon);

    CopyMon(&gPlayerParty[i], mon, sizeof(*mon));
    gPlayerPartyCount = i + 1;
    return MON_GIVEN_TO_PARTY;
}
