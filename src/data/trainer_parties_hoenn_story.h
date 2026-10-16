// Hoenn Space Center encounters; native species and graphics.
static const struct TrainerMonNoItemDefaultMoves sHoennParty_TabithaSpaceCenter[] = {
    {
    .iv = 75,
    .lvl = 36,
    .species = SPECIES_NUMEL,
    },
    {
    .iv = 75,
    .lvl = 38,
    .species = SPECIES_MIGHTYENA,
    },
    {
    .iv = 75,
    .lvl = 40,
    .species = SPECIES_ZUBAT,
    },
    {
    .iv = 75,
    .lvl = 42,
    .species = SPECIES_CAMERUPT,
    }
};
static const struct TrainerMonNoItemDefaultMoves sHoennParty_MaxieSpaceCenter[] = {
    {
    .iv = 150,
    .lvl = 42,
    .species = SPECIES_MIGHTYENA,
    },
    {
    .iv = 150,
    .lvl = 43,
    .species = SPECIES_CROBAT,
    },
    {
    .iv = 150,
    .lvl = 44,
    .species = SPECIES_CAMERUPT,
    }
};

// THYL_WALLY_FINAL_V1
static const struct TrainerMonNoItemCustomMoves sHoennParty_WallyVictoryRoadFinal[] = {
    {
    .iv = 150,
    .lvl = 44,
    .species = SPECIES_ALTARIA,
    .moves = {MOVE_AERIAL_ACE, MOVE_SAFEGUARD, MOVE_DRAGON_BREATH, MOVE_DRAGON_DANCE}
    },
    {
    .iv = 150,
    .lvl = 43,
    .species = SPECIES_DELCATTY,
    .moves = {MOVE_SING, MOVE_ASSIST, MOVE_CHARM, MOVE_FAINT_ATTACK}
    },
    {
    .iv = 150,
    .lvl = 44,
    .species = SPECIES_ROSELIA,
    .moves = {MOVE_MAGICAL_LEAF, MOVE_LEECH_SEED, MOVE_GIGA_DRAIN, MOVE_TOXIC}
    },
    {
    .iv = 150,
    .lvl = 41,
    .species = SPECIES_MAGNETON,
    .moves = {MOVE_SUPERSONIC, MOVE_THUNDERBOLT, MOVE_TRI_ATTACK, MOVE_SCREECH}
    },
    {
    .iv = 250,
    .lvl = 45,
    .species = SPECIES_GARDEVOIR,
    .moves = {MOVE_DOUBLE_TEAM, MOVE_CALM_MIND, MOVE_PSYCHIC, MOVE_FUTURE_SIGHT}
    }
};

// THYL_VICTORY_ROAD_1F_TRAINERS_V1
static const struct TrainerMonNoItemDefaultMoves sHoennParty_EdgarVictoryRoad[] = {
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_CACTURNE,
    },
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_PELIPPER,
    }
};
static const struct TrainerMonNoItemDefaultMoves sHoennParty_HopeVictoryRoad[] = {
    {
    .iv = 100,
    .lvl = 45,
    .species = SPECIES_ROSELIA,
    }
};
static const struct TrainerMonNoItemDefaultMoves sHoennParty_AlbertVictoryRoad[] = {
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_MAGNETON,
    },
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_MUK,
    }
};
static const struct TrainerMonNoItemCustomMoves sHoennParty_KatelynnVictoryRoad[] = {
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_GARDEVOIR,
    .moves = {MOVE_SKILL_SWAP, MOVE_PSYCHIC, MOVE_THUNDERBOLT, MOVE_CALM_MIND}
    },
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_SLAKING,
    .moves = {MOVE_EARTHQUAKE, MOVE_SHADOW_BALL, MOVE_AERIAL_ACE, MOVE_BRICK_BREAK}
    }
};
static const struct TrainerMonNoItemCustomMoves sHoennParty_QuincyVictoryRoad[] = {
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_SLAKING,
    .moves = {MOVE_ATTRACT, MOVE_ICE_BEAM, MOVE_THUNDERBOLT, MOVE_FLAMETHROWER}
    },
    {
    .iv = 100,
    .lvl = 43,
    .species = SPECIES_DUSCLOPS,
    .moves = {MOVE_SKILL_SWAP, MOVE_PROTECT, MOVE_WILL_O_WISP, MOVE_TOXIC}
    }
};
