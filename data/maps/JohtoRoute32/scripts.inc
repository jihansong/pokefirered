JohtoRoute32_MapScripts::
    .byte 0

JohtoRoute32_CheckBadge::
    goto_if_set FLAG_JOHTO_BADGE01_GET, JohtoRoute32_ClearPath
    lockall
    msgbox JohtoRoute32_Text_BadgeNeeded
    applymovement LOCALID_PLAYER, JohtoRoute32_MoveBack
    waitmovement 0
    releaseall
    end
JohtoRoute32_ClearPath::
    setvar VAR_TEMP_0, 1
    end
JohtoRoute32_MoveBack:
    walk_up
    step_end
JohtoRoute32_Russell::
    trainerbattle_single TRAINER_JOHTO_RUSSELL, JohtoRoute32_Text_Intro, JohtoRoute32_Text_Defeat
    msgbox JohtoRoute32_Text_After, MSGBOX_AUTOCLOSE
    end

JohtoRoute32_RouteSign::
    msgbox JohtoRoute32_Text_RouteSign, MSGBOX_NPC
    end

JohtoRoute32_CaveSign::
    msgbox JohtoRoute32_Text_CaveSign, MSGBOX_NPC
    end

JohtoRoute32_Researcher::
    msgbox JohtoRoute32_Text_Researcher, MSGBOX_NPC
    end
