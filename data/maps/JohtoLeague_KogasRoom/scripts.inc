JohtoLeague_KogasRoom_MapScripts::
    .byte 0

JohtoLeague_KogasRoom_Leader::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_WILL_CLEARED, JohtoLeague_KogasRoom_PriorNotReady
    goto_if_defeated TRAINER_JOHTO_KOGA, JohtoLeague_KogasRoom_Victory
    trainerbattle_single TRAINER_JOHTO_KOGA, JohtoLeague_KogasRoom_Text_Intro, JohtoLeague_KogasRoom_Text_Loss, JohtoLeague_KogasRoom_Victory, NO_MUSIC
    release
    end
JohtoLeague_KogasRoom_Victory::
    setflag FLAG_JOHTO_KOGA_CLEARED
    msgbox JohtoLeague_KogasRoom_Text_After
    release
    end
JohtoLeague_KogasRoom_NextRoom::
    lockall
    goto_if_unset FLAG_JOHTO_KOGA_CLEARED, JohtoLeague_KogasRoom_GateClosed
    special SetOrdinaryWarpTransition
    warp MAP_JOHTO_LEAGUE_BRUNOS_ROOM, 0
    waitstate
    releaseall
    end
JohtoLeague_KogasRoom_GateClosed::
    msgbox JohtoLeague_KogasRoom_Text_GateClosed
    applymovement LOCALID_PLAYER, JohtoLeague_KogasRoom_PushBack
    waitmovement 0
    releaseall
    end
JohtoLeague_KogasRoom_PriorNotReady::
    msgbox JohtoLeague_KogasRoom_Text_PriorNotReady
    release
    end
JohtoLeague_KogasRoom_PushBack::
    walk_down
    step_end
