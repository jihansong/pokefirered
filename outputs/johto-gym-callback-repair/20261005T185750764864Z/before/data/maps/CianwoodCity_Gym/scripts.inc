CianwoodCity_Gym_MapScripts::
    .byte 0

CianwoodCity_Gym_CHUCK::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE05_GET, CianwoodCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_BADGE04_GET, CianwoodCity_Gym_NotReady
    trainerbattle_single TRAINER_JOHTO_CHUCK, CianwoodCity_Gym_Text_Intro, CianwoodCity_Gym_Text_Defeat
    setflag FLAG_JOHTO_BADGE05_GET
    msgbox CianwoodCity_Gym_Text_Badge
CianwoodCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM01_FROM_CHUCK, CianwoodCity_Gym_After
    giveitem ITEM_TM01
    goto_if_eq VAR_RESULT, FALSE, CianwoodCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM01_FROM_CHUCK
    msgbox CianwoodCity_Gym_Text_TM
    release
    end
CianwoodCity_Gym_NotReady::
    msgbox CianwoodCity_Gym_Text_NotReady
    release
    end
CianwoodCity_Gym_BagFull::
    msgbox CianwoodCity_Gym_Text_BagFull
    release
    end
CianwoodCity_Gym_After::
    msgbox CianwoodCity_Gym_Text_After
    release
    end

CianwoodCity_Gym_YOSHI::
trainerbattle_single TRAINER_JOHTO_YOSHI, CianwoodCity_Gym_Text_YOSHIIntro, CianwoodCity_Gym_Text_YOSHIDefeat
    msgbox CianwoodCity_Gym_Text_YOSHIAfter, MSGBOX_NPC
    end
