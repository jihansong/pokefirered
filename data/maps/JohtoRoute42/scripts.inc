JohtoRoute42_MapScripts::
    .byte 0

JohtoRoute42_Hiker::
msgbox JohtoRoute42_Text_Hiker, MSGBOX_NPC
    end

JohtoRoute42_HARRISON::
trainerbattle_single TRAINER_JOHTO_HARRISON, JohtoRoute42_Text_HARRISONIntro, JohtoRoute42_Text_HARRISONDefeat
    msgbox JohtoRoute42_Text_HARRISONAfter, MSGBOX_NPC
    end
