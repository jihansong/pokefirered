JohtoLeague_KarensRoom_MapScripts::
    .byte 0

JohtoLeague_KarensRoom_Leader::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BRUNO_CLEARED, JohtoLeague_KarensRoom_PriorNotReady
    goto_if_defeated TRAINER_JOHTO_KAREN, JohtoLeague_KarensRoom_Victory
    trainerbattle_single TRAINER_JOHTO_KAREN, JohtoLeague_KarensRoom_Text_Intro, JohtoLeague_KarensRoom_Text_Loss, JohtoLeague_KarensRoom_Victory, NO_MUSIC
    release
    end
JohtoLeague_KarensRoom_Victory::
    setflag FLAG_JOHTO_KAREN_CLEARED
    msgbox JohtoLeague_KarensRoom_Text_After
    release
    end
JohtoLeague_KarensRoom_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_KAREN_CLEARED, JohtoLeague_KarensRoom_GateClosed
    special SetOrdinaryWarpTransition
    warp MAP_JOHTO_LEAGUE_LANCES_ROOM, 0
    waitstate
    releaseall
    end
JohtoLeague_KarensRoom_GateClosed::
    msgbox JohtoLeague_KarensRoom_Text_GateClosed
    applymovement LOCALID_PLAYER, JohtoLeague_KarensRoom_PushBack
    waitmovement 0
    releaseall
    end
JohtoLeague_KarensRoom_PriorNotReady::
    msgbox JohtoLeague_KarensRoom_Text_PriorNotReady
    release
    end
JohtoLeague_KarensRoom_PushBack::
    walk_down
    step_end
