JohtoVictoryRoad_1F_MapScripts::
    .byte 0

JohtoVictoryRoad_1F_Silver::
    lock
    faceplayer
    goto_if_defeated TRAINER_JOHTO_SILVER_VICTORY_ROAD, JohtoVictoryRoad_1F_Silver_Victory
    trainerbattle_single TRAINER_JOHTO_SILVER_VICTORY_ROAD, JohtoVictoryRoad_1F_Text_SilverIntro, JohtoVictoryRoad_1F_Text_SilverLoss, JohtoVictoryRoad_1F_Silver_Victory, NO_MUSIC
    release
    end
JohtoVictoryRoad_1F_Silver_Victory::
    setflag FLAG_JOHTO_SILVER_LEAGUE_RESOLVED
    msgbox JohtoVictoryRoad_1F_Text_SilverAfter
    release
    end
JohtoVictoryRoad_1F_LeagueExit::
    lockall
    goto_if_unset FLAG_JOHTO_SILVER_LEAGUE_RESOLVED, JohtoVictoryRoad_1F_SilverWait
    warp MAP_JOHTO_INDIGO_PLATEAU, 1
    waitstate
    releaseall
    end
JohtoVictoryRoad_1F_SilverWait::
    msgbox JohtoVictoryRoad_1F_Text_SilverWaiting
    applymovement LOCALID_PLAYER, JohtoVictoryRoad_1F_PushBack
    waitmovement 0
    releaseall
    end
JohtoVictoryRoad_1F_PushBack::
    walk_down
    step_end
