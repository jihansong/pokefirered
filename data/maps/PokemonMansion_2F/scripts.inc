PokemonMansion_2F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, PokemonMansion_2F_OnLoad
	.byte 0

PokemonMansion_2F_OnLoad::
	call_if_set FLAG_POKEMON_MANSION_SWITCH_STATE, PokemonMansion_EventScript_PressSwitch_2F
	end

PokemonMansion_2F_EventScript_Statue::
	lockall
	setvar VAR_0x8004, 1
	call PokemonMansion_EventScript_SecretSwitch
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	releaseall
	end

PokemonMansion_2F_EventScript_DiaryJuly5th::
	lockall
	setflag FLAG_READ_MANSION_DIARY_JULY_5
	msgbox PokemonMansion_1F_Text_NewMonDiscoveredInGuyanaJungle
	releaseall
	end

PokemonMansion_2F_EventScript_DiaryJuly10th::
	lockall
	setflag FLAG_READ_MANSION_DIARY_JULY_10
	msgbox PokemonMansion_1F_Text_ChristenedDiscoveredMonMew
	releaseall
	end

PokemonMansion_2F_EventScript_Arnie::
	trainerbattle_single TRAINER_BURGLAR_ARNIE, PokemonMansion_1F_Text_ArnieIntro, PokemonMansion_1F_Text_ArnieDefeat
	msgbox PokemonMansion_1F_Text_ArniePostBattle, MSGBOX_AUTOCLOSE
	end
