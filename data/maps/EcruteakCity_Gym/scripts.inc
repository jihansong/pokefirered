EcruteakCity_Gym_MapScripts::
    .byte 0

EcruteakCity_Gym_Morty::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE04_GET, EcruteakCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_BADGE03_GET, EcruteakCity_Gym_NotReady
    goto_if_unset FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, EcruteakCity_Gym_NotReady
    trainerbattle_single TRAINER_JOHTO_MORTY, EcruteakCity_Gym_Text_Intro, EcruteakCity_Gym_Text_Defeat, EcruteakCity_Gym_MortyVictory, NO_MUSIC
    goto EcruteakCity_Gym_MortyVictory
EcruteakCity_Gym_MortyVictory::
    msgbox EcruteakCity_Gym_Text_Badge
    setflag FLAG_JOHTO_BADGE04_GET
EcruteakCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM30_FROM_MORTY, EcruteakCity_Gym_After
    checkitemspace ITEM_TM30, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_Gym_BagFull
    giveitem ITEM_TM30, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM30_FROM_MORTY
    msgbox EcruteakCity_Gym_Text_TM
    release
    end
EcruteakCity_Gym_After::
    msgbox EcruteakCity_Gym_Text_After
    release
    end
EcruteakCity_Gym_NotReady::
    msgbox EcruteakCity_Gym_Text_NotReady
    release
    end
EcruteakCity_Gym_BagFull::
    msgbox EcruteakCity_Gym_Text_BagFull
    release
    end

EcruteakCity_Gym_PING::
trainerbattle_single TRAINER_JOHTO_PING, EcruteakCity_Gym_Text_PINGIntro, EcruteakCity_Gym_Text_PINGDefeat
    msgbox EcruteakCity_Gym_Text_PINGAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_Gym_GRACE::
trainerbattle_single TRAINER_JOHTO_GRACE, EcruteakCity_Gym_Text_GRACEIntro, EcruteakCity_Gym_Text_GRACEDefeat
    msgbox EcruteakCity_Gym_Text_GRACEAfter, MSGBOX_AUTOCLOSE
    end
