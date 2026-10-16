JohtoRoute31_MapScripts::
    .byte 0

JohtoRoute31_Wade::
    trainerbattle_single TRAINER_JOHTO_WADE, JohtoRoute31_Text_WadeIntro, JohtoRoute31_Text_WadeDefeat
    msgbox JohtoRoute31_Text_WadeAfter, MSGBOX_AUTOCLOSE
    end

JohtoRoute31_RouteSign::
    msgbox JohtoRoute31_Text_RouteSign, MSGBOX_NPC
    end

JohtoRoute31_Traveler::
    msgbox JohtoRoute31_Text_Traveler, MSGBOX_NPC
    end
