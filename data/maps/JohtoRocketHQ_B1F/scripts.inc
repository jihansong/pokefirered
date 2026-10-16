JohtoRocketHQ_B1F_MapScripts::
    .byte 0

JohtoRocketHQ_B1F_HQ_GUARD_A::
trainerbattle_single TRAINER_JOHTO_HQ_GUARD_A, JohtoRocketHQ_B1F_Text_HQ_GUARD_AIntro, JohtoRocketHQ_B1F_Text_HQ_GUARD_ADefeat
    msgbox JohtoRocketHQ_B1F_Text_HQ_GUARD_AAfter, MSGBOX_NPC
    end

JohtoRocketHQ_B1F_HQ_GUARD_B::
trainerbattle_single TRAINER_JOHTO_HQ_GUARD_B, JohtoRocketHQ_B1F_Text_HQ_GUARD_BIntro, JohtoRocketHQ_B1F_Text_HQ_GUARD_BDefeat
    msgbox JohtoRocketHQ_B1F_Text_HQ_GUARD_BAfter, MSGBOX_NPC
    end

JohtoRocketHQ_B1F_Lance::
msgbox JohtoRocketHQ_B1F_Text_Lance, MSGBOX_NPC
    end
