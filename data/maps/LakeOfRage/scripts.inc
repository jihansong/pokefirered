LakeOfRage_MapScripts::
    .byte 0

LakeOfRage_RedGyarados::
lock
    goto_if_set FLAG_JOHTO_RED_GYARADOS_RESOLVED, LakeOfRage_GyaradosAfter
    msgbox LakeOfRage_Text_Gyarados
    setwildbattle SPECIES_GYARADOS, 30
    special MakeScriptedWildMonShiny
    playmoncry SPECIES_GYARADOS, CRY_MODE_ENCOUNTER
    waitmoncry
    setflag FLAG_SYS_SPECIAL_WILD_BATTLE
    dowildbattle
    clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
    specialvar VAR_RESULT, GetBattleOutcome
    goto_if_eq VAR_RESULT, B_OUTCOME_WON, LakeOfRage_GyaradosClear
    goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, LakeOfRage_GyaradosClear
    release
    end
LakeOfRage_GyaradosClear::
    setflag FLAG_JOHTO_RED_GYARADOS_RESOLVED
    removeobject 1
    msgbox LakeOfRage_Text_GyaradosClear
LakeOfRage_GyaradosAfter::
    release
    end

LakeOfRage_Lance::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, LakeOfRage_LanceAfter
    goto_if_unset FLAG_JOHTO_RED_GYARADOS_RESOLVED, LakeOfRage_LanceBefore
    setflag FLAG_JOHTO_LANCE_INVESTIGATION_JOINED
    goto_if_set FLAG_JOHTO_RED_SCALE_RECEIVED, LakeOfRage_LanceJoined
    giveitem ITEM_RED_SCALE
    goto_if_eq VAR_RESULT, FALSE, LakeOfRage_LanceFull
    setflag FLAG_JOHTO_RED_SCALE_RECEIVED
LakeOfRage_LanceJoined::
    msgbox LakeOfRage_Text_LanceJoined
    release
    end
LakeOfRage_LanceFull::
    msgbox LakeOfRage_Text_LanceFull
    release
    end
LakeOfRage_LanceBefore::
    msgbox LakeOfRage_Text_LanceBefore
    release
    end
LakeOfRage_LanceAfter::
    msgbox LakeOfRage_Text_LanceAfter
    release
    end
