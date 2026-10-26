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
