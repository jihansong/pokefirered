Route24_MapScripts::
	.byte 0

Route24_EventScript_Rocket::
	lock
	faceplayer
	goto_if_eq VAR_MAP_SCENE_ROUTE24, 1, Route24_EventScript_RocketPostBattle
	msgbox Route24_Text_JustEarnedFabulousPrize
	checkitemspace ITEM_NUGGET
	goto_if_eq VAR_RESULT, FALSE, Route24_EventScript_NoRoomForNugget
	call Route24_EventScript_BattleRocket
	release
	end

Route24_EventScript_NoRoomForNugget::
	msgbox Route24_Text_YouDontHaveAnyRoom
	release
	end

Route24_EventScript_RocketPostBattle::
	msgbox Route24_Text_YoudBecomeTopRocketLeader
	release
	end

Route24_EventScript_RocketTriggerLeft::
	lockall
	setvar VAR_TEMP_1, 0
	goto Route24_EventScript_RocketTrigger
	end

Route24_EventScript_RocketTriggerRight::
	lockall
	setvar VAR_TEMP_1, 1
	goto Route24_EventScript_RocketTrigger
	end

Route24_EventScript_RocketTrigger::
	textcolor NPC_TEXT_COLOR_MALE
	call_if_eq VAR_TEMP_1, 0, Route24_EventScript_RocketApproachPlayer
	call_if_eq VAR_TEMP_1, 1, Route24_EventScript_RocketMotionToPlayer
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	msgbox Route24_Text_JustEarnedFabulousPrize
	checkitemspace ITEM_NUGGET
	goto_if_eq VAR_RESULT, FALSE, Route24_EventScript_NoRoomForNuggetTrigger
	call Route24_EventScript_BattleRocket
	releaseall
	end

Route24_EventScript_BattleRocket::
	giveitem_msg Route24_Text_ReceivedNuggetFromMysteryTrainer, ITEM_NUGGET
	message Route24_Text_JoinTeamRocket
	waitmessage
	playbgm MUS_ENCOUNTER_ROCKET, 0
	waitbuttonpress
	setvar VAR_LAST_TALKED, LOCALID_ROUTE24_ROCKET
	trainerbattle_no_intro TRAINER_TEAM_ROCKET_GRUNT_6, Route24_Text_RocketDefeat
	msgbox Route24_Text_YoudBecomeTopRocketLeader
	setvar VAR_MAP_SCENE_ROUTE24, 1
	return

Route24_EventScript_RocketApproachPlayer::
	applymovement LOCALID_ROUTE24_ROCKET, Route24_Movement_RocketApproachPlayer
	waitmovement 0
	return

Route24_EventScript_RocketMotionToPlayer::
	applymovement LOCALID_ROUTE24_ROCKET, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	return

Route24_EventScript_NoRoomForNuggetTrigger::
	msgbox Route24_Text_YouDontHaveAnyRoom
	closemessage
	applymovement LOCALID_PLAYER, Route24_Movement_WalkDown
	waitmovement 0
	call_if_eq VAR_TEMP_1, 0, Route24_EventScript_RocketWalkBackToPos
	release
	end

Route24_EventScript_RocketWalkBackToPos::
	applymovement LOCALID_ROUTE24_ROCKET, Route24_Movement_RocketWalkBackToPos
	waitmovement 0
	return

Route24_Movement_RocketApproachPlayer::
	walk_left
	step_end

Route24_Movement_RocketWalkBackToPos::
	walk_right
	walk_in_place_faster_left
	step_end

Route24_Movement_WalkDown::
	walk_down
	step_end

@ Yellow's Damian, who gives away the CHARMANDER he couldn't raise.
Route24_EventScript_Damian::
	lock
	faceplayer
	goto_if_set FLAG_GOT_CHARMANDER_FROM_DAMIAN, Route24_EventScript_DamianAlreadyGaveCharmander
	msgbox Route24_Text_ShouldReleaseMyCharmander, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route24_EventScript_DamianDeclined
	goto Route24_EventScript_GiveCharmander
	end

Route24_EventScript_DamianDeclined::
	msgbox Route24_Text_BetterReleaseItThen
	release
	end

Route24_EventScript_DamianAlreadyGaveCharmander::
	msgbox Route24_Text_HowsCharmanderDoing
	release
	end

Route24_EventScript_GiveCharmander::
	setvar VAR_TEMP_1, SPECIES_CHARMANDER
	givemon SPECIES_CHARMANDER, 10
	goto_if_eq VAR_RESULT, 0, Route24_EventScript_ReceiveCharmanderParty
	goto_if_eq VAR_RESULT, 1, Route24_EventScript_ReceiveCharmanderPC
	goto_if_eq VAR_RESULT, 2, EventScript_NoMoreRoomForPokemon
	release
	end

Route24_EventScript_ReceiveCharmanderParty::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message Route24_Text_ReceivedCharmander
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_CHARMANDER
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route24_EventScript_EndReceiveCharmander
	call EventScript_GetGiftMonPartySlot
	call EventScript_ChangePokemonNickname
	goto Route24_EventScript_EndReceiveCharmander
	end

Route24_EventScript_ReceiveCharmanderPC::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message Route24_Text_ReceivedCharmander
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_CHARMANDER
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route24_EventScript_CharmanderTransferredToPC
	call EventScript_NameReceivedBoxMon
	goto Route24_EventScript_CharmanderTransferredToPC
	end

Route24_EventScript_CharmanderTransferredToPC::
	call EventScript_TransferredToPC
	goto Route24_EventScript_EndReceiveCharmander
	end

Route24_EventScript_EndReceiveCharmander::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox Route24_Text_TakeGoodCareOfCharmander
	setflag FLAG_GOT_CHARMANDER_FROM_DAMIAN
	release
	end
