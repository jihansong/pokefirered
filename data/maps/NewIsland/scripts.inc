NewIsland_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, NewIsland_OnTransition
	.byte 0

NewIsland_OnTransition::
	setflag FLAG_TEMP_1
	goto_if_set FLAG_ROCKET_NEW_ISLAND, NewIsland_EventScript_TransitionEnd
	clearflag FLAG_TEMP_1
	setvar VAR_TEMP_1, 1
NewIsland_EventScript_TransitionEnd::
	end

@ Thunder Yellow v0.5.0, TEAM ROCKET event 11: after the player has faced MEWTWO,
@ a sailor on the VERMILION quay rows out on foggy nights to an island that
@ isn't on any map. The old cloning lab there holds three logs that tie MEW,
@ the truck on the quay, M-1 (DITTO) and M-2 (MEWTWO) together. The trio are
@ looting it; a final double battle sends them off, and they drop the CARGO TAG.
NewIsland_EventScript_RocketTrio::
	lockall
	setvar VAR_TEMP_1, 0
	goto_if_eq VAR_ROCKET_RETRY, 13, NewIsland_EventScript_RocketTrioRetry
	textcolor NPC_TEXT_COLOR_MALE
	msgbox NewIsland_Text_MeowthReadsFiles
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox NewIsland_Text_JessieBossWillPay
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	applymovement LOCALID_NEW_ISLAND_JESSIE, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_NEW_ISLAND_MEOWTH, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_NEW_ISLAND_JAMES, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	applymovement LOCALID_NEW_ISLAND_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	textcolor NPC_TEXT_COLOR_MALE
	msgbox NewIsland_Text_MeowthTwerpFollowedUs
	applymovement LOCALID_NEW_ISLAND_JESSIE, NewIsland_Movement_TrioStepForward
	applymovement LOCALID_NEW_ISLAND_MEOWTH, NewIsland_Movement_TrioStepForward
	applymovement LOCALID_NEW_ISLAND_JAMES, NewIsland_Movement_TrioStepForward
	waitmovement 0
	call EventScript_RocketTrioMotto
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox NewIsland_Text_JessieWobbuffet
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox NewIsland_Text_RocketFinalIntro
	closemessage
NewIsland_EventScript_RocketTrioBattle::
	setvar VAR_0x8004, 13
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_NEW_ISLAND_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_NEW_ISLAND, NewIsland_Text_RocketFinalDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox NewIsland_Text_JessieAfterFinal
	textcolor NPC_TEXT_COLOR_MALE
	msgbox NewIsland_Text_MeowthAfterFinal
	closemessage
	setvar VAR_0x8008, LOCALID_NEW_ISLAND_JESSIE
	setvar VAR_0x8009, LOCALID_NEW_ISLAND_JAMES
	setvar VAR_0x800A, LOCALID_NEW_ISLAND_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_NEW_ISLAND_JESSIE
	removeobject LOCALID_NEW_ISLAND_MEOWTH
	removeobject LOCALID_NEW_ISLAND_JAMES
	fadedefaultbgm
	setvar VAR_0x8004, 2600
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, NewIsland_EventScript_RocketCoins
	setvar VAR_0x8004, 4680
NewIsland_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox NewIsland_Text_SomethingFluttered
	giveitem ITEM_CARGO_TAG
	setvar VAR_0x8004, ROCKET_HELD_CARGO_TAG
	call EventScript_RocketRewardResult
	setflag FLAG_ROCKET_NEW_ISLAND
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox NewIsland_Text_CargoTagReads
	goto_if_set FLAG_FOUGHT_MEW, NewIsland_EventScript_EmptyIncubator
	@ v0.9.0: MEW is still under the truck on the VERMILION quay, so this is its
	@ EGG, the lab's reserve sample. Taking it empties the truck's hiding place.
	msgbox NewIsland_Text_IncubatorHums
	msgbox NewIsland_Text_EggInside
	specialvar VAR_RESULT, GiveMewEgg
	call EventScript_RocketEggResult
	goto_if_eq VAR_RESULT, 2, NewIsland_EventScript_RocketTrioDone
	call EventScript_GotMewEgg
NewIsland_EventScript_RocketTrioDone::
	releaseall
	end

@ The player has met MEW already: the reserve sample hatched long ago.
NewIsland_EventScript_EmptyIncubator::
	msgbox NewIsland_Text_IncubatorOpen
	msgbox NewIsland_Text_CandyBesideShell
	giveitem ITEM_RARE_CANDY, 3
	setvar VAR_0x8004, ROCKET_BONUS_NEW_ISLAND
	call EventScript_RocketRewardResult
	releaseall
	end

NewIsland_EventScript_RocketTrioRetry::
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	applymovement LOCALID_NEW_ISLAND_JESSIE, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_NEW_ISLAND_MEOWTH, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_NEW_ISLAND_JAMES, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	applymovement LOCALID_NEW_ISLAND_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	applymovement LOCALID_NEW_ISLAND_JESSIE, NewIsland_Movement_TrioStepForward
	applymovement LOCALID_NEW_ISLAND_MEOWTH, NewIsland_Movement_TrioStepForward
	applymovement LOCALID_NEW_ISLAND_JAMES, NewIsland_Movement_TrioStepForward
	waitmovement 0
	call EventScript_RocketTrioRetry
	goto NewIsland_EventScript_RocketTrioBattle

NewIsland_Movement_TrioStepForward::
	walk_down
	walk_down
	step_end

NewIsland_EventScript_Log1::
	msgbox NewIsland_Text_Log1, MSGBOX_SIGN
	end

NewIsland_EventScript_Log2::
	msgbox NewIsland_Text_Log2, MSGBOX_SIGN
	end

NewIsland_EventScript_Log3::
	msgbox NewIsland_Text_Log3, MSGBOX_SIGN
	end

NewIsland_EventScript_Sailor::
	lock
	faceplayer
	msgbox NewIsland_Text_SailorHeadBack, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, NewIsland_EventScript_SailorWait
	msgbox NewIsland_Text_SailorCastOff
	closemessage
	fadescreen FADE_TO_BLACK
	playse SE_EXIT
	warp MAP_VERMILION_CITY, 32, 30
	waitstate
	release
	end

NewIsland_EventScript_SailorWait::
	msgbox NewIsland_Text_SailorWait
	release
	end
