JohtoLeague_LancesRoom_MapScripts::
    .byte 0

JohtoLeague_LancesRoom_Leader::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_KAREN_CLEARED, JohtoLeague_LancesRoom_PriorNotReady
    goto_if_defeated TRAINER_JOHTO_LANCE_CHAMPION, JohtoLeague_LancesRoom_Victory
    trainerbattle_single TRAINER_JOHTO_LANCE_CHAMPION, JohtoLeague_LancesRoom_Text_Intro, JohtoLeague_LancesRoom_Text_Loss, JohtoLeague_LancesRoom_Victory, NO_MUSIC
    release
    end
JohtoLeague_LancesRoom_Victory::
    setflag FLAG_JOHTO_LANCE_CHAMPION_CLEARED
    msgbox JohtoLeague_LancesRoom_Text_After
    release
    end
JohtoLeague_LancesRoom_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_LANCE_CHAMPION_CLEARED, JohtoLeague_LancesRoom_GateClosed
    warp MAP_JOHTO_LEAGUE_HALL_OF_FAME, 0
    waitstate
    releaseall
    end
JohtoLeague_LancesRoom_GateClosed::
    msgbox JohtoLeague_LancesRoom_Text_GateClosed
    applymovement LOCALID_PLAYER, JohtoLeague_LancesRoom_PushBack
    waitmovement 0
    releaseall
    end
JohtoLeague_LancesRoom_PriorNotReady::
    msgbox JohtoLeague_LancesRoom_Text_PriorNotReady
    release
    end
JohtoLeague_LancesRoom_PushBack::
    walk_down
    step_end
