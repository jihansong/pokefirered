SproutTower_1F_MapScripts::
    .byte 0

SproutTower_1F_Edmond::
    trainerbattle_single TRAINER_JOHTO_EDMOND, SproutTower_1F_Text_Intro, SproutTower_1F_Text_Defeat
    msgbox SproutTower_1F_Text_After, MSGBOX_AUTOCLOSE
    end

SproutTower_1F_Visitor::
    msgbox SproutTower_1F_Text_Visitor, MSGBOX_NPC
    end
