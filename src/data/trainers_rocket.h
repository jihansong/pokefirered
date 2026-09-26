// Thunder Yellow v0.9.0: TEAM ROCKET trio battles that had no trainer before
// (constants/opponents_rocket.h, parties in trainer_parties_rocket.h).

    [TRAINER_JESSIE_JAMES_VIRIDIAN_PC] = {
        .trainerClass = TRAINER_CLASS_TEAM_ROCKET,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_AQUA,
        .trainerPic = TRAINER_PIC_JESSIE_JAMES,
        .trainerName = _("JESSIE&JAMES"),
        .items = {},
        .doubleBattle = FALSE,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
        .party = NO_ITEM_CUSTOM_MOVES(sParty_JessieJamesViridianPC),
    },
    [TRAINER_JESSIE_JAMES_INDIGO] = {
        .trainerClass = TRAINER_CLASS_TEAM_ROCKET,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_AQUA,
        .trainerPic = TRAINER_PIC_JESSIE_JAMES,
        .trainerName = _("JESSIE&JAMES"),
        .items = {},
        .doubleBattle = TRUE,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
        .party = NO_ITEM_CUSTOM_MOVES(sParty_JessieJamesIndigo),
    },
