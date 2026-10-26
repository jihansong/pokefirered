SeafloorCavern_Room1_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SeafloorCavern_Room1_TY_PuzzleEntry
	map_script MAP_SCRIPT_ON_RESUME, SeafloorCavern_Room1_TY_PuzzleEntry
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Original Emerald boulders; map-local save compatibility only.
SeafloorCavern_Room1_TY_PuzzleEntry::
	special HoennSeafloorMarkPuzzleSave
	end

SeafloorCavern_Room1_EventScript_Grunt1::
	trainerbattle_single TRAINER_HOENN_GRUNT_SEAFLOOR_CAVERN_1, SeafloorCavern_Room1_Text_Grunt1Intro, SeafloorCavern_Room1_Text_Grunt1Defeat
	msgbox SeafloorCavern_Room1_Text_Grunt1PostBattle, MSGBOX_AUTOCLOSE
	end

SeafloorCavern_Room1_EventScript_Grunt2::
	trainerbattle_single TRAINER_HOENN_GRUNT_SEAFLOOR_CAVERN_2, SeafloorCavern_Room1_Text_Grunt2Intro, SeafloorCavern_Room1_Text_Grunt2Defeat
	msgbox SeafloorCavern_Room1_Text_Grunt2PostBattle, MSGBOX_AUTOCLOSE
	end
@ END PATCH
