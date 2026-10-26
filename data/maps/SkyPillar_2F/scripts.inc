SkyPillar_2F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_2F_TY_RestoreFloor
	map_script MAP_SCRIPT_ON_TRANSITION, SkyPillar_2F_TY_Enter
	map_script MAP_SCRIPT_ON_RESUME, SkyPillar_2F_TY_Resume
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SkyPillar_2F_TY_Frames
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SkyPillar_2F_TY_RestoreFloor::
	special HoennSkyPillarRestoreFloor
	end

SkyPillar_2F_TY_Enter::
	setvar VAR_TEMP_0, 1
	end

SkyPillar_2F_TY_Resume::
	setstepcallback STEP_CB_SKY_PILLAR_FLOOR
	end

SkyPillar_2F_TY_Frames::
	map_script_2 VAR_TEMP_0, 0, SkyPillar_2F_TY_Fall
	.2byte 0

SkyPillar_2F_TY_Fall::
	lockall
	delay 20
	applymovement LOCALID_PLAYER, SkyPillar_2F_TY_Hide
	waitmovement 0
	playse SE_FALL
	delay 60
	warphole MAP_SKY_PILLAR_1F
	waitstate
	end

SkyPillar_2F_TY_Hide::
	set_invisible
	step_end
@ END PATCH
