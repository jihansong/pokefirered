SkyPillar_5F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_5F_TY_RestoreFloor
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SkyPillar_5F_TY_RestoreFloor::
	special HoennSkyPillarRestoreFloor
	end
@ END PATCH
