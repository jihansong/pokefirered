BlackthornCity_Gym_MapScripts::
    .byte 0

BlackthornCity_Gym_ALLEN::
trainerbattle_single TRAINER_JOHTO_ALLEN, BlackthornCity_Gym_Text_ALLENIntro, BlackthornCity_Gym_Text_ALLENDefeat
    msgbox BlackthornCity_Gym_Text_ALLENAfter, MSGBOX_NPC
    end

BlackthornCity_Gym_FRAN::
trainerbattle_single TRAINER_JOHTO_FRAN, BlackthornCity_Gym_Text_FRANIntro, BlackthornCity_Gym_Text_FRANDefeat
    msgbox BlackthornCity_Gym_Text_FRANAfter, MSGBOX_NPC
    end

BlackthornCity_Gym_Clair::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE08_GET, BlackthornCity_Gym_ClairAfter
    goto_if_set FLAG_JOHTO_CLAIR_DEFEATED, BlackthornCity_Gym_ClairTrial
    goto_if_unset FLAG_JOHTO_BADGE07_GET, BlackthornCity_Gym_ClairBefore
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, BlackthornCity_Gym_ClairBefore
    goto_if_defeated TRAINER_JOHTO_CLAIR, BlackthornCity_Gym_ClairVictory
    trainerbattle_single TRAINER_JOHTO_CLAIR, BlackthornCity_Gym_Text_ClairIntro, BlackthornCity_Gym_Text_ClairDefeat, BlackthornCity_Gym_ClairVictory, NO_MUSIC
    goto BlackthornCity_Gym_ClairVictory
BlackthornCity_Gym_ClairVictory::
    setflag FLAG_JOHTO_CLAIR_DEFEATED
BlackthornCity_Gym_ClairTrial::
    msgbox BlackthornCity_Gym_Text_ClairTrial
    release
    end
BlackthornCity_Gym_ClairBefore::
    msgbox BlackthornCity_Gym_Text_ClairBefore
    release
    end
BlackthornCity_Gym_ClairAfter::
    msgbox BlackthornCity_Gym_Text_ClairAfter
    release
    end
