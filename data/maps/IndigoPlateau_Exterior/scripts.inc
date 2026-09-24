IndigoPlateau_Exterior_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoPlateau_Exterior_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, IndigoPlateau_Exterior_OnFrame
	.byte 0

IndigoPlateau_Exterior_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_INDIGO_PLATEAU_EXTERIOR
	call_if_eq VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR, 1, IndigoPlateau_Exterior_EventScript_PlayCreditsMusic
	setflag FLAG_TEMP_1
	goto_if_eq VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR, 1, IndigoPlateau_Exterior_EventScript_TransitionEnd
	goto_if_set FLAG_ROCKET_INDIGO_TORCH, IndigoPlateau_Exterior_EventScript_TransitionEnd
	goto_if_unset FLAG_BADGE08_GET, IndigoPlateau_Exterior_EventScript_TransitionEnd
	setvar VAR_TEMP_1, 1
IndigoPlateau_Exterior_EventScript_TransitionEnd::
	end

IndigoPlateau_Exterior_EventScript_PlayCreditsMusic::
	playbgm MUS_CREDITS, 0
	return

@ Thunder Yellow v0.5.0, TEAM ROCKET event 10: the first time the player reaches
@ the plateau with all eight badges, the trio sneak out of the LEAGUE with the
@ INDIGO TORCH, the flame that opens every LEAGUE challenge. It flares up in
@ MEOWTH's paws and sends them flying. A LEAGUE official gives a FULL RESTORE.
@ v0.9.0 (#12): a double battle first. The trigger sits on the one-tile-wide
@ road up from ROUTE 23, so it can't be walked around, and until the torch is
@ back the door guard inside keeps the way to the ELITE FOUR shut. A loss sends
@ the player to the plateau's own POKéMON CENTER, a few steps away.
IndigoPlateau_Exterior_EventScript_RocketTorch::
	lockall
	setvar VAR_TEMP_1, 0
	opendoor 11, 6
	waitdooranim
	addobject LOCALID_INDIGO_JESSIE
	applymovement LOCALID_INDIGO_JESSIE, IndigoPlateau_Exterior_Movement_JessieExit
	waitmovement 0
	addobject LOCALID_INDIGO_JAMES
	applymovement LOCALID_INDIGO_JAMES, IndigoPlateau_Exterior_Movement_JamesExit
	waitmovement 0
	addobject LOCALID_INDIGO_MEOWTH
	applymovement LOCALID_INDIGO_MEOWTH, IndigoPlateau_Exterior_Movement_MeowthExit
	waitmovement 0
	closedoor 11, 6
	waitdooranim
	goto_if_eq VAR_ROCKET_RETRY, 12, IndigoPlateau_Exterior_EventScript_RocketTorchRetry
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_MeowthGotTheTorch
	applymovement LOCALID_INDIGO_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	msgbox IndigoPlateau_Exterior_Text_MeowthTwerpHere
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox IndigoPlateau_Exterior_Text_JessieIndigoTorch
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_JamesNoChallenges
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox IndigoPlateau_Exterior_Text_JessieEarnTheTorch
	closemessage
IndigoPlateau_Exterior_EventScript_RocketTorchBattle::
	setrespawn HEAL_LOCATION_INDIGO_PLATEAU
	setvar VAR_0x8004, 12
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_INDIGO_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_INDIGO, IndigoPlateau_Exterior_Text_RocketTorchDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	textcolor NPC_TEXT_COLOR_NEUTRAL
	goto_if_eq VAR_RESULT, PARTY_SIZE, IndigoPlateau_Exterior_EventScript_TorchFlaresInWind
	msgbox IndigoPlateau_Exterior_Text_PikachuZapsTorch
	closemessage
	playse SE_M_THUNDERBOLT
	fadescreenspeed FADE_TO_WHITE, 0
	fadescreenspeed FADE_FROM_WHITE, 0
	fadescreenspeed FADE_TO_WHITE, 0
	fadescreenspeed FADE_FROM_WHITE, 0
	goto IndigoPlateau_Exterior_EventScript_TorchFlares

IndigoPlateau_Exterior_EventScript_TorchFlaresInWind::
	msgbox IndigoPlateau_Exterior_Text_WindGusts
	closemessage
IndigoPlateau_Exterior_EventScript_TorchFlares::
	playse SE_M_FLAME_WHEEL
	applymovement LOCALID_INDIGO_MEOWTH, IndigoPlateau_Exterior_Movement_MeowthHotHot
	waitmovement 0
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_MeowthHotHotHot
	closemessage
	setvar VAR_0x8008, LOCALID_INDIGO_JESSIE
	setvar VAR_0x8009, LOCALID_INDIGO_JAMES
	setvar VAR_0x800A, LOCALID_INDIGO_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_INDIGO_JESSIE
	removeobject LOCALID_INDIGO_MEOWTH
	removeobject LOCALID_INDIGO_JAMES
	setflag FLAG_ROCKET_INDIGO_TORCH
	fadedefaultbgm
	addmoney 2200
	setvar VAR_0x8004, 2200
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, IndigoPlateau_Exterior_EventScript_RocketCoins
	addmoney 1760
	setvar VAR_0x8004, 3960
IndigoPlateau_Exterior_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox IndigoPlateau_Exterior_Text_TorchLanded
	closemessage
	opendoor 11, 6
	waitdooranim
	addobject LOCALID_INDIGO_OFFICIAL
	applymovement LOCALID_INDIGO_OFFICIAL, IndigoPlateau_Exterior_Movement_OfficialExit
	waitmovement 0
	closedoor 11, 6
	waitdooranim
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_OfficialThanks
	giveitem ITEM_FULL_RESTORE
	setvar VAR_0x8004, ROCKET_HELD_FULL_RESTORE
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_OfficialFireStone
	giveitem ITEM_FIRE_STONE
	setvar VAR_0x8004, ROCKET_BONUS_FIRE_STONE
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_MALE
	msgbox IndigoPlateau_Exterior_Text_OfficialGoodLuck
	closemessage
	applymovement LOCALID_INDIGO_OFFICIAL, IndigoPlateau_Exterior_Movement_OfficialReturn
	waitmovement 0
	opendoor 11, 6
	waitdooranim
	applymovement LOCALID_INDIGO_OFFICIAL, IndigoPlateau_Exterior_Movement_OfficialEnter
	waitmovement 0
	removeobject LOCALID_INDIGO_OFFICIAL
	closedoor 11, 6
	waitdooranim
	releaseall
	end

IndigoPlateau_Exterior_EventScript_RocketTorchRetry::
	applymovement LOCALID_INDIGO_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	call EventScript_RocketTrioRetry
	goto IndigoPlateau_Exterior_EventScript_RocketTorchBattle

@ The trio stop two tiles above the player on row 13.
IndigoPlateau_Exterior_Movement_JessieExit::
	walk_down
	walk_down
	walk_left
	walk_down
	walk_down
	walk_down
	face_down
	step_end

IndigoPlateau_Exterior_Movement_JamesExit::
	walk_down
	walk_down
	walk_right
	walk_down
	walk_down
	walk_down
	face_down
	step_end

IndigoPlateau_Exterior_Movement_MeowthExit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	face_down
	step_end

IndigoPlateau_Exterior_Movement_MeowthHotHot::
	jump_in_place_down
	jump_in_place_down
	jump_in_place_down
	step_end

IndigoPlateau_Exterior_Movement_OfficialExit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

IndigoPlateau_Exterior_Movement_OfficialReturn::
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

IndigoPlateau_Exterior_Movement_OfficialEnter::
	walk_up
	set_invisible
	step_end

IndigoPlateau_Exterior_OnFrame::
	map_script_2 VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR, 1, IndigoPlateau_Exterior_EventScript_Credits
	.2byte 0


@ After beating the champion, you are warped to the main
@ entrance of Indigo Plateau. This script starts running
@ immediately after your walking animation.
@ The script is timed to the music.
IndigoPlateau_Exterior_EventScript_Credits::
	lockall
	delay 105

	@ Rival exits building. Spawn a dummy object to lock the camera.
	opendoor 11, 6
	waitdooranim
	special SpawnCameraObject
	addobject LOCALID_CREDITS_RIVAL
	applymovement LOCALID_CREDITS_RIVAL, IndigoPlateau_Exterior_Movement_RivalExitBuilding
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PushPlayerOutOfWay
	waitmovement 0
	closedoor 11, 6
	waitdooranim

	@ Rival runs off
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerWatchRivalLeave
	applymovement LOCALID_CREDITS_RIVAL, IndigoPlateau_Exterior_Movement_RivalLeave
	waitmovement 0
	delay 100

	@ Oak exits building
	opendoor 11, 6
	waitdooranim
	addobject LOCALID_CREDITS_PROF_OAK
	applymovement LOCALID_CREDITS_PROF_OAK, IndigoPlateau_Exterior_Movement_OakExitBuilding
	waitmovement 0
	closedoor 11, 6
	waitdooranim
	delay 160

	@ Oak looks at player, then walks off
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerWatchOakLeave
	applymovement LOCALID_CREDITS_PROF_OAK, IndigoPlateau_Exterior_Movement_OakLeave
	waitmovement 0
	delay 100

	@ Player begin to leave
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerBeginLeave
	waitmovement 0
	delay 155
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerFaceLeague
	waitmovement 0
	delay 90

	@ Player runs off
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerTurnAround
	waitmovement 0
	applymovement LOCALID_PLAYER, IndigoPlateau_Exterior_Movement_PlayerLeave
	waitmovement 0

	@ Reset the map state and roll the credits
	special RemoveCameraObject
	setvar VAR_MAP_SCENE_INDIGO_PLATEAU_EXTERIOR, 0
	removeobject LOCALID_CREDITS_RIVAL
	removeobject LOCALID_CREDITS_PROF_OAK
	special DoCredits
	waitstate
	releaseall
	end

IndigoPlateau_Exterior_Movement_PlayerLeave::
	player_run_down
	player_run_down
	player_run_down
	player_run_down
	player_run_down
	player_run_down
	step_end

@ Unused
IndigoPlateau_Exterior_Movement_PlayerExitBuilding::
	walk_down
	walk_down
	step_end

IndigoPlateau_Exterior_Movement_PlayerWatchRivalLeave::
	delay_16
	delay_4
	walk_in_place_faster_down
	step_end

IndigoPlateau_Exterior_Movement_PlayerWatchOakLeave::
	delay_8
	walk_in_place_faster_right
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	walk_in_place_faster_down
	step_end

IndigoPlateau_Exterior_Movement_PlayerBeginLeave::
	walk_right
	delay_16
	walk_down
	walk_down
	delay_16
	delay_16
	step_end

IndigoPlateau_Exterior_Movement_PlayerTurnAround::
	walk_in_place_faster_down
	step_end

IndigoPlateau_Exterior_Movement_PushPlayerOutOfWay::
	face_right
	lock_facing_direction
	walk_left
	unlock_facing_direction
	step_end

IndigoPlateau_Exterior_Movement_PlayerFaceLeague::
	walk_in_place_faster_up
	step_end

IndigoPlateau_Exterior_Movement_RivalLeave::
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

IndigoPlateau_Exterior_Movement_RivalExitBuilding::
	walk_fast_down
	step_end

IndigoPlateau_Exterior_Movement_OakLeave::
	walk_in_place_faster_left
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	delay_16
	walk_in_place_faster_down
	delay_16
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

IndigoPlateau_Exterior_Movement_OakExitBuilding::
	walk_down
	step_end
