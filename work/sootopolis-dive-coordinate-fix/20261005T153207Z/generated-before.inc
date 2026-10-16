Underwater_SootopolisCity_MapScripts::
	map_script MAP_SCRIPT_ON_DIVE_WARP, Underwater_SootopolisCity_NativeDiveWarp
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow Sootopolis Dive v1
Underwater_SootopolisCity_NativeDiveWarp::
	setdivewarp MAP_SOOTOPOLIS_CITY, 31, 53
	end
@ END PATCH
