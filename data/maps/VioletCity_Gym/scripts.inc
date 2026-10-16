VioletCity_Gym_MapScripts::
    .byte 0

VioletCity_Gym_Falkner::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_SPROUT_TOWER_CLEARED, VioletCity_Gym_NotReady
    goto_if_set FLAG_JOHTO_BADGE01_GET, VioletCity_Gym_Reward
    trainerbattle_single TRAINER_JOHTO_FALKNER, VioletCity_Gym_Text_Intro, VioletCity_Gym_Text_Defeat, VioletCity_Gym_Victory, NO_MUSIC
    goto VioletCity_Gym_Reward
VioletCity_Gym_Victory::
    setflag FLAG_JOHTO_BADGE01_GET
    msgbox VioletCity_Gym_Text_Badge
    goto VioletCity_Gym_Reward
VioletCity_Gym_Reward::
    goto_if_set FLAG_JOHTO_GOT_TM40_FROM_FALKNER, VioletCity_Gym_After
    checkitemspace ITEM_TM40
    goto_if_eq VAR_RESULT, FALSE, VioletCity_Gym_BagFull
    giveitem ITEM_TM40
    goto_if_eq VAR_RESULT, FALSE, VioletCity_Gym_BagFull
    setflag FLAG_JOHTO_GOT_TM40_FROM_FALKNER
    msgbox VioletCity_Gym_Text_TM
VioletCity_Gym_After::
    msgbox VioletCity_Gym_Text_After
    release
    end
VioletCity_Gym_NotReady::
    msgbox VioletCity_Gym_Text_NotReady
    release
    end
VioletCity_Gym_BagFull::
    msgbox VioletCity_Gym_Text_BagFull
    release
    end

VioletCity_Gym_Abe::
    trainerbattle_single TRAINER_JOHTO_ABE, VioletCity_Gym_Text_AbeIntro, VioletCity_Gym_Text_AbeDefeat
    msgbox VioletCity_Gym_Text_AbeAfter, MSGBOX_AUTOCLOSE
    end

VioletCity_Gym_Rod::
    trainerbattle_single TRAINER_JOHTO_ROD, VioletCity_Gym_Text_RodIntro, VioletCity_Gym_Text_RodDefeat
    msgbox VioletCity_Gym_Text_RodAfter, MSGBOX_AUTOCLOSE
    end

VioletCity_Gym_GymGuy::
    msgbox VioletCity_Gym_Text_GymGuy, MSGBOX_NPC
    end
