Route22_MapScripts::
	.byte 0

Route22_EventScript_EarlyRivalTriggerTop::
	lockall
	setvar VAR_TEMP_1, 0
	goto Route22_EventScript_EarlyRival
	end

Route22_EventScript_EarlyRivalTriggerMid::
	lockall
	setvar VAR_TEMP_1, 1
	setobjectxyperm LOCALID_ROUTE22_RIVAL, 25, 5
	goto Route22_EventScript_EarlyRival
	end

Route22_EventScript_EarlyRivalTriggerBottom::
	lockall
	setvar VAR_TEMP_1, 2
	setobjectxyperm LOCALID_ROUTE22_RIVAL, 25, 5
	goto Route22_EventScript_EarlyRival
	end

Route22_EventScript_EarlyRival::
	textcolor NPC_TEXT_COLOR_MALE
	playbgm MUS_ENCOUNTER_RIVAL, 0
	addobject LOCALID_ROUTE22_RIVAL
	call_if_eq VAR_TEMP_1, 0, Route22_EventScript_EarlyRivalApproach
	call_if_eq VAR_TEMP_1, 1, Route22_EventScript_EarlyRivalApproach
	call_if_eq VAR_TEMP_1, 2, Route22_EventScript_EarlyRivalApproachBottom
	delay 6
	msgbox Route22_Text_EarlyRivalIntro
	trainerbattle_earlyrival TRAINER_RIVAL_ROUTE22_EARLY, RIVAL_BATTLE_HEAL_AFTER, Route22_Text_EarlyRivalDefeat, Text_RivalVictory
	call_if_eq VAR_RESULT, FALSE, Route22_EventScript_EarlyRivalCheckEvolveJolteon
	msgbox Route22_Text_EarlyRivalPostBattle
	closemessage
	delay 10
	playbgm MUS_RIVAL_EXIT, 0
	call_if_eq VAR_TEMP_1, 0, Route22_EventScript_EarlyRivalExit
	call_if_eq VAR_TEMP_1, 1, Route22_EventScript_EarlyRivalExit
	call_if_eq VAR_TEMP_1, 2, Route22_EventScript_EarlyRivalExitBottom
	fadedefaultbgm
	removeobject LOCALID_ROUTE22_RIVAL
	setvar VAR_MAP_SCENE_ROUTE22, 2
	releaseall
	end

Route22_EventScript_EarlyRivalApproach::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_RivalApproach
	waitmovement 0
	return

Route22_EventScript_EarlyRivalApproachBottom::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_RivalApproachBottom
	applymovement LOCALID_PLAYER, Route22_Movement_PlayerFaceRival
	waitmovement 0
	return

@ Beating the rival here after beating him in the lab sends his Eevee down the Jolteon line.
Route22_EventScript_EarlyRivalCheckEvolveJolteon::
	call_if_eq VAR_RIVAL_STARTER, RIVAL_STARTER_FLAREON, Route22_EventScript_EarlyRivalSetJolteon
	return

Route22_EventScript_EarlyRivalSetJolteon::
	setvar VAR_RIVAL_STARTER, RIVAL_STARTER_JOLTEON
	return

Route22_EventScript_EarlyRivalExit::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_EarlyRivalExit
	waitmovement 0
	return

Route22_EventScript_EarlyRivalExitBottom::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_EarlyRivalExitBottom
	waitmovement 0
	return

Route22_Movement_UnusedRivalExit:: @ 8
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

Route22_Movement_EarlyRivalExit::
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

Route22_Movement_EarlyRivalExitBottom::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

Route22_Movement_RivalApproach::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

Route22_Movement_RivalApproachBottom::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_in_place_faster_down
	step_end

Route22_Movement_PlayerFaceRival::
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_8
	walk_in_place_faster_up
	step_end

Route22_EventScript_LateRivalTriggerTop::
	lockall
	setvar VAR_TEMP_1, 0
	goto Route22_EventScript_LateRival
	end

Route22_EventScript_LateRivalTriggerMid::
	lockall
	setvar VAR_TEMP_1, 1
	setobjectxyperm LOCALID_ROUTE22_RIVAL, 25, 5
	goto Route22_EventScript_LateRival
	end

Route22_EventScript_LateRivalTriggerBottom::
	lockall
	setvar VAR_TEMP_1, 2
	setobjectxyperm LOCALID_ROUTE22_RIVAL, 25, 5
	goto Route22_EventScript_LateRival
	end

Route22_EventScript_LateRival::
	textcolor NPC_TEXT_COLOR_MALE
	playbgm MUS_ENCOUNTER_RIVAL, 0
	addobject LOCALID_ROUTE22_RIVAL
	call_if_eq VAR_TEMP_1, 0, Route22_EventScript_LateRivalApproach
	call_if_eq VAR_TEMP_1, 1, Route22_EventScript_LateRivalApproach
	call_if_eq VAR_TEMP_1, 2, Route22_EventScript_LateRivalApproachBottom
	msgbox Route22_Text_LateRivalIntro
	setvar VAR_LAST_TALKED, LOCALID_ROUTE22_RIVAL
	call_if_eq VAR_RIVAL_STARTER, RIVAL_STARTER_JOLTEON, Route22_EventScript_LateRivalJolteon
	call_if_eq VAR_RIVAL_STARTER, RIVAL_STARTER_FLAREON, Route22_EventScript_LateRivalFlareon
	call_if_eq VAR_RIVAL_STARTER, RIVAL_STARTER_VAPOREON, Route22_EventScript_LateRivalVaporeon
	msgbox Route22_Text_LateRivalPostBattle
	closemessage
	delay 10
	playbgm MUS_RIVAL_EXIT, 0
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_LateRivalExit
	waitmovement 0
	fadedefaultbgm
	removeobject LOCALID_ROUTE22_RIVAL
	setvar VAR_MAP_SCENE_ROUTE22, 4
	releaseall
	end

Route22_EventScript_LateRivalApproach::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_RivalApproach
	waitmovement 0
	return

Route22_EventScript_LateRivalApproachBottom::
	applymovement LOCALID_ROUTE22_RIVAL, Route22_Movement_RivalApproachBottom
	applymovement LOCALID_PLAYER, Route22_Movement_PlayerFaceRival
	waitmovement 0
	return

Route22_EventScript_LateRivalJolteon::
	trainerbattle_no_intro TRAINER_RIVAL_ROUTE22_LATE_JOLTEON, Route22_Text_LateRivalDefeat
	return

Route22_EventScript_LateRivalFlareon::
	trainerbattle_no_intro TRAINER_RIVAL_ROUTE22_LATE_FLAREON, Route22_Text_LateRivalDefeat
	return

Route22_EventScript_LateRivalVaporeon::
	trainerbattle_no_intro TRAINER_RIVAL_ROUTE22_LATE_VAPOREON, Route22_Text_LateRivalDefeat
	return

Route22_Movement_LateRivalExit::
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

Route22_EventScript_LeagueGateSign::
	msgbox Route22_Text_LeagueGateSign, MSGBOX_SIGN
	end
