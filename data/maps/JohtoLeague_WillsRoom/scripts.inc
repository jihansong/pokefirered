JohtoLeague_WillsRoom_MapScripts::
    .byte 0

JohtoLeague_WillsRoom_Leader::
    lock
    faceplayer
    goto_if_defeated TRAINER_JOHTO_WILL, JohtoLeague_WillsRoom_Victory
    trainerbattle_single TRAINER_JOHTO_WILL, JohtoLeague_WillsRoom_Text_Intro, JohtoLeague_WillsRoom_Text_Loss, JohtoLeague_WillsRoom_Victory, NO_MUSIC
    release
    end
JohtoLeague_WillsRoom_Victory::
    setflag FLAG_JOHTO_WILL_CLEARED
    msgbox JohtoLeague_WillsRoom_Text_After
    release
    end
JohtoLeague_WillsRoom_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_WILL_CLEARED, JohtoLeague_WillsRoom_GateClosed
    special SetOrdinaryWarpTransition
    warp MAP_JOHTO_LEAGUE_KOGAS_ROOM, 0
    waitstate
    releaseall
    end
JohtoLeague_WillsRoom_GateClosed::
    msgbox JohtoLeague_WillsRoom_Text_GateClosed
    applymovement LOCALID_PLAYER, JohtoLeague_WillsRoom_PushBack
    waitmovement 0
    releaseall
    end
JohtoLeague_WillsRoom_PriorNotReady::
    msgbox JohtoLeague_WillsRoom_Text_PriorNotReady
    release
    end
JohtoLeague_WillsRoom_PushBack::
    walk_down
    step_end
