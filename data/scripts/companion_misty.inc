PalletTown_EventScript_MistyJoin::
    setvar VAR_TEMP_7, FALSE
    lockall
    specialvar VAR_RESULT, CanMistyJoin
    goto_if_eq VAR_RESULT, FALSE, PalletTown_EventScript_MistyNotReady
    msgbox MistyCompanion_Text_Join, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, PalletTown_EventScript_MistyDeclined
    removeobject LOCALID_PALLET_MISTY
    special MistyJoin
    msgbox MistyCompanion_Text_Joined, MSGBOX_DEFAULT
    releaseall
    end
PalletTown_EventScript_MistyNotReady::
    msgbox MistyCompanion_Text_NotReady, MSGBOX_DEFAULT
    releaseall
    end
PalletTown_EventScript_MistyDeclined::
    special MistyDeclineCompanionJoin
    msgbox MistyCompanion_Text_Declined, MSGBOX_DEFAULT
    releaseall
    end

EventScript_TalkToMistyCompanion::
    lock
    faceplayer
    @ A bag-full TM03 reward must remain claimable after the GYM closes.
    goto_if_unset FLAG_GOT_TM03_FROM_MISTY, CeruleanCity_Gym_EventScript_GiveTM03
    msgbox MistyCompanion_Text_TrainQuestion, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MistyCompanion_EventScript_Moment
    specialvar VAR_RESULT, MistyGetGrowthStage
    goto_if_eq VAR_RESULT, 4, MistyCompanion_EventScript_Train4
    goto_if_eq VAR_RESULT, 3, MistyCompanion_EventScript_Train3
    goto_if_eq VAR_RESULT, 2, MistyCompanion_EventScript_Train2
    goto_if_eq VAR_RESULT, 1, MistyCompanion_EventScript_Train1
    goto MistyCompanion_EventScript_Train0

MistyCompanion_EventScript_Train0::
    msgbox MistyCompanion_Text_TrainIntro, MSGBOX_DEFAULT
    trainerbattle_earlyrival TRAINER_MISTY_COMPANION_STAGE0, RIVAL_BATTLE_HEAL_AFTER, MistyCompanion_Text_TrainDefeat, MistyCompanion_Text_TrainVictory
    goto MistyCompanion_EventScript_AfterTraining

MistyCompanion_EventScript_Train1::
    msgbox MistyCompanion_Text_TrainIntro, MSGBOX_DEFAULT
    trainerbattle_earlyrival TRAINER_MISTY_COMPANION_STAGE1, RIVAL_BATTLE_HEAL_AFTER, MistyCompanion_Text_TrainDefeat, MistyCompanion_Text_TrainVictory
    goto MistyCompanion_EventScript_AfterTraining

MistyCompanion_EventScript_Train2::
    msgbox MistyCompanion_Text_TrainIntro, MSGBOX_DEFAULT
    trainerbattle_earlyrival TRAINER_MISTY_COMPANION_STAGE2, RIVAL_BATTLE_HEAL_AFTER, MistyCompanion_Text_TrainDefeat, MistyCompanion_Text_TrainVictory
    goto MistyCompanion_EventScript_AfterTraining

MistyCompanion_EventScript_Train3::
    msgbox MistyCompanion_Text_TrainIntro, MSGBOX_DEFAULT
    trainerbattle_earlyrival TRAINER_MISTY_COMPANION_STAGE3, RIVAL_BATTLE_HEAL_AFTER, MistyCompanion_Text_TrainDefeat, MistyCompanion_Text_TrainVictory
    goto MistyCompanion_EventScript_AfterTraining

MistyCompanion_EventScript_Train4::
    msgbox MistyCompanion_Text_TrainIntro, MSGBOX_DEFAULT
    trainerbattle_earlyrival TRAINER_MISTY_COMPANION_STAGE4, RIVAL_BATTLE_HEAL_AFTER, MistyCompanion_Text_TrainDefeat, MistyCompanion_Text_TrainVictory
    goto MistyCompanion_EventScript_AfterTraining

MistyCompanion_EventScript_AfterTraining::
    special HealPlayerParty
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_AfterTraining, MSGBOX_DEFAULT
    releaseall
    end
MistyCompanion_EventScript_Moment::
    specialvar VAR_RESULT, MistyGetGrowthStage
    goto_if_eq VAR_RESULT, 4, MistyCompanion_EventScript_Moment4
    goto_if_eq VAR_RESULT, 3, MistyCompanion_EventScript_Moment3
    goto_if_eq VAR_RESULT, 2, MistyCompanion_EventScript_Moment2
    goto_if_eq VAR_RESULT, 1, MistyCompanion_EventScript_Moment1
    goto MistyCompanion_EventScript_Moment0

MistyCompanion_EventScript_Moment0::
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_Moment0, MSGBOX_DEFAULT
    release
    end

MistyCompanion_EventScript_Moment1::
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_Moment1, MSGBOX_DEFAULT
    release
    end

MistyCompanion_EventScript_Moment2::
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_Moment2, MSGBOX_DEFAULT
    release
    end

MistyCompanion_EventScript_Moment3::
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_Moment3, MSGBOX_DEFAULT
    release
    end

MistyCompanion_EventScript_Moment4::
    call MistyCompanion_EventScript_SendHeart
    msgbox MistyCompanion_Text_Moment4, MSGBOX_DEFAULT
    release
    end

MistyCompanion_EventScript_SendHeart::
    closemessage
    dofieldeffect FLDEFF_MISTY_HEART
    waitfieldeffect FLDEFF_MISTY_HEART
    return

MistyCompanion_Text_Join::
    .string "MISTY: You did it, {PLAYER}!\n"
    .string "I want to see what comes next.\p"
    .string "May I travel with you?$"

MistyCompanion_Text_Joined::
    .string "MISTY: I closed my GYM so I can\n"
    .string "travel with you and PIKACHU.\p"
    .string "GOLDUCK and SEADRA are ready!\n"
    .string "Let us keep growing together!$"

MistyCompanion_Text_NotReady::
    .string "MISTY: Finish the KANTO\n"
    .string "League first. I will be here.$"

MistyCompanion_Text_Declined::
    .string "MISTY: Take your time.\n"
    .string "Come talk when you are ready.$"

MistyCompanion_Text_TrainQuestion::
    .string "MISTY: Ready for a friendly\n"
    .string "training battle?$"

MistyCompanion_Text_TrainIntro::
    .string "MISTY: Show me how far\n"
    .string "you and your team have grown!$"

MistyCompanion_Text_TrainDefeat::
    .string "That was wonderful, {PLAYER}!$"

MistyCompanion_Text_TrainVictory::
    .string "We learn from every battle.\n"
    .string "I will help your team recover.$"

MistyCompanion_Text_AfterTraining::
    .string "MISTY: Everyone is rested.\n"
    .string "I like being by your side!\p"
    .string "Let us keep traveling together!$"

MistyCompanion_Text_Moment0::
    .string "MISTY: You make my heart\n"
    .string "skip a beat, {PLAYER}!\p"
    .string "Would you go on a date with me\n"
    .string "at our next rest stop?$"

MistyCompanion_Text_Moment1::
    .string "MISTY: JOHTO feels brighter\n"
    .string "when we travel together!\p"
    .string "POLITOED has joined our team.\n"
    .string "I would love to date you.$"

MistyCompanion_Text_Moment2::
    .string "MISTY: My team keeps growing,\n"
    .string "and so do my feelings for you.\p"
    .string "How about a date by the sea\n"
    .string "when we take a break?$"

MistyCompanion_Text_Moment3::
    .string "MISTY: The DRAGON SCALE helped\n"
    .string "SEADRA become KINGDRA!\p"
    .string "Now our team has six friends.\n"
    .string "I want to stay with you, too!$"

MistyCompanion_Text_Moment4::
    .string "MISTY: Let us go on a real date\n"
    .string "when this adventure is over.\p"
    .string "Someday, would you like\n"
    .string "to marry me?$"

@ Caller retains its existing locks. This helper returns to the airport story.
EventScript_MistyPostChampionBridge::
    specialvar VAR_RESULT, CanOfferMistyCompanionJoin
    goto_if_eq VAR_RESULT, FALSE, MistyCompanion_PostChampionBridgeDone
    msgbox MistyCompanion_Text_Join, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, MistyCompanion_PostChampionBridgeDeclined
    special MistyJoin
    msgbox MistyCompanion_Text_Joined, MSGBOX_DEFAULT
    return
MistyCompanion_PostChampionBridgeDeclined::
    special MistyDeclineCompanionJoin
    msgbox MistyCompanion_Text_Declined, MSGBOX_DEFAULT
MistyCompanion_PostChampionBridgeDone::
    return
