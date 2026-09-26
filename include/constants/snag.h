#ifndef GUARD_CONSTANTS_SNAG_H
#define GUARD_CONSTANTS_SNAG_H

// Trainer-battle snagging (v0.10.0). When the player takes a POKéMON from the
// Kanto rival, Tournament BLUE or JESSIE & JAMES, the evolution family's slot
// flag is set and that family stays out of their later parties (src/snag.c).
// The slots are reserved Hoenn flags 0x780..0x79F (gSaveBlock2Ptr->hoennFlags),
// so nothing in the save moves; old saves read as "nothing taken".
// tools/qa/snagcheck.py checks every species in those parties has a slot.

#define SNAG_FLAGS_START                (HOENN_FLAGS_START + 0x780)
#define SNAG_SLOT_COUNT                 32

// The rival's families: slots 0..15 (13..15 spare)
#define SNAG_SLOT_RIVAL_SPEAROW         0
#define SNAG_SLOT_RIVAL_RATTATA         1
#define SNAG_SLOT_RIVAL_SANDSHREW       2
#define SNAG_SLOT_RIVAL_EEVEE           3
#define SNAG_SLOT_RIVAL_SHELLDER        4
#define SNAG_SLOT_RIVAL_VULPIX          5
#define SNAG_SLOT_RIVAL_MAGNEMITE       6
#define SNAG_SLOT_RIVAL_ABRA            7
#define SNAG_SLOT_RIVAL_EXEGGCUTE       8
#define SNAG_SLOT_RIVAL_PIDGEY          9
#define SNAG_SLOT_RIVAL_RHYHORN         10
#define SNAG_SLOT_RIVAL_GROWLITHE       11
#define SNAG_SLOT_RIVAL_SQUIRTLE        12
#define SNAG_SLOTS_RIVAL_FIRST          0
#define SNAG_SLOTS_RIVAL_END            16

// JESSIE & JAMES's families: slots 16..31 (22..31 spare). MEOWTH has none: it
// can't be taken.
#define SNAG_SLOT_ROCKET_EKANS          16
#define SNAG_SLOT_ROCKET_KOFFING        17
#define SNAG_SLOT_ROCKET_MAGIKARP       18
#define SNAG_SLOT_ROCKET_BELLSPROUT     19
#define SNAG_SLOT_ROCKET_LICKITUNG      20
#define SNAG_SLOT_ROCKET_WOBBUFFET      21
#define SNAG_SLOTS_ROCKET_FIRST         16
#define SNAG_SLOTS_ROCKET_END           32

#define SNAG_SLOT_NONE                  0xFF

#define FLAG_SNAG_RIVAL_SPEAROW         (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_SPEAROW)
#define FLAG_SNAG_RIVAL_RATTATA         (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_RATTATA)
#define FLAG_SNAG_RIVAL_SANDSHREW       (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_SANDSHREW)
#define FLAG_SNAG_RIVAL_EEVEE           (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_EEVEE)
#define FLAG_SNAG_RIVAL_SHELLDER        (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_SHELLDER)
#define FLAG_SNAG_RIVAL_VULPIX          (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_VULPIX)
#define FLAG_SNAG_RIVAL_MAGNEMITE       (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_MAGNEMITE)
#define FLAG_SNAG_RIVAL_ABRA            (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_ABRA)
#define FLAG_SNAG_RIVAL_EXEGGCUTE       (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_EXEGGCUTE)
#define FLAG_SNAG_RIVAL_PIDGEY          (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_PIDGEY)
#define FLAG_SNAG_RIVAL_RHYHORN         (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_RHYHORN)
#define FLAG_SNAG_RIVAL_GROWLITHE       (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_GROWLITHE)
#define FLAG_SNAG_RIVAL_SQUIRTLE        (SNAG_FLAGS_START + SNAG_SLOT_RIVAL_SQUIRTLE)
#define FLAG_SNAG_ROCKET_EKANS          (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_EKANS)
#define FLAG_SNAG_ROCKET_KOFFING        (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_KOFFING)
#define FLAG_SNAG_ROCKET_MAGIKARP       (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_MAGIKARP)
#define FLAG_SNAG_ROCKET_BELLSPROUT     (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_BELLSPROUT)
#define FLAG_SNAG_ROCKET_LICKITUNG      (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_LICKITUNG)
#define FLAG_SNAG_ROCKET_WOBBUFFET      (SNAG_FLAGS_START + SNAG_SLOT_ROCKET_WOBBUFFET)

// Whose parties remember what was taken (GetSnagGroup)
#define SNAG_GROUP_NONE                 0
#define SNAG_GROUP_RIVAL                1
#define SNAG_GROUP_ROCKET               2

// cMULTISTRING_CHOOSER after the snagged POKéMON is given (stage 2's
// snaggivemon): party, or the gCaughtMonStringIds cases for the PC.
#define SNAG_MSG_PARTY                  0xFF

#endif // GUARD_CONSTANTS_SNAG_H
