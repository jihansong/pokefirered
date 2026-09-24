PokemonTower_7F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonTower_7F_OnTransition
	.byte 0

PokemonTower_7F_OnTransition::
	call PokemonTower_7F_EventScript_HideJessieJames
	setflag FLAG_TEMP_5
	call_if_set FLAG_RESCUED_MR_FUJI, PokemonTower_7F_EventScript_TryShowN
	end

PokemonTower_7F_EventScript_MrFuji::
	lock
	faceplayer
	famechecker FAMECHECKER_MRFUJI, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	setflag FLAG_HIDE_TOWER_FUJI
	clearflag FLAG_HIDE_POKEHOUSE_FUJI
	setflag FLAG_RESCUED_MR_FUJI
	msgbox PokemonTower_7F_Text_MrFujiThankYouFollowMe
	closemessage
	warp MAP_LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE, 4, 7
	waitstate
	release
	end

PokemonTower_7F_EventScript_Grunt1::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_19, PokemonTower_7F_Text_Grunt1Intro, PokemonTower_7F_Text_Grunt1Defeat, PokemonTower_7F_EventScript_DefeatedGrunt1
	msgbox PokemonTower_7F_Text_Grunt1PostBattle, MSGBOX_AUTOCLOSE
	end

PokemonTower_7F_EventScript_DefeatedGrunt1::
	msgbox PokemonTower_7F_Text_Grunt1PostBattle
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_eq VAR_0x8004, 10, PokemonTower_7F_EventScript_Grunt1ExitMid
	goto_if_eq VAR_0x8004, 11, PokemonTower_7F_EventScript_Grunt1ExitRight
	goto_if_eq VAR_0x8004, 9, PokemonTower_7F_EventScript_Grunt1ExitLeft
	applymovement LOCALID_POKEMON_TOWER_GRUNT1, PokemonTower_7F_Movement_Grunt1Exit
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt1
	end

PokemonTower_7F_EventScript_Grunt1ExitMid::
	applymovement LOCALID_POKEMON_TOWER_GRUNT1, PokemonTower_7F_Movement_Grunt1ExitMid
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt1
	end

PokemonTower_7F_EventScript_Grunt1ExitRight::
	applymovement LOCALID_POKEMON_TOWER_GRUNT1, PokemonTower_7F_Movement_Grunt1ExitRight
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt1
	end

PokemonTower_7F_EventScript_Grunt1ExitLeft::
	applymovement LOCALID_POKEMON_TOWER_GRUNT1, PokemonTower_7F_Movement_Grunt1ExitLeft
	waitmovement 0
	playse SE_EXIT
	delay 25
	goto PokemonTower_7F_EventScript_RemoveGrunt1
	end

PokemonTower_7F_EventScript_RemoveGrunt1::
	removeobject LOCALID_POKEMON_TOWER_GRUNT1
	release
	end

PokemonTower_7F_Movement_Grunt1ExitMid::
	walk_down
	walk_right
	walk_down
	walk_down
	walk_down
	walk_right
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt1ExitRight::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt1Exit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt1ExitLeft::
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_down
	walk_down
	walk_in_place_faster_left
	step_end

PokemonTower_7F_EventScript_Grunt2::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_20, PokemonTower_7F_Text_Grunt2Intro, PokemonTower_7F_Text_Grunt2Defeat, PokemonTower_7F_EventScript_DefeatedGrunt2
	msgbox PokemonTower_7F_Text_Grunt2PostBattle, MSGBOX_AUTOCLOSE
	end

PokemonTower_7F_EventScript_DefeatedGrunt2::
	famechecker FAMECHECKER_MRFUJI, 1
	msgbox PokemonTower_7F_Text_Grunt2PostBattle
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_eq VAR_0x8004, 12, PokemonTower_7F_EventScript_Grunt2ExitLeft
	goto_if_eq VAR_0x8004, 13, PokemonTower_7F_EventScript_Grunt2ExitRight
	applymovement LOCALID_POKEMON_TOWER_GRUNT2, PokemonTower_7F_Movement_Grunt2Exit
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt2
	end

PokemonTower_7F_EventScript_Grunt2ExitLeft::
	applymovement LOCALID_POKEMON_TOWER_GRUNT2, PokemonTower_7F_Movement_Grunt2ExitLeft
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt2
	end

PokemonTower_7F_EventScript_Grunt2ExitRight::
	applymovement LOCALID_POKEMON_TOWER_GRUNT2, PokemonTower_7F_Movement_Grunt2ExitRight
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt2
	end

PokemonTower_7F_EventScript_RemoveGrunt2::
	removeobject LOCALID_POKEMON_TOWER_GRUNT2
	release
	end

PokemonTower_7F_Movement_Grunt2ExitLeft::
	walk_down
	walk_down
	walk_down
	walk_left
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt2Exit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt2ExitRight::
	walk_left
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_EventScript_Grunt3::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_21, PokemonTower_7F_Text_Grunt3Intro, PokemonTower_7F_Text_Grunt3Defeat, PokemonTower_7F_EventScript_DefeatedGrunt3
	msgbox PokemonTower_7F_Text_Grunt3PostBattle, MSGBOX_AUTOCLOSE
	end

PokemonTower_7F_EventScript_DefeatedGrunt3::
	msgbox PokemonTower_7F_Text_Grunt3PostBattle
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_eq VAR_0x8004, 10, PokemonTower_7F_EventScript_Grunt3ExitRight
	goto_if_eq VAR_0x8004, 9, PokemonTower_7F_EventScript_Grunt3ExitLeft
	applymovement LOCALID_POKEMON_TOWER_GRUNT3, PokemonTower_7F_Movement_Grunt3Exit
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt3
	end

PokemonTower_7F_EventScript_Grunt3ExitRight::
	applymovement LOCALID_POKEMON_TOWER_GRUNT3, PokemonTower_7F_Movement_Grunt3ExitRight
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt3
	end

PokemonTower_7F_EventScript_Grunt3ExitLeft::
	applymovement LOCALID_POKEMON_TOWER_GRUNT3, PokemonTower_7F_Movement_Grunt3ExitLeft
	waitmovement 0
	goto PokemonTower_7F_EventScript_RemoveGrunt3
	end

PokemonTower_7F_EventScript_RemoveGrunt3::
	removeobject LOCALID_POKEMON_TOWER_GRUNT3
	release
	end

PokemonTower_7F_EventScript_Unused::
	release
	end

PokemonTower_7F_Movement_Grunt3ExitRight::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_right
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt3Exit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_Movement_Grunt3ExitLeft::
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PokemonTower_7F_EventScript_JessieJamesTrigger0::
	lockall
	setvar VAR_TEMP_1, 0
	goto PokemonTower_7F_EventScript_JessieJames
	end

PokemonTower_7F_EventScript_JessieJamesTrigger1::
	lockall
	setvar VAR_TEMP_1, 1
	goto PokemonTower_7F_EventScript_JessieJames
	end

PokemonTower_7F_EventScript_JessieJamesTrigger2::
	lockall
	setvar VAR_TEMP_1, 2
	goto PokemonTower_7F_EventScript_JessieJames
	end

@ Jessie & James ambush the player, as in Pokémon Yellow.
PokemonTower_7F_EventScript_JessieJames::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playbgm MUS_ENCOUNTER_ROCKET, 0
	msgbox PokemonTower_7F_Text_JessieJamesStop
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	call_if_eq VAR_TEMP_1, 0, PokemonTower_7F_EventScript_JessieJamesAppear0
	call_if_eq VAR_TEMP_1, 1, PokemonTower_7F_EventScript_JessieJamesAppear1
	call_if_eq VAR_TEMP_1, 2, PokemonTower_7F_EventScript_JessieJamesAppear2
	setobjectxyperm LOCALID_POKEMON_TOWER_MEOWTH, 11, 12
	addobject LOCALID_POKEMON_TOWER_MEOWTH
	goto_if_eq VAR_ROCKET_RETRY, 6, PokemonTower_7F_EventScript_JessieJamesRetry
	call PokemonTower_7F_EventScript_GhostPrank
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PokemonTower_7F_Text_JessieJamesIntro
	closemessage
PokemonTower_7F_EventScript_JessieJamesBattle::
	setvar VAR_0x8004, 6
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_POKEMON_TOWER_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_POKEMON_TOWER, PokemonTower_7F_Text_JessieJamesDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PokemonTower_7F_Text_JessieJamesBlastOff
	closemessage
	setvar VAR_0x8008, LOCALID_POKEMON_TOWER_JESSIE
	setvar VAR_0x8009, LOCALID_POKEMON_TOWER_JAMES
	setvar VAR_0x800A, LOCALID_POKEMON_TOWER_MEOWTH
	special RocketTrioBlastOff
	waitstate
	removeobject LOCALID_POKEMON_TOWER_JESSIE
	removeobject LOCALID_POKEMON_TOWER_JAMES
	removeobject LOCALID_POKEMON_TOWER_MEOWTH
	setvar VAR_MAP_SCENE_POKEMON_TOWER_7F_JESSIE_JAMES, 1
	addmoney 768
	setvar VAR_0x8004, 768
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, PokemonTower_7F_EventScript_RocketCoins
	addmoney 1024
	setvar VAR_0x8004, 1792
PokemonTower_7F_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	msgbox PokemonTower_7F_Text_CleanseTagLeft
	giveitem ITEM_CLEANSE_TAG
	setvar VAR_0x8004, ROCKET_BONUS_CLEANSE_TAG
	call EventScript_RocketRewardResult
	releaseall
	end

PokemonTower_7F_EventScript_JessieJamesRetry::
	call EventScript_RocketTrioRetry
	goto PokemonTower_7F_EventScript_JessieJamesBattle

@ Thunder Yellow v0.5.0, TEAM ROCKET event 5: before the battle the tower's GASTLY
@ and HAUNTER play a trick on the trio, with MEOWTH along.
PokemonTower_7F_EventScript_GhostPrank::
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox PokemonTower_7F_Text_JessieNoGhostsHere
	closemessage
	fadescreenspeed FADE_TO_BLACK, 2
	playmoncry SPECIES_GASTLY, CRY_MODE_NORMAL
	waitmoncry
	fadescreenspeed FADE_FROM_BLACK, 2
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PokemonTower_7F_Text_ColdBreath
	closemessage
	applymovement LOCALID_POKEMON_TOWER_JESSIE, PokemonTower_7F_Movement_Startled
	applymovement LOCALID_POKEMON_TOWER_JAMES, PokemonTower_7F_Movement_Startled
	applymovement LOCALID_POKEMON_TOWER_MEOWTH, PokemonTower_7F_Movement_Startled
	waitmovement 0
	textcolor NPC_TEXT_COLOR_MALE
	msgbox PokemonTower_7F_Text_JamesLickedEar
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox PokemonTower_7F_Text_JessieStopScreaming
	textcolor NPC_TEXT_COLOR_MALE
	msgbox PokemonTower_7F_Text_MeowthBehindYou
	closemessage
	playmoncry SPECIES_HAUNTER, CRY_MODE_NORMAL
	applymovement LOCALID_POKEMON_TOWER_JESSIE, PokemonTower_7F_Movement_Shiver
	applymovement LOCALID_POKEMON_TOWER_JAMES, PokemonTower_7F_Movement_Shiver
	applymovement LOCALID_POKEMON_TOWER_MEOWTH, PokemonTower_7F_Movement_Shiver
	waitmovement 0
	waitmoncry
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PokemonTower_7F_Text_LaughterFades
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox PokemonTower_7F_Text_JessieNotScared
	return

PokemonTower_7F_Movement_Startled:
	jump_in_place_down
	jump_in_place_down
	step_end

PokemonTower_7F_Movement_Shiver:
	walk_in_place_faster_left
	walk_in_place_faster_right
	walk_in_place_faster_left
	walk_in_place_faster_right
	face_down
	step_end

PokemonTower_7F_EventScript_JessieJamesAppear0::
	setobjectxyperm LOCALID_POKEMON_TOWER_JESSIE, 10, 11
	setobjectxyperm LOCALID_POKEMON_TOWER_JAMES, 11, 11
	addobject LOCALID_POKEMON_TOWER_JESSIE
	addobject LOCALID_POKEMON_TOWER_JAMES
	applymovement LOCALID_POKEMON_TOWER_JESSIE, PokemonTower_7F_EventScript_JessieJamesMovement0
	applymovement LOCALID_POKEMON_TOWER_JAMES, PokemonTower_7F_EventScript_JessieJamesMovement0
	waitmovement 0
	return

PokemonTower_7F_EventScript_JessieJamesMovement0:
	walk_down
	walk_down
	step_end

PokemonTower_7F_EventScript_JessieJamesAppear1::
	setobjectxyperm LOCALID_POKEMON_TOWER_JESSIE, 11, 11
	setobjectxyperm LOCALID_POKEMON_TOWER_JAMES, 12, 11
	addobject LOCALID_POKEMON_TOWER_JESSIE
	addobject LOCALID_POKEMON_TOWER_JAMES
	applymovement LOCALID_POKEMON_TOWER_JESSIE, PokemonTower_7F_EventScript_JessieJamesMovement1
	applymovement LOCALID_POKEMON_TOWER_JAMES, PokemonTower_7F_EventScript_JessieJamesMovement1
	waitmovement 0
	return

PokemonTower_7F_EventScript_JessieJamesMovement1:
	walk_down
	walk_down
	step_end

PokemonTower_7F_EventScript_JessieJamesAppear2::
	setobjectxyperm LOCALID_POKEMON_TOWER_JESSIE, 12, 11
	setobjectxyperm LOCALID_POKEMON_TOWER_JAMES, 11, 11
	addobject LOCALID_POKEMON_TOWER_JESSIE
	addobject LOCALID_POKEMON_TOWER_JAMES
	applymovement LOCALID_POKEMON_TOWER_JESSIE, PokemonTower_7F_EventScript_JessieJamesMovement2
	applymovement LOCALID_POKEMON_TOWER_JAMES, PokemonTower_7F_EventScript_JessieJamesMovement2
	waitmovement 0
	return

PokemonTower_7F_EventScript_JessieJamesMovement2:
	walk_down
	walk_down
	step_end

PokemonTower_7F_EventScript_HideJessieJames::
	setflag FLAG_HIDE_POKEMON_TOWER_7F_JESSIE_JAMES
	return

PokemonTower_7F_EventScript_TryShowN::
	goto_if_set FLAG_MET_N_TOWER, EventScript_Return
	clearflag FLAG_TEMP_5
	return

@ v0.6.0: after MR. FUJI is rescued, N stands where he was held.
PokemonTower_7F_EventScript_N::
	lock
	faceplayer
	msgbox PokemonTower_7F_Text_NVoices
	call EventScript_NHearsPikachu
	msgbox PokemonTower_7F_Text_NLetsBattle
	trainerbattle_no_intro TRAINER_N_TOWER, PokemonTower_7F_Text_NDefeat
	msgbox PokemonTower_7F_Text_NAfter
	setflag FLAG_MET_N_TOWER
	goto EventScript_NLeaves
	end
