BurnedTower_1F_MapScripts::
    .byte 0

BurnedTower_1F_Silver::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED, BurnedTower_1F_SilverDone
    goto_if_unset FLAG_JOHTO_BADGE03_GET, BurnedTower_1F_SilverBefore
    trainerbattle_single TRAINER_JOHTO_SILVER_BURNED_TOWER, BurnedTower_1F_Text_Intro, BurnedTower_1F_Text_Defeat, BurnedTower_1F_SilverVictory, NO_MUSIC
    goto BurnedTower_1F_SilverVictory
BurnedTower_1F_SilverVictory::
    setflag FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED
    msgbox BurnedTower_1F_Text_After
    removeobject 1
    release
    end
BurnedTower_1F_SilverBefore::
    msgbox BurnedTower_1F_Text_Before
    release
    end
BurnedTower_1F_SilverDone::
    release
    end

BurnedTower_1F_Researcher::
msgbox BurnedTower_1F_Text_Researcher, MSGBOX_NPC
    end
