IlexForest_AzaleaGate_MapScripts::
    .byte 0

IlexForest_AzaleaGate_Silver::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_SILVER_AZALEA_DEFEATED, IlexForest_AzaleaGate_SilverDone
    goto_if_unset FLAG_JOHTO_BADGE02_GET, IlexForest_AzaleaGate_SilverNotReady
    trainerbattle_single TRAINER_JOHTO_SILVER_AZALEA, IlexForest_AzaleaGate_Text_SilverIntro, IlexForest_AzaleaGate_Text_SilverDefeat, IlexForest_AzaleaGate_SilverVictory, NO_MUSIC
    goto IlexForest_AzaleaGate_SilverVictory
IlexForest_AzaleaGate_SilverVictory::
    msgbox IlexForest_AzaleaGate_Text_SilverAfter
    setflag FLAG_JOHTO_SILVER_AZALEA_DEFEATED
    removeobject 1
    release
    end
IlexForest_AzaleaGate_SilverNotReady::
    msgbox IlexForest_AzaleaGate_Text_SilverNotReady
    release
    end
IlexForest_AzaleaGate_SilverDone::
    release
    end

IlexForest_AzaleaGate_CheckPass::
goto_if_set FLAG_JOHTO_SILVER_AZALEA_DEFEATED, IlexForest_AzaleaGate_Pass
    lockall
    msgbox IlexForest_AzaleaGate_Text_Stop
    applymovement LOCALID_PLAYER, IlexForest_AzaleaGate_StepBack
    waitmovement 0
    releaseall
    end
IlexForest_AzaleaGate_Pass::
    setvar VAR_TEMP_0, 1
    end
IlexForest_AzaleaGate_StepBack:
    walk_down
    step_end

IlexForest_AzaleaGate_Officer::
msgbox IlexForest_AzaleaGate_Text_Officer, MSGBOX_NPC
    end
