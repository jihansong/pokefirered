SproutTower_3F_MapScripts::
    .byte 0

SproutTower_3F_Elder::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_ELM_REPORT_DELIVERED, SproutTower_3F_NotReady
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_CLEARED, SproutTower_3F_Reward
    trainerbattle_single TRAINER_JOHTO_LI, SproutTower_3F_Text_Intro, SproutTower_3F_Text_Defeat, SproutTower_3F_Victory, NO_MUSIC
    goto SproutTower_3F_Reward
SproutTower_3F_Victory::
    setflag FLAG_JOHTO_SPROUT_TOWER_CLEARED
    msgbox SproutTower_3F_Text_ResearchComplete
    goto SproutTower_3F_Reward
SproutTower_3F_Reward::
    goto_if_set FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED, SproutTower_3F_After
    goto_if_set FLAG_GOT_HM05, SproutTower_3F_AlternateReward
    checkitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkpcitem ITEM_HM05
    goto_if_eq VAR_RESULT, TRUE, SproutTower_3F_AlternateReward
    checkitemspace ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    giveitem ITEM_HM05
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Flash
    goto SproutTower_3F_After
SproutTower_3F_AlternateReward::
    checkitemspace ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    msgbox SproutTower_3F_Text_KnownFlash
    giveitem ITEM_TM10
    goto_if_eq VAR_RESULT, FALSE, SproutTower_3F_BagFull
    setflag FLAG_JOHTO_SPROUT_TOWER_FLASH_RECEIVED
    msgbox SproutTower_3F_Text_Alternate
SproutTower_3F_After::
    msgbox SproutTower_3F_Text_After
    release
    end
SproutTower_3F_NotReady::
    msgbox SproutTower_3F_Text_NotReady
    release
    end
SproutTower_3F_BagFull::
    msgbox SproutTower_3F_Text_BagFull
    release
    end
