DragonDen_1F_MapScripts::
    .byte 0

DragonDen_1F_TrialGate::
lockall
    goto_if_set FLAG_JOHTO_CLAIR_DEFEATED, DragonDen_1F_TrialGateOpen
    msgbox DragonDen_1F_Text_TrialGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, DragonDen_1F_TrialGateBack
    waitmovement 0
    releaseall
    end
DragonDen_1F_TrialGateOpen::
    releaseall
    warp MAP_DRAGON_DEN_SHRINE, 1
    waitstate
    end
DragonDen_1F_TrialGateBack:
    walk_down
    step_end
