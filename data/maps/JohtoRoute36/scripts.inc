JohtoRoute36_MapScripts::
    .byte 0

JohtoRoute36_Sudowoodo::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_SUDOWOODO_CLEARED, JohtoRoute36_SudowoodoDone
    goto_if_unset FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED, JohtoRoute36_NeedWater
    msgbox JohtoRoute36_Text_Water
    setwildbattle SPECIES_SUDOWOODO, 20
    waitse
    playmoncry SPECIES_SUDOWOODO, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, JohtoRoute36_SudowoodoClear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, JohtoRoute36_SudowoodoClear
    release
    end
JohtoRoute36_SudowoodoClear::
    setflag FLAG_JOHTO_SUDOWOODO_CLEARED
    removeobject 1
    msgbox JohtoRoute36_Text_Clear
    release
    end
JohtoRoute36_NeedWater::
    msgbox JohtoRoute36_Text_NeedWater
    release
    end
JohtoRoute36_SudowoodoDone::
    release
    end

JohtoRoute36_Worker::
msgbox JohtoRoute36_Text_Worker, MSGBOX_NPC
    end

JohtoRoute36_IVAN::
trainerbattle_single TRAINER_JOHTO_IVAN, JohtoRoute36_Text_IVANIntro, JohtoRoute36_Text_IVANDefeat
    msgbox JohtoRoute36_Text_IVANAfter, MSGBOX_AUTOCLOSE
    end
