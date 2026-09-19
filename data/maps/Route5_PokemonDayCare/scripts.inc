@ Handled by data/scripts/day_care.inc

Route5_PokemonDayCare_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route5_PokemonDayCare_OnTransition
	.byte 0

Route5_PokemonDayCare_OnTransition::
	setflag FLAG_HIDE_ROUTE5_EGG_APPRAISER
	specialvar VAR_RESULT, ShouldShowEggAppraiser
	call_if_eq VAR_RESULT, TRUE, Route5_PokemonDayCare_EventScript_ShowEggAppraiser
	end

Route5_PokemonDayCare_EventScript_ShowEggAppraiser::
	clearflag FLAG_HIDE_ROUTE5_EGG_APPRAISER
	return
