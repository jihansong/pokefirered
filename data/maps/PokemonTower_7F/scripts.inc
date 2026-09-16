PokemonTower_7F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonTower_7F_OnTransition
	.byte 0

PokemonTower_7F_OnTransition::
	call PokemonTower_7F_EventScript_HideJessieJames
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
	msgbox PokemonTower_7F_Text_JessieJamesIntro
	closemessage
	setvar VAR_LAST_TALKED, LOCALID_POKEMON_TOWER_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_POKEMON_TOWER, PokemonTower_7F_Text_JessieJamesDefeat
	msgbox PokemonTower_7F_Text_JessieJamesBlastOff
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_POKEMON_TOWER_JESSIE
	removeobject LOCALID_POKEMON_TOWER_JAMES
	fadescreen FADE_FROM_BLACK
	setvar VAR_MAP_SCENE_POKEMON_TOWER_7F_JESSIE_JAMES, 1
	releaseall
	end

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
