Underwater_SeafloorCavern_MapScripts::
@ Thunder Yellow native Dive v1
	map_script MAP_SCRIPT_ON_DIVE_WARP, Underwater_SeafloorCavern_NativeDiveWarp
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow native Dive v1
Underwater_SeafloorCavern_NativeDiveWarp::
	setdivewarp MAP_SEAFLOOR_CAVERN_ENTRANCE, 10, 16
	end
@ END PATCH
