GoldenrodCity_RadioTower_4F_MapScripts::
    .byte 0

GoldenrodCity_RadioTower_4F_ARIANA_RADIO::
trainerbattle_single TRAINER_JOHTO_ARIANA_RADIO, GoldenrodCity_RadioTower_4F_Text_ARIANA_RADIOIntro, GoldenrodCity_RadioTower_4F_Text_ARIANA_RADIODefeat
    msgbox GoldenrodCity_RadioTower_4F_Text_ARIANA_RADIOAfter, MSGBOX_NPC
    end

GoldenrodCity_RadioTower_4F_UpperGate::
lockall
    goto_if_not_defeated TRAINER_JOHTO_ARIANA_RADIO, GoldenrodCity_RadioTower_4F_UpperGateClosed
    releaseall
    special SetOrdinaryWarpTransition
    warp MAP_GOLDENROD_CITY_RADIO_TOWER_5F, 0
    waitstate
    end
GoldenrodCity_RadioTower_4F_UpperGateClosed::
    msgbox GoldenrodCity_RadioTower_4F_Text_UpperGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, GoldenrodCity_RadioTower_4F_UpperGateBack
    waitmovement 0
    releaseall
    end
GoldenrodCity_RadioTower_4F_UpperGateBack:
    walk_right
    step_end
