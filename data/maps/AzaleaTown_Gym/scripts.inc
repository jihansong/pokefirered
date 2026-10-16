AzaleaTown_Gym_MapScripts::
    .byte 0

AzaleaTown_Gym_Bugsy::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE01_GET, AzaleaTown_Gym_NotReady
    goto_if_unset FLAG_JOHTO_KURT_REPORT_DELIVERED, AzaleaTown_Gym_NotReady
    goto_if_set FLAG_JOHTO_BADGE02_GET, AzaleaTown_Gym_Reward
    trainerbattle_single TRAINER_JOHTO_BUGSY, AzaleaTown_Gym_Text_Intro, AzaleaTown_Gym_Text_Defeat, AzaleaTown_Gym_Victory, NO_MUSIC
    goto AzaleaTown_Gym_Reward
AzaleaTown_Gym_Victory::
    setflag FLAG_JOHTO_BADGE02_GET
    msgbox AzaleaTown_Gym_Text_Badge
AzaleaTown_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM06_FROM_BUGSY, AzaleaTown_Gym_After
    checkitemspace ITEM_TM06
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_Gym_BagFull
    giveitem ITEM_TM06
    goto_if_eq VAR_RESULT, FALSE, AzaleaTown_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM06_FROM_BUGSY
    msgbox AzaleaTown_Gym_Text_TM
AzaleaTown_Gym_After::
    msgbox AzaleaTown_Gym_Text_After
    release
    end
AzaleaTown_Gym_NotReady::
    msgbox AzaleaTown_Gym_Text_NotReady
    release
    end
AzaleaTown_Gym_BagFull::
    msgbox AzaleaTown_Gym_Text_BagFull
    release
    end

AzaleaTown_Gym_Al::
    trainerbattle_single TRAINER_JOHTO_AL, AzaleaTown_Gym_Text_StudentIntro, AzaleaTown_Gym_Text_StudentDefeat
    msgbox AzaleaTown_Gym_Text_StudentAfter, MSGBOX_AUTOCLOSE
    end

AzaleaTown_Gym_Benny::
    trainerbattle_single TRAINER_JOHTO_BENNY, AzaleaTown_Gym_Text_StudentIntro, AzaleaTown_Gym_Text_StudentDefeat
    msgbox AzaleaTown_Gym_Text_StudentAfter, MSGBOX_AUTOCLOSE
    end

AzaleaTown_Gym_GymGuy::
    msgbox AzaleaTown_Gym_Text_GymGuy, MSGBOX_NPC
    end
