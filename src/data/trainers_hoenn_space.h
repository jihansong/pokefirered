// TEAM ORBIT infiltrators reuse their existing trainer IDs and portraits.
    [TRAINER_HOENN_SPACE_FLIGHT_CHECK] =
    {
        .trainerClass = TRAINER_CLASS_COOLTRAINER,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_COOL,
        .trainerPic = TRAINER_PIC_COOLTRAINER_M,
        .trainerName = _("ORBIT IVO"),
        .items = {ITEM_NONE, ITEM_NONE, ITEM_NONE, ITEM_NONE},
        .doubleBattle = FALSE,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
        .party = NO_ITEM_CUSTOM_MOVES(sSpaceParty_FlightCheck),
    },
    [TRAINER_HOENN_SPACE_SYSTEMS_CHECK] =
    {
        .trainerClass = TRAINER_CLASS_SCIENTIST,
        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_COOL,
        .trainerPic = TRAINER_PIC_SCIENTIST,
        .trainerName = _("ORBIT LIORA"),
        .items = {ITEM_NONE, ITEM_NONE, ITEM_NONE, ITEM_NONE},
        .doubleBattle = FALSE,
        .aiFlags = AI_SCRIPT_CHECK_BAD_MOVE | AI_SCRIPT_TRY_TO_FAINT | AI_SCRIPT_CHECK_VIABILITY,
        .party = NO_ITEM_CUSTOM_MOVES(sSpaceParty_SystemsCheck),
    },
