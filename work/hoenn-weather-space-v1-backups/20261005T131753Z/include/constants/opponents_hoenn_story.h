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

#endif  // GUARD_CONSTANTS_OPPONENTS_HOENN_STORY_H
