PokemonMansion_B1F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, PokemonMansion_B1F_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonMansion_B1F_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, PokemonMansion_B1F_OnFrame
	.byte 0

PokemonMansion_B1F_OnLoad::
	call_if_set FLAG_POKEMON_MANSION_SWITCH_STATE, PokemonMansion_EventScript_PressSwitch_B1F
	call_if_set FLAG_OPENED_MANSION_HIDDEN_STAIRS, PokemonMansion_B1F_EventScript_SetHiddenStairs
	end

@ Once every MEWTWO diary in the mansion and the three secret lab logs have been
@ read, the floor beside the statue switch opens onto stairs down to B4F.
PokemonMansion_B1F_OnTransition::
	setvar VAR_TEMP_1, 0
	goto_if_set FLAG_OPENED_MANSION_HIDDEN_STAIRS, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_DIARY_JULY_5, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_DIARY_JULY_10, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_DIARY_FEB_6, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_DIARY_SEP_1, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_1, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_2, EventScript_Return
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_3, EventScript_Return
	setvar VAR_TEMP_1, 1
	end

PokemonMansion_B1F_OnFrame::
	map_script_2 VAR_TEMP_1, 1, PokemonMansion_B1F_EventScript_OpenHiddenStairs
	.2byte 0

PokemonMansion_B1F_EventScript_OpenHiddenStairs::
	lockall
	setvar VAR_TEMP_1, 0
	delay 30
	playse SE_M_EARTHQUAKE
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 3
	special ShakeScreen
	delay 40
	waitse
	playse SE_UNLOCK
	call PokemonMansion_B1F_EventScript_SetHiddenStairs
	special DrawWholeMapView
	waitse
	setflag FLAG_OPENED_MANSION_HIDDEN_STAIRS
	msgbox PokemonMansion_B1F_Text_FloorOpenedByStatue
	releaseall
	end

PokemonMansion_B1F_EventScript_SetHiddenStairs::
	setmetatile 21, 30, 0x2D0, TRUE
	setmetatile 22, 30, 0x2D1, TRUE
	setmetatile 23, 30, 0x2D2, FALSE
	setmetatile 21, 31, 0x2D8, TRUE
	setmetatile 22, 31, 0x2D9, TRUE
	setmetatile 23, 31, 0x2DA, FALSE
	return

PokemonMansion_B1F_EventScript_Statue::
	lockall
	setvar VAR_0x8004, 3
	call PokemonMansion_EventScript_SecretSwitch
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	releaseall
	end

PokemonMansion_B1F_EventScript_DiarySep1st::
	lockall
	setflag FLAG_READ_MANSION_DIARY_SEP_1
	msgbox PokemonMansion_B1F_Text_MewtwoIsFarTooPowerful
	releaseall
	end

PokemonMansion_B1F_EventScript_Lewis::
	trainerbattle_single TRAINER_BURGLAR_LEWIS, PokemonMansion_B1F_Text_LewisIntro, PokemonMansion_B1F_Text_LewisDefeat
	msgbox PokemonMansion_B1F_Text_LewisPostBattle, MSGBOX_AUTOCLOSE
	end

PokemonMansion_B1F_EventScript_Ivan::
	trainerbattle_single TRAINER_SCIENTIST_IVAN, PokemonMansion_B1F_Text_IvanIntro, PokemonMansion_B1F_Text_IvanDefeat
	msgbox PokemonMansion_B1F_Text_IvanPostBattle, MSGBOX_AUTOCLOSE
	end
