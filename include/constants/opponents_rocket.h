#ifndef GUARD_CONSTANTS_OPPONENTS_ROCKET_H
#define GUARD_CONSTANTS_OPPONENTS_ROCKET_H

// Thunder Yellow v0.9.0: TEAM ROCKET trio battles that had no trainer of their
// own before. They sit past the Hoenn story and rematch ranges, so their
// defeated bits live in gSaveBlock2Ptr->hoennTrainerFlags (1024 bits).
//
//   +768 .. +783   TEAM ROCKET trio appearances (+770 .. +783 kept for JOHTO
//                  and HOENN ones)

#define ROCKET_TRAINERS_START               (HOENN_TRAINERS_START + 768)
#define TRAINER_JESSIE_JAMES_VIRIDIAN_PC    (HOENN_TRAINERS_START + 768)
#define TRAINER_JESSIE_JAMES_INDIGO         (HOENN_TRAINERS_START + 769)
#define ROCKET_TRAINERS_END                 (HOENN_TRAINERS_START + 783)

#endif  // GUARD_CONSTANTS_OPPONENTS_ROCKET_H
