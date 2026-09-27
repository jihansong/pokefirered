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

// v0.11.0 PETALBURG WOODS (Hoenn stage 3), a double battle. The anime's HOENN
// team: JESSIE's DUSTOX (the WURMPLE she caught in these woods, grown up) and
// SEVIPER, JAMES's CACTURNE, WOBBUFFET, WEEZING (docs/v0.11.0-plan.md 5.2)
static const struct TrainerMonNoItemCustomMoves sParty_JessieJamesPetalburgWoods[] = {
    {
        .iv = 0,
        .lvl = 64,
        .species = SPECIES_DUSTOX,
        .moves = {MOVE_SILVER_WIND, MOVE_PSYBEAM, MOVE_TOXIC, MOVE_LIGHT_SCREEN},
    },
    {
        .iv = 0,
        .lvl = 64,
        .species = SPECIES_SEVIPER,
        .moves = {MOVE_POISON_FANG, MOVE_CRUNCH, MOVE_GLARE, MOVE_POISON_TAIL},
    },
    {
        .iv = 0,
        .lvl = 64,
        .species = SPECIES_CACTURNE,
        .moves = {MOVE_NEEDLE_ARM, MOVE_FAINT_ATTACK, MOVE_COTTON_SPORE, MOVE_PIN_MISSILE},
    },
    {
        .iv = 0,
        .lvl = 65,
        .species = SPECIES_WOBBUFFET,
        .moves = {MOVE_COUNTER, MOVE_MIRROR_COAT, MOVE_SAFEGUARD, MOVE_DESTINY_BOND},
    },
    {
        .iv = 0,
        .lvl = 65,
        .species = SPECIES_WEEZING,
        .moves = {MOVE_SLUDGE_BOMB, MOVE_FLAMETHROWER, MOVE_SMOKESCREEN, MOVE_SHADOW_BALL},
    },
    {
        .iv = 0,
        .lvl = 67,
        .species = SPECIES_MEOWTH,
        .moves = {MOVE_PAY_DAY, MOVE_SLASH, MOVE_FAKE_OUT, MOVE_SHADOW_BALL},
    },
};
