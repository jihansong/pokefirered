Route110_TrickHouseCorridor_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route110_TrickHouseCorridor_OnTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Ported from pokeemerald (the map data is identical), text written fresh.
Route110_TrickHouseCorridor_OnTransition:
	setvar VAR_HOENN_TRICK_ENTER_FROM_CORRIDOR, 1
	end
@ END PATCH
