SkyPillar_1F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_1F_TY_RestoreFloor
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SkyPillar_1F_TY_RestoreFloor::
	special HoennSkyPillarRestoreFloor
	end
@ END PATCH
