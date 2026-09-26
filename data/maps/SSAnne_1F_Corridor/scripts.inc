SSAnne_1F_Corridor_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SSAnne_1F_Corridor_OnTransition
	.byte 0

SSAnne_1F_Corridor_OnTransition::
	setflag FLAG_TEMP_3
	goto_if_set FLAG_ROCKET_SS_ANNE, SSAnne_1F_Corridor_EventScript_HidePlotters
	setvar VAR_TEMP_1, 1
	end

SSAnne_1F_Corridor_EventScript_HidePlotters::
	setflag FLAG_TEMP_1
	setflag FLAG_TEMP_2
	end

@ Thunder Yellow v0.5.0, TEAM ROCKET event 4: on board the S.S. ANNE, JAMES buys a
@ "golden egg" MAGIKARP from a salesman, and the trio let slip their plan to rob
@ every passenger at the party. Two grunts, then JESSIE & JAMES, whose team now
@ includes that MAGIKARP. The salesman, amused, gives the player a NUGGET.
SSAnne_1F_Corridor_EventScript_RocketPlot::
	lockall
	setvar VAR_TEMP_1, 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	goto_if_eq VAR_ROCKET_RETRY, 4, SSAnne_1F_Corridor_EventScript_RocketRetry
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_SalesmanPitch
	msgbox SSAnne_1F_Corridor_Text_JamesBuys
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox SSAnne_1F_Corridor_Text_JessieScolds
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_MeowthPlan
	applymovement LOCALID_SSANNE_MEOWTH, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_SSANNE_JESSIE, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_SSANNE_JAMES, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	applymovement LOCALID_SSANNE_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	call_if_set FLAG_ROCKET_VIRIDIAN_PC, SSAnne_1F_Corridor_EventScript_MeowthSpotsPikachu
	call_if_unset FLAG_ROCKET_VIRIDIAN_PC, SSAnne_1F_Corridor_EventScript_MeowthSpotsKid
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox SSAnne_1F_Corridor_Text_JessieCallGrunts
	closemessage
	call SSAnne_1F_Corridor_EventScript_Grunts
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_JamesMagikarpToTheRescue
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox SSAnne_1F_Corridor_Text_RocketBattleIntro
	closemessage
SSAnne_1F_Corridor_EventScript_RocketBattle::
	setvar VAR_0x8004, 4
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_SSANNE_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_SS_ANNE, SSAnne_1F_Corridor_Text_RocketDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	setvar VAR_0x8008, LOCALID_SSANNE_JESSIE
	setvar VAR_0x8009, LOCALID_SSANNE_JAMES
	setvar VAR_0x800A, LOCALID_SSANNE_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_SSANNE_JESSIE
	removeobject LOCALID_SSANNE_JAMES
	removeobject LOCALID_SSANNE_MEOWTH
	setflag FLAG_ROCKET_SS_ANNE
	fadedefaultbgm
	setvar VAR_0x8004, 576
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, SSAnne_1F_Corridor_EventScript_RocketCoins
	setvar VAR_0x8004, 1344
SSAnne_1F_Corridor_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	applymovement LOCALID_SSANNE_SALESMAN, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_SalesmanLaughs
	giveitem ITEM_NUGGET
	setvar VAR_0x8004, ROCKET_HELD_NUGGET
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_SalesmanRareCandy
	giveitem ITEM_RARE_CANDY
	setvar VAR_0x8004, ROCKET_BONUS_SS_ANNE_CANDY
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_SalesmanBye
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_SALESMAN
	fadescreen FADE_FROM_BLACK
	releaseall
	end

@ The two grunts JESSIE calls, fought in order. A retry after losing to one of
@ them, or to the trio, skips any already beaten.
SSAnne_1F_Corridor_EventScript_Grunts::
	goto_if_defeated TRAINER_ROCKET_SS_ANNE_2, EventScript_Return
	setvar VAR_ROCKET_RETRY, 4
	clearflag FLAG_TEMP_3
	addobject LOCALID_SSANNE_GRUNT_1
	addobject LOCALID_SSANNE_GRUNT_2
	applymovement LOCALID_SSANNE_GRUNT_1, SSAnne_1F_Corridor_Movement_GruntIn
	applymovement LOCALID_SSANNE_GRUNT_2, SSAnne_1F_Corridor_Movement_GruntIn
	waitmovement 0
	goto_if_defeated TRAINER_ROCKET_SS_ANNE_1, SSAnne_1F_Corridor_EventScript_Grunt2
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_Grunt1Intro
	closemessage
	trainerbattle_no_intro TRAINER_ROCKET_SS_ANNE_1, SSAnne_1F_Corridor_Text_Grunt1Defeat
SSAnne_1F_Corridor_EventScript_Grunt2::
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox SSAnne_1F_Corridor_Text_Grunt2Intro
	closemessage
	trainerbattle_no_intro TRAINER_ROCKET_SS_ANNE_2, SSAnne_1F_Corridor_Text_Grunt2Defeat
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_GRUNT_1
	removeobject LOCALID_SSANNE_GRUNT_2
	fadescreen FADE_FROM_BLACK
	return

SSAnne_1F_Corridor_EventScript_RocketRetry::
	applymovement LOCALID_SSANNE_MEOWTH, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_SSANNE_JESSIE, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_SSANNE_JAMES, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	applymovement LOCALID_SSANNE_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	call EventScript_RocketTrioRetry
	call SSAnne_1F_Corridor_EventScript_Grunts
	goto SSAnne_1F_Corridor_EventScript_RocketBattle

SSAnne_1F_Corridor_EventScript_MeowthSpotsPikachu::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_MeowthSpotsPikachu
	return

SSAnne_1F_Corridor_EventScript_MeowthSpotsKid::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox SSAnne_1F_Corridor_Text_MeowthSpotsKid
	return

SSAnne_1F_Corridor_Movement_GruntIn:
	walk_left
	walk_left
	step_end

SSAnne_1F_Corridor_EventScript_WorkerM::
	msgbox SSAnne_1F_Corridor_Text_LeStrongSilentType, MSGBOX_NPC
	end

SSAnne_1F_Corridor_EventScript_Sailor::
	msgbox SSAnne_1F_Corridor_Text_PassengersAreRestless, MSGBOX_NPC
	end
