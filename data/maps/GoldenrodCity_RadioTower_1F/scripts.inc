GoldenrodCity_RadioTower_1F_MapScripts::
    .byte 0

GoldenrodCity_RadioTower_1F_ResearchDesk::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED, GoldenrodCity_RadioTower_1F_Registered
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, GoldenrodCity_RadioTower_1F_BeforeElm
    msgbox GoldenrodCity_RadioTower_1F_Text_Register
    setflag FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED
    release
    end
GoldenrodCity_RadioTower_1F_Registered::
    msgbox GoldenrodCity_RadioTower_1F_Text_Registered
    release
    end
GoldenrodCity_RadioTower_1F_BeforeElm::
    msgbox GoldenrodCity_RadioTower_1F_Text_BeforeElm
    release
    end

GoldenrodCity_RadioTower_1F_Reception::
msgbox GoldenrodCity_RadioTower_1F_Text_Reception, MSGBOX_NPC
    end
@ JOHTO_RADIO_TOWER_RESCUE_V1 LOBBY

GoldenrodCity_RadioTower_1F_BroadcastClerk::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodCity_RadioTower_1F_BroadcastClerkAfter
    goto_if_unset FLAG_JOHTO_BADGE07_GET, GoldenrodCity_RadioTower_1F_BroadcastClerkBefore
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkAlarm
    release
    end
GoldenrodCity_RadioTower_1F_BroadcastClerkBefore::
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkBefore
    release
    end
GoldenrodCity_RadioTower_1F_BroadcastClerkAfter::
    msgbox GoldenrodCity_RadioTower_1F_Text_BroadcastClerkAfter
    release
    end

GoldenrodCity_RadioTower_1F_UpperGate::
lockall
    goto_if_unset FLAG_JOHTO_BADGE07_GET, GoldenrodCity_RadioTower_1F_UpperGateClosed
    releaseall
    special SetOrdinaryWarpTransition
    warp MAP_GOLDENROD_CITY_RADIO_TOWER_2F, 1
    waitstate
    end
GoldenrodCity_RadioTower_1F_UpperGateClosed::
    msgbox GoldenrodCity_RadioTower_1F_Text_UpperGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, GoldenrodCity_RadioTower_1F_UpperGateBack
    waitmovement 0
    releaseall
    end
GoldenrodCity_RadioTower_1F_UpperGateBack:
    walk_right
    step_end

GoldenrodCity_RadioTower_1F_RadioNotice::
msgbox GoldenrodCity_RadioTower_1F_Text_RadioNotice, MSGBOX_NPC
    end
