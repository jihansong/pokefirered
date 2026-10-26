JohtoLeague_BrunosRoom_MapScripts::
    .byte 0

JohtoLeague_BrunosRoom_Leader::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_KOGA_CLEARED, JohtoLeague_BrunosRoom_PriorNotReady
    goto_if_defeated TRAINER_JOHTO_BRUNO, JohtoLeague_BrunosRoom_Victory
    trainerbattle_single TRAINER_JOHTO_BRUNO, JohtoLeague_BrunosRoom_Text_Intro, JohtoLeague_BrunosRoom_Text_Loss, JohtoLeague_BrunosRoom_Victory, NO_MUSIC
    release
    end
JohtoLeague_BrunosRoom_Victory::
    setflag FLAG_JOHTO_BRUNO_CLEARED
    msgbox JohtoLeague_BrunosRoom_Text_After
    release
    end
JohtoLeague_BrunosRoom_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_BRUNO_CLEARED, JohtoLeague_BrunosRoom_GateClosed
    special SetOrdinaryWarpTransition
    warp MAP_JOHTO_LEAGUE_KARENS_ROOM, 0
    waitstate
    releaseall
    end
JohtoLeague_BrunosRoom_GateClosed::
    msgbox JohtoLeague_BrunosRoom_Text_GateClosed
    applymovement LOCALID_PLAYER, JohtoLeague_BrunosRoom_PushBack
    waitmovement 0
    releaseall
    end
JohtoLeague_BrunosRoom_PriorNotReady::
    msgbox JohtoLeague_BrunosRoom_Text_PriorNotReady
    release
    end
JohtoLeague_BrunosRoom_PushBack::
    walk_down
    step_end
