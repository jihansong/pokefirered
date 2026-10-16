GoldenrodCity_Gym_MapScripts::
    .byte 0

GoldenrodCity_Gym_Whitney::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_BADGE02_GET, GoldenrodCity_Gym_NotReady
    goto_if_unset FLAG_JOHTO_GOLDENROD_RESEARCH_REGISTERED, GoldenrodCity_Gym_NotReady
    goto_if_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AfterBattle
    trainerbattle_single TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_Text_Intro, GoldenrodCity_Gym_Text_Defeat, GoldenrodCity_Gym_WhitneyVictory, NO_MUSIC
    goto GoldenrodCity_Gym_AfterBattle
GoldenrodCity_Gym_WhitneyVictory::
    msgbox GoldenrodCity_Gym_Text_Upset
    release
    end
GoldenrodCity_Gym_AfterBattle::
    goto_if_unset FLAG_JOHTO_WHITNEY_ENCOURAGED, GoldenrodCity_Gym_Upset
    msgbox GoldenrodCity_Gym_Text_Badge
    setflag FLAG_JOHTO_BADGE03_GET
GoldenrodCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM45_FROM_WHITNEY, GoldenrodCity_Gym_After
    checkitemspace ITEM_TM45, 1
    goto_if_eq VAR_RESULT, FALSE, GoldenrodCity_Gym_BagFull
    giveitem ITEM_TM45, 1
    goto_if_eq VAR_RESULT, FALSE, GoldenrodCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM45_FROM_WHITNEY
    msgbox GoldenrodCity_Gym_Text_TM
    release
    end
GoldenrodCity_Gym_After::
    msgbox GoldenrodCity_Gym_Text_After
    release
    end
GoldenrodCity_Gym_Upset::
    msgbox GoldenrodCity_Gym_Text_Upset
    release
    end
GoldenrodCity_Gym_NotReady::
    msgbox GoldenrodCity_Gym_Text_NotReady
    release
    end
GoldenrodCity_Gym_BagFull::
    msgbox GoldenrodCity_Gym_Text_BagFull
    release
    end

GoldenrodCity_Gym_Assistant::
lock
    faceplayer
    goto_if_not_defeated TRAINER_JOHTO_WHITNEY, GoldenrodCity_Gym_AssistantBefore
    goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_Gym_AssistantAfter
    msgbox GoldenrodCity_Gym_Text_AssistantEncourage
    setflag FLAG_JOHTO_WHITNEY_ENCOURAGED
    release
    end
GoldenrodCity_Gym_AssistantBefore::
    msgbox GoldenrodCity_Gym_Text_AssistantBefore
    release
    end
GoldenrodCity_Gym_AssistantAfter::
    msgbox GoldenrodCity_Gym_Text_AssistantAfter
    release
    end

GoldenrodCity_Gym_Victoria::
trainerbattle_single TRAINER_JOHTO_VICTORIA, GoldenrodCity_Gym_Text_VictoriaIntro, GoldenrodCity_Gym_Text_VictoriaDefeat
    msgbox GoldenrodCity_Gym_Text_VictoriaAfter, MSGBOX_AUTOCLOSE
    end

GoldenrodCity_Gym_Samantha::
trainerbattle_single TRAINER_JOHTO_SAMANTHA, GoldenrodCity_Gym_Text_SamanthaIntro, GoldenrodCity_Gym_Text_SamanthaDefeat
    msgbox GoldenrodCity_Gym_Text_SamanthaAfter, MSGBOX_AUTOCLOSE
    end
