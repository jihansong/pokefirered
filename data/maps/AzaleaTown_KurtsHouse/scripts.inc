AzaleaTown_KurtsHouse_MapScripts::
    .byte 0

AzaleaTown_KurtsHouse_Kurt::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_SLOWPOKE_WELL_CLEARED, AzaleaTown_KurtsHouse_Report
    goto_if_set FLAG_JOHTO_KURT_RESCUE_REQUESTED, AzaleaTown_KurtsHouse_Wait
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, AzaleaTown_KurtsHouse_BeforeElm
    msgbox AzaleaTown_KurtsHouse_Text_Request
    setflag FLAG_JOHTO_KURT_RESCUE_REQUESTED
    release
    end
AzaleaTown_KurtsHouse_Report::
    goto_if_set FLAG_JOHTO_KURT_REPORT_DELIVERED, AzaleaTown_KurtsHouse_Reward
    msgbox AzaleaTown_KurtsHouse_Text_Report
    setflag FLAG_JOHTO_KURT_REPORT_DELIVERED
AzaleaTown_KurtsHouse_Reward::
    goto_if_set FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT, AzaleaTown_KurtsHouse_After
    checkitemspace ITEM_NET_BALL, 3
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_KurtsHouse_BagFull
    giveitem ITEM_NET_BALL, 3
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_KurtsHouse_BagFull
    setflag FLAG_JOHTO_GOT_NET_BALLS_FROM_KURT
AzaleaTown_KurtsHouse_After::
    msgbox AzaleaTown_KurtsHouse_Text_After
    release
    end
AzaleaTown_KurtsHouse_BagFull::
    msgbox AzaleaTown_KurtsHouse_Text_BagFull
    release
    end
AzaleaTown_KurtsHouse_Wait::
    msgbox AzaleaTown_KurtsHouse_Text_Wait
    release
    end
AzaleaTown_KurtsHouse_BeforeElm::
    msgbox AzaleaTown_KurtsHouse_Text_BeforeElm
    release
    end

AzaleaTown_KurtsHouse_Granddaughter::
    msgbox AzaleaTown_KurtsHouse_Text_Granddaughter, MSGBOX_NPC
    end
