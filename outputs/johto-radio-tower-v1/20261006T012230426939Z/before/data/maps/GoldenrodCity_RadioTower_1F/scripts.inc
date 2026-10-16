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
