SeafloorCavern_Room2_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SeafloorCavern_Room2_TY_PuzzleEntry
	map_script MAP_SCRIPT_ON_RESUME, SeafloorCavern_Room2_TY_PuzzleEntry
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Original Emerald boulders; map-local save compatibility only.
SeafloorCavern_Room2_TY_PuzzleEntry::
	special HoennSeafloorMarkPuzzleSave
	end
@ END PATCH
