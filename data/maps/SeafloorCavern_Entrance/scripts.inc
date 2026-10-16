SeafloorCavern_Entrance_MapScripts::
@ Thunder Yellow native Dive v1
	map_script MAP_SCRIPT_ON_DIVE_WARP, SeafloorCavern_Entrance_NativeDiveWarp
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow native Dive v1
SeafloorCavern_Entrance_NativeDiveWarp::
	setdivewarp MAP_UNDERWATER_SEAFLOOR_CAVERN, 6, 6
	end
@ END PATCH
