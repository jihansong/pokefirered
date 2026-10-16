JohtoRoute35_MapScripts::
    .byte 0

JohtoRoute35_RouteSign::
msgbox JohtoRoute35_Text_RouteSign, MSGBOX_NPC
    end

JohtoRoute35_ARNIE::
trainerbattle_single TRAINER_JOHTO_ARNIE, JohtoRoute35_Text_ARNIEIntro, JohtoRoute35_Text_ARNIEDefeat
    msgbox JohtoRoute35_Text_ARNIEAfter, MSGBOX_AUTOCLOSE
    end
