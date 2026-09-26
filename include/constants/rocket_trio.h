#ifndef GUARD_CONSTANTS_ROCKET_TRIO_H
#define GUARD_CONSTANTS_ROCKET_TRIO_H

// Thunder Yellow v0.9.0: the rewards TEAM ROCKET's trio leave behind.
// Bit numbers for the specials CheckRocketRewardBit, SetRocketRewardBit and
// ClearRocketRewardBit (VAR_0x8004 = bit). Bits 0..15 live in
// VAR_ROCKET_BONUS_GIVEN (1 = the new reward was handed over); bits 16..31 in
// VAR_ROCKET_REWARD_HELD, bit - 16 (1 = the bag was full, so the OFFICER at the
// VIRIDIAN POKéMON CENTER keeps it). The two read the opposite way on purpose:
// a save from before v0.9.0 already has the old rewards (nothing held) and
// none of the new ones (nothing given), and the OFFICER hands those over.

#define ROCKET_BONUS_WATER_STONE    0   // #3  CERULEAN GYM
#define ROCKET_BONUS_SS_ANNE_CANDY  1   // #4  S.S. ANNE, or the VERMILION harbor
#define ROCKET_BONUS_THUNDER_STONE  2   // #5  ROCKET HIDEOUT
#define ROCKET_BONUS_CLEANSE_TAG    3   // #6  POKéMON TOWER
#define ROCKET_BONUS_LEAF_STONE     4   // #7  CELADON GYM
#define ROCKET_BONUS_UP_GRADE       5   // #8  SILPH CO.
#define ROCKET_BONUS_DRAGON_SCALE   6   // #9  SAFARI ZONE gate
#define ROCKET_BONUS_CINNABAR_CANDY 7   // #10 CINNABAR, RARE CANDY x2 (was the MT. MOON fossil not picked)
#define ROCKET_BONUS_GYM_CANDY      8   // #11 VIRIDIAN GYM, RARE CANDY x3
#define ROCKET_BONUS_EEVEE_EGG      9   // #11 VIRIDIAN GYM, an EEVEE EGG
#define ROCKET_BONUS_FIRE_STONE     10  // #12 INDIGO PLATEAU
#define ROCKET_BONUS_NEW_ISLAND     11  // #13 NEW ISLAND, the MEW EGG or RARE CANDY x3

#define ROCKET_HELD_FIRST           16
#define ROCKET_HELD_MYSTIC_WATER    16  // #3
#define ROCKET_HELD_NUGGET          17  // #4
#define ROCKET_HELD_MIRACLE_SEED    18  // #7
#define ROCKET_HELD_DRAGON_FANG     19  // #9
#define ROCKET_HELD_FULL_RESTORE    20  // #12
#define ROCKET_HELD_CARGO_TAG       21  // #13

// VAR_ROCKET_RETRY: the event number (the v0.9.0 plan's #2..#13) of the trio
// battle last lost, so the next try skips the long lines.
#define ROCKET_RETRY_NONE           0

// Whether the player could field two POKéMON when the trio battle began
// (HasEnoughMonsForDoubleBattle, the engine's own test), kept for the coin
// bonus after it. A temp var: it survives the battle and is cleared on warps.
// No other script on the trio's maps uses VAR_TEMP_D.
#define VAR_ROCKET_DOUBLES          VAR_TEMP_D

#endif // GUARD_CONSTANTS_ROCKET_TRIO_H
