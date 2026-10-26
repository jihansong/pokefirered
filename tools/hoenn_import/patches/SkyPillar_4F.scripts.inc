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
