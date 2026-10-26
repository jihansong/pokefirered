SkyPillar_3F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_3F_TY_RestoreCleanFloor
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)

SkyPillar_3F_TY_RestoreCleanFloor::
	special HoennSkyPillarRestoreFloor
	end
@ END PATCH
