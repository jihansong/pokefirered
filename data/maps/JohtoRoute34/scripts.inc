JohtoRoute34_MapScripts::
    .byte 0

JohtoRoute34_Todd::
trainerbattle_single TRAINER_JOHTO_TODD, JohtoRoute34_Text_ToddIntro, JohtoRoute34_Text_ToddDefeat
    msgbox JohtoRoute34_Text_ToddAfter, MSGBOX_AUTOCLOSE
    end

JohtoRoute34_Gina::
trainerbattle_single TRAINER_JOHTO_GINA, JohtoRoute34_Text_GinaIntro, JohtoRoute34_Text_GinaDefeat
    msgbox JohtoRoute34_Text_GinaAfter, MSGBOX_AUTOCLOSE
    end

JohtoRoute34_Brandon::
trainerbattle_single TRAINER_JOHTO_BRANDON, JohtoRoute34_Text_BrandonIntro, JohtoRoute34_Text_BrandonDefeat
    msgbox JohtoRoute34_Text_BrandonAfter, MSGBOX_AUTOCLOSE
    end

JohtoRoute34_RouteSign::
msgbox JohtoRoute34_Text_RouteSign, MSGBOX_NPC
    end

JohtoRoute34_DayCareSign::
msgbox JohtoRoute34_Text_DayCareSign, MSGBOX_NPC
    end
