#ifndef GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H
#define GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H

// Numbers reserved for trainers the Hoenn story adds on its own, past the
// imported ones (0..519) and the INDIGO PLATEAU tournament entrants (520..535).
// Their defeated bits sit in gSaveBlock2Ptr->hoennTrainerFlags, which holds
// 1024 bits, so the whole range below fits without touching the save layout.
//
//   +536 .. +639   new story trainers, one release at a time
//   +640 .. +767   rematch versions of story trainers
//   +768 .. +783   TEAM ROCKET trio appearances (opponents_rocket.h)
//
// The import script only ever rewrites the block between the BEGIN/END markers
// in opponents.h, so names added here survive a re-import.

#define HOENN_STORY_TRAINERS_START   (HOENN_TRAINERS_START + 536)
#define HOENN_STORY_TRAINERS_END     (HOENN_TRAINERS_START + 639)
#define HOENN_REMATCH_TRAINERS_START (HOENN_TRAINERS_START + 640)
#define HOENN_REMATCH_TRAINERS_END   (HOENN_TRAINERS_START + 767)

// Stage 1 (Slateport harbour) adds no trainers of its own: the museum grunts
// and ARCHIE use the imported data, and ARCHIE only warns the player.

#define TRAINER_HOENN_TABITHA_SPACE_CENTER (HOENN_TRAINERS_START + 536)
#define TRAINER_HOENN_MAXIE_SPACE_CENTER (HOENN_TRAINERS_START + 537)
// THYL_WALLY_FINAL_V1
#define TRAINER_HOENN_WALLY_VICTORY_ROAD_FINAL (HOENN_TRAINERS_START + 538)
// THYL_VICTORY_ROAD_1F_TRAINERS_V1
#define TRAINER_HOENN_EDGAR_VICTORY_ROAD (HOENN_TRAINERS_START + 539)
#define TRAINER_HOENN_HOPE_VICTORY_ROAD (HOENN_TRAINERS_START + 540)
#define TRAINER_HOENN_ALBERT_VICTORY_ROAD (HOENN_TRAINERS_START + 541)
#define TRAINER_HOENN_KATELYNN_VICTORY_ROAD (HOENN_TRAINERS_START + 542)
#define TRAINER_HOENN_QUINCY_VICTORY_ROAD (HOENN_TRAINERS_START + 543)
#define TRAINER_HOENN_SPACE_FLIGHT_CHECK (HOENN_TRAINERS_START + 544)
#define TRAINER_HOENN_SPACE_SYSTEMS_CHECK (HOENN_TRAINERS_START + 545)
#endif  // GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H
