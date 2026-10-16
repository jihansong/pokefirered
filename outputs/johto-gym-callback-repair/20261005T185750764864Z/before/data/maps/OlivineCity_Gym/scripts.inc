OlivineCity_Gym_MapScripts::
    map_script MAP_SCRIPT_ON_LOAD, OlivineCity_Gym_OnLoad
    .byte 0

OlivineCity_Gym_JASMINE::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BADGE06_GET, OlivineCity_Gym_Reward
    goto_if_unset FLAG_JOHTO_AMPHY_CURED, OlivineCity_Gym_NotReady
    goto_if_unset FLAG_JOHTO_BADGE05_GET, OlivineCity_Gym_NotReady
    trainerbattle_single TRAINER_JOHTO_JASMINE, OlivineCity_Gym_Text_Intro, OlivineCity_Gym_Text_Defeat
    setflag FLAG_JOHTO_BADGE06_GET
    msgbox OlivineCity_Gym_Text_Badge
OlivineCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM23_FROM_JASMINE, OlivineCity_Gym_After
    giveitem ITEM_TM23
    goto_if_eq VAR_RESULT, FALSE, OlivineCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM23_FROM_JASMINE
    msgbox OlivineCity_Gym_Text_TM
    release
    end
OlivineCity_Gym_NotReady::
    msgbox OlivineCity_Gym_Text_NotReady
    release
    end
OlivineCity_Gym_BagFull::
    msgbox OlivineCity_Gym_Text_BagFull
    release
    end
OlivineCity_Gym_After::
    msgbox OlivineCity_Gym_Text_After
    release
    end

OlivineCity_Gym_OnLoad::
goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineCity_Gym_ShowJasmine
    setflag FLAG_HIDE_JOHTO_JASMINE_GYM
    end
OlivineCity_Gym_ShowJasmine::
    clearflag FLAG_HIDE_JOHTO_JASMINE_GYM
    end

OlivineCity_Gym_Guide::
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineCity_Gym_GuideRestored
msgbox OlivineCity_Gym_Text_Guide, MSGBOX_NPC
    end
OlivineCity_Gym_GuideRestored::
    msgbox OlivineCity_Gym_Text_GuideRestored, MSGBOX_NPC
    end
