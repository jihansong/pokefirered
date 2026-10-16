MahoganyTown_Gym_MapScripts::
    .byte 0

MahoganyTown_Gym_Pryce::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE06_GET, MahoganyTown_Gym_Before
    goto_if_unset FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_Gym_Before
    goto_if_defeated TRAINER_JOHTO_PRYCE, MahoganyTown_Gym_Victory
    trainerbattle_single TRAINER_JOHTO_PRYCE, MahoganyTown_Gym_Text_Intro, MahoganyTown_Gym_Text_Defeat, MahoganyTown_Gym_Victory, NO_MUSIC
    goto MahoganyTown_Gym_Victory
MahoganyTown_Gym_Victory::
    setflag FLAG_JOHTO_BADGE07_GET
    goto_if_set FLAG_JOHTO_PRYCE_TM13_RECEIVED, MahoganyTown_Gym_After
    giveitem ITEM_TM13
    goto_if_eq VAR_RESULT, FALSE, MahoganyTown_Gym_Full
    setflag FLAG_JOHTO_PRYCE_TM13_RECEIVED
MahoganyTown_Gym_After::
    msgbox MahoganyTown_Gym_Text_After
    release
    end
MahoganyTown_Gym_Full::
    msgbox MahoganyTown_Gym_Text_Full
    release
    end
MahoganyTown_Gym_Before::
    msgbox MahoganyTown_Gym_Text_Before
    release
    end
