SkyPillar_Outside_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_Outside_TY_OpenStoryDoor
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Preserve the closed door until the existing sea-sky ascent is available.
SkyPillar_Outside_TY_OpenStoryDoor::
	goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, SkyPillar_Outside_TY_OpenDoor
	goto_if_set FLAG_HOENN_BADGE08_GET, SkyPillar_Outside_TY_OpenDoor
	end

SkyPillar_Outside_TY_OpenDoor::
	@ Original Emerald Pacifidlog Sky Pillar open-door top and bottom.
	setmetatile 14, 4, 0x2AA, TRUE
	setmetatile 14, 5, 0x2B2, FALSE
	end
@ END PATCH
