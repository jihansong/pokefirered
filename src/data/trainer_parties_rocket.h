// Thunder Yellow v0.9.0: TEAM ROCKET trio battles that had no trainer before
// (constants/opponents_rocket.h). MEOWTH is always last: the prize money
// comes from the last party member's level.

// #1 VIRIDIAN POKéMON CENTER: MEOWTH sizes up PIKACHU on its own
static const struct TrainerMonNoItemCustomMoves sParty_JessieJamesViridianPC[] = {
    {
        .iv = 0,
        .lvl = 5,
        .species = SPECIES_MEOWTH,
        .moves = {MOVE_SCRATCH, MOVE_GROWL, MOVE_PAY_DAY, MOVE_NONE},
    },
};

// #12 INDIGO PLATEAU: the whole team, before any CHAMPION challenge
static const struct TrainerMonNoItemCustomMoves sParty_JessieJamesIndigo[] = {
    {
        .iv = 0,
        .lvl = 53,
        .species = SPECIES_ARBOK,
        .moves = {MOVE_SLUDGE_BOMB, MOVE_BITE, MOVE_GLARE, MOVE_IRON_TAIL},
    },
    {
        .iv = 0,
        .lvl = 53,
        .species = SPECIES_WEEZING,
        .moves = {MOVE_SLUDGE_BOMB, MOVE_FLAMETHROWER, MOVE_SMOKESCREEN, MOVE_SHADOW_BALL},
    },
    {
        .iv = 0,
        .lvl = 52,
        .species = SPECIES_VICTREEBEL,
        .moves = {MOVE_GIGA_DRAIN, MOVE_SLUDGE_BOMB, MOVE_RAZOR_LEAF, MOVE_SLEEP_POWDER},
    },
    {
        .iv = 0,
        .lvl = 52,
        .species = SPECIES_LICKITUNG,
        .moves = {MOVE_SLAM, MOVE_KNOCK_OFF, MOVE_SUPERSONIC, MOVE_ICE_BEAM},
    },
    {
        .iv = 0,
        .lvl = 52,
        .species = SPECIES_GYARADOS,
        .moves = {MOVE_WATERFALL, MOVE_BITE, MOVE_TWISTER, MOVE_DRAGON_DANCE},
    },
    {
        .iv = 0,
        .lvl = 55,
        .species = SPECIES_MEOWTH,
        .moves = {MOVE_PAY_DAY, MOVE_SLASH, MOVE_FAKE_OUT, MOVE_SHADOW_BALL},
    },
};
