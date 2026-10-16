GoldenrodUnderground_Basement_MapScripts::
    .byte 0

GoldenrodUnderground_Basement_Silver::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodUnderground_Basement_SilverBefore
    goto_if_defeated TRAINER_JOHTO_SILVER_UNDERGROUND, GoldenrodUnderground_Basement_SilverVictory
    trainerbattle_single TRAINER_JOHTO_SILVER_UNDERGROUND, GoldenrodUnderground_Basement_Text_SilverIntro, GoldenrodUnderground_Basement_Text_SilverDefeat, GoldenrodUnderground_Basement_SilverVictory, NO_MUSIC
    goto GoldenrodUnderground_Basement_SilverVictory
GoldenrodUnderground_Basement_SilverVictory::
    msgbox GoldenrodUnderground_Basement_Text_SilverAfter
    setflag FLAG_HIDE_JOHTO_RADIO_SILVER
    removeobject LOCALID_RADIO_SILVER
    release
    end
GoldenrodUnderground_Basement_SilverBefore::
    msgbox GoldenrodUnderground_Basement_Text_SilverBefore
    release
    end

GoldenrodUnderground_Basement_WarehouseGate::
lockall
    goto_if_not_defeated TRAINER_JOHTO_SILVER_UNDERGROUND, GoldenrodUnderground_Basement_WarehouseGateClosed
    releaseall
    warp MAP_GOLDENROD_WAREHOUSE, 0
    waitstate
    end
GoldenrodUnderground_Basement_WarehouseGateClosed::
    msgbox GoldenrodUnderground_Basement_Text_WarehouseGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, GoldenrodUnderground_Basement_WarehouseGateBack
    waitmovement 0
    releaseall
    end
GoldenrodUnderground_Basement_WarehouseGateBack:
    walk_right
    step_end
