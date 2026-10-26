SkyPillar_4F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_4F_TY_ClearLooseStones
	map_script MAP_SCRIPT_ON_TRANSITION, SkyPillar_4F_TY_Enter
	map_script MAP_SCRIPT_ON_RESUME, SkyPillar_4F_TY_Resume
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SkyPillar_4F_TY_Frames
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SkyPillar_4F_TY_ClearLooseStones::
	special HoennSkyPillarRestoreFloor
	end

SkyPillar_4F_TY_Enter::
	setvar VAR_TEMP_0, 1
	end

SkyPillar_4F_TY_Resume::
	setstepcallback STEP_CB_SKY_PILLAR_FLOOR
	end

SkyPillar_4F_TY_Frames::
	map_script_2 VAR_TEMP_0, 0, SkyPillar_4F_TY_Fall
	.2byte 0

SkyPillar_4F_TY_Fall::
	lockall
	delay 20
	applymovement LOCALID_PLAYER, SkyPillar_4F_TY_Hide
	waitmovement 0
	playse SE_FALL
	delay 60
	warphole MAP_SKY_PILLAR_3F
	waitstate
	end

SkyPillar_4F_TY_Hide::
	set_invisible
	step_end
@ END PATCH
