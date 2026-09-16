CeruleanCave_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CeruleanCave_1F_OnTransition
	.byte 0

CeruleanCave_1F_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_CERULEAN_CAVE_1F
	setflag FLAG_HIDE_CERULEAN_CAVE_PIKABLU
	setvar VAR_TEMP_1, 1
	goto_if_unset FLAG_HEARD_PIKABLU_RUMOR, CeruleanCave_1F_EventScript_NoPikablu
	goto_if_set FLAG_CAUGHT_PIKABLU, CeruleanCave_1F_EventScript_NoPikablu
	clearflag FLAG_HIDE_CERULEAN_CAVE_PIKABLU
	setobjectxyperm LOCALID_CERULEAN_CAVE_PIKABLU, 37, 11
	setvar VAR_TEMP_1, 0
	end

CeruleanCave_1F_EventScript_NoPikablu::
	end

@ Once the player has heard the rumor, a blue PIKACHU is seen at the channel by the
@ entrance. It dashes off across the lake; following it by SURF leads to a MARILL.
CeruleanCave_1F_EventScript_PikabluDashesOff::
	lockall
	setvar VAR_TEMP_1, 1
	applymovement LOCALID_CERULEAN_CAVE_PIKABLU, CeruleanCave_1F_Movement_PikabluNotice
	waitmovement 0
	applymovement LOCALID_CERULEAN_CAVE_PIKABLU, CeruleanCave_1F_Movement_PikabluDash
	waitmovement 0
	setobjectxyperm LOCALID_CERULEAN_CAVE_PIKABLU, 23, 1
	msgbox CeruleanCave_1F_Text_BluePokemonDashedOff
	releaseall
	end

CeruleanCave_1F_EventScript_Pikablu::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	faceplayer
	waitse
	playmoncry SPECIES_MARILL, CRY_MODE_ENCOUNTER
	msgbox CeruleanCave_1F_Text_Pikablu
	waitmoncry
	setwildbattle SPECIES_MARILL, 35
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CeruleanCave_1F_EventScript_CaughtPikablu
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CERULEAN_CAVE_PIKABLU
	fadescreen FADE_FROM_BLACK
	msgbox CeruleanCave_1F_Text_PikabluDoveAway
	release
	end

CeruleanCave_1F_EventScript_CaughtPikablu::
	special NamePikablu
	setflag FLAG_CAUGHT_PIKABLU
	removeobject LOCALID_CERULEAN_CAVE_PIKABLU
	release
	end

CeruleanCave_1F_Movement_PikabluNotice::
	face_down
	emote_exclamation_mark
	jump_in_place_down
	step_end

CeruleanCave_1F_Movement_PikabluDash::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	step_end
