JohtoRocketHQ_B3F_MapScripts::
    .byte 0

JohtoRocketHQ_B3F_ARIANA::
trainerbattle_single TRAINER_JOHTO_ARIANA, JohtoRocketHQ_B3F_Text_ARIANAIntro, JohtoRocketHQ_B3F_Text_ARIANADefeat
    msgbox JohtoRocketHQ_B3F_Text_ARIANAAfter, MSGBOX_NPC
    end

JohtoRocketHQ_B3F_Electrode1::
lock
    goto_if_set FLAG_JOHTO_HQ_ELECTRODE1_CLEARED, JohtoRocketHQ_B3F_Electrode1After
    goto_if_defeated TRAINER_JOHTO_ARIANA, JohtoRocketHQ_B3F_Electrode1Battle
    msgbox JohtoRocketHQ_B3F_Text_ExecutiveFirst
    release
    end
JohtoRocketHQ_B3F_Electrode1Battle::
    setwildbattle SPECIES_ELECTRODE, 23
    playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, JohtoRocketHQ_B3F_Electrode1Clear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, JohtoRocketHQ_B3F_Electrode1Clear
    release
    end
JohtoRocketHQ_B3F_Electrode1Clear::
    setflag FLAG_JOHTO_HQ_ELECTRODE1_CLEARED
    removeobject 1
JohtoRocketHQ_B3F_Electrode1After::
    release
    end

JohtoRocketHQ_B3F_Electrode2::
lock
    goto_if_set FLAG_JOHTO_HQ_ELECTRODE2_CLEARED, JohtoRocketHQ_B3F_Electrode2After
    goto_if_defeated TRAINER_JOHTO_ARIANA, JohtoRocketHQ_B3F_Electrode2Battle
    msgbox JohtoRocketHQ_B3F_Text_ExecutiveFirst
    release
    end
JohtoRocketHQ_B3F_Electrode2Battle::
    setwildbattle SPECIES_ELECTRODE, 23
    playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, JohtoRocketHQ_B3F_Electrode2Clear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, JohtoRocketHQ_B3F_Electrode2Clear
    release
    end
JohtoRocketHQ_B3F_Electrode2Clear::
    setflag FLAG_JOHTO_HQ_ELECTRODE2_CLEARED
    removeobject 2
JohtoRocketHQ_B3F_Electrode2After::
    release
    end

JohtoRocketHQ_B3F_Electrode3::
lock
    goto_if_set FLAG_JOHTO_HQ_ELECTRODE3_CLEARED, JohtoRocketHQ_B3F_Electrode3After
    goto_if_defeated TRAINER_JOHTO_ARIANA, JohtoRocketHQ_B3F_Electrode3Battle
    msgbox JohtoRocketHQ_B3F_Text_ExecutiveFirst
    release
    end
JohtoRocketHQ_B3F_Electrode3Battle::
    setwildbattle SPECIES_ELECTRODE, 23
    playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, JohtoRocketHQ_B3F_Electrode3Clear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, JohtoRocketHQ_B3F_Electrode3Clear
    release
    end
JohtoRocketHQ_B3F_Electrode3Clear::
    setflag FLAG_JOHTO_HQ_ELECTRODE3_CLEARED
    removeobject 3
JohtoRocketHQ_B3F_Electrode3After::
    release
    end

JohtoRocketHQ_B3F_Lance::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE1_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE2_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_unset FLAG_JOHTO_HQ_ELECTRODE3_CLEARED, JohtoRocketHQ_B3F_NotReady
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, JohtoRocketHQ_B3F_Reward
    setflag FLAG_JOHTO_ROCKET_HQ_CLEARED
JohtoRocketHQ_B3F_Reward::
    goto_if_set FLAG_JOHTO_RED_SCALE_RECEIVED, JohtoRocketHQ_B3F_TM
    giveitem ITEM_RED_SCALE
    goto_if_eq VAR_RESULT, FALSE, JohtoRocketHQ_B3F_ScaleFull
    setflag FLAG_JOHTO_RED_SCALE_RECEIVED
JohtoRocketHQ_B3F_TM::
    goto_if_set FLAG_JOHTO_LANCE_TM24_RECEIVED, JohtoRocketHQ_B3F_After
    giveitem ITEM_TM24
    goto_if_eq VAR_RESULT, FALSE, JohtoRocketHQ_B3F_Full
    setflag FLAG_JOHTO_LANCE_TM24_RECEIVED
JohtoRocketHQ_B3F_After::
    msgbox JohtoRocketHQ_B3F_Text_After
    release
    end
JohtoRocketHQ_B3F_ScaleFull::
    msgbox JohtoRocketHQ_B3F_Text_ScaleFull
    release
    end
JohtoRocketHQ_B3F_Full::
    msgbox JohtoRocketHQ_B3F_Text_Full
    release
    end
JohtoRocketHQ_B3F_NotReady::
    msgbox JohtoRocketHQ_B3F_Text_NotReady
    release
    end
