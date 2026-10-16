GoldenrodCity_RadioTower_5F_MapScripts::
    .byte 0

GoldenrodCity_RadioTower_5F_Archer::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodCity_RadioTower_5F_ArcherAfter
    goto_if_unset FLAG_JOHTO_RADIO_DIRECTOR_RESCUED, GoldenrodCity_RadioTower_5F_ArcherBefore
    goto_if_not_defeated TRAINER_JOHTO_ARIANA_RADIO, GoldenrodCity_RadioTower_5F_ArcherBefore
    goto_if_defeated TRAINER_JOHTO_ARCHER, GoldenrodCity_RadioTower_5F_ArcherVictory
    trainerbattle_single TRAINER_JOHTO_ARCHER, GoldenrodCity_RadioTower_5F_Text_ArcherIntro, GoldenrodCity_RadioTower_5F_Text_ArcherDefeat, GoldenrodCity_RadioTower_5F_ArcherVictory, NO_MUSIC
    goto GoldenrodCity_RadioTower_5F_ArcherVictory
GoldenrodCity_RadioTower_5F_ArcherVictory::
    setflag FLAG_JOHTO_RADIO_TOWER_CLEARED
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherAfter
    removeobject LOCALID_RADIO_ARCHER
    release
    end
GoldenrodCity_RadioTower_5F_ArcherBefore::
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherBefore
    release
    end
GoldenrodCity_RadioTower_5F_ArcherAfter::
    msgbox GoldenrodCity_RadioTower_5F_Text_ArcherAfter
    release
    end
