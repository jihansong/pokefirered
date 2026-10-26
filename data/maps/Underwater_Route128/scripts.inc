Underwater_Route128_MapScripts::
	map_script MAP_SCRIPT_ON_DIVE_WARP, Underwater_Route128_TY_SurfaceWarp
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ The cave exit lies under a surface reef. Emerge on the adjacent deep water.
Underwater_Route128_TY_SurfaceWarp::
	getplayerxy VAR_0x8006, VAR_0x8007
	compare VAR_0x8006, 38
	goto_if_ne Underwater_Route128_TY_SurfaceSamePosition
	compare VAR_0x8007, 26
	goto_if_ne Underwater_Route128_TY_SurfaceSamePosition
	setdivewarp MAP_ROUTE128, 38, 27
	end

Underwater_Route128_TY_SurfaceSamePosition::
	setdivewarp MAP_ROUTE128, VAR_0x8006, VAR_0x8007
	end
@ END PATCH
