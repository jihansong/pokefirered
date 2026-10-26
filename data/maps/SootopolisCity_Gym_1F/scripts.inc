SootopolisCity_Gym_1F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SootopolisCity_Gym_1F_TY_OpenStoryStairs
	map_script MAP_SCRIPT_ON_TRANSITION, SootopolisCity_Gym_1F_TY_IceEnter
	map_script MAP_SCRIPT_ON_RESUME, SootopolisCity_Gym_1F_TY_IceResume
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SootopolisCity_Gym_1F_TY_IceFrames
	.byte 0

SootopolisCity_Gym_1F_EventScript_H1::
	msgbox SootopolisCity_Gym_1F_Text_H1, MSGBOX_NPC
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ THYL_LEAGUE_V1
SootopolisCity_Gym_1F_EventScript_H0::
	goto_if_set FLAG_HOENN_BADGE08_GET, SootopolisCity_Gym_1F_TY_Boss
	goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, SootopolisCity_Gym_1F_TY_Boss
	msgbox SootopolisCity_Gym_1F_Text_TY_StormGate, MSGBOX_NPC
	end

SootopolisCity_Gym_1F_TY_Boss::
	goto_if_defeated TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_TY_Reward
	trainerbattle_single TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_Text_H0_0, SootopolisCity_Gym_1F_Text_H0_1, SootopolisCity_Gym_1F_TY_Reward
	goto SootopolisCity_Gym_1F_TY_Reward

SootopolisCity_Gym_1F_TY_Reward::
	lock
	faceplayer
	goto_if_not_defeated TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_TY_Done
	setflag FLAG_HOENN_BADGE08_GET
	goto_if_set FLAG_HOENN_GOT_TM03, SootopolisCity_Gym_1F_TY_Post
	msgbox SootopolisCity_Gym_1F_TY_Badge
	checkitemspace ITEM_TM03
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_Gym_1F_TY_Full
	giveitem ITEM_TM03
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_Gym_1F_TY_Full
	setflag FLAG_HOENN_GOT_TM03
SootopolisCity_Gym_1F_TY_Post::
	msgbox SootopolisCity_Gym_1F_Text_H0_2
SootopolisCity_Gym_1F_TY_Done::
	release
	end

SootopolisCity_Gym_1F_TY_Full::
	msgbox SootopolisCity_Gym_1F_TY_BagFull
	release
	end

@ Thunder Yellow Hoenn sea-sky chapter v1

@ Original Emerald ice progression; counter is map-local in Thunder Yellow.
SootopolisCity_Gym_1F_TY_OpenStoryStairs::
	special HoennSootopolisRestoreIce
	end

SootopolisCity_Gym_1F_TY_IceEnter::
	special HoennSootopolisResetIce
	end

SootopolisCity_Gym_1F_TY_IceResume::
	setstepcallback STEP_CB_SOOTOPOLIS_ICE
	end

SootopolisCity_Gym_1F_TY_IceFrames::
	map_script_2 VAR_TEMP_0, 8, SootopolisCity_Gym_1F_TY_UnlockIce
	map_script_2 VAR_TEMP_0, 28, SootopolisCity_Gym_1F_TY_UnlockIce
	map_script_2 VAR_TEMP_0, 67, SootopolisCity_Gym_1F_TY_UnlockIce
	map_script_2 VAR_TEMP_0, 0, SootopolisCity_Gym_1F_TY_Fall
	.2byte 0

SootopolisCity_Gym_1F_TY_UnlockIce::
	addvar VAR_TEMP_0, 1
	delay 40
	playse SE_ICE_STAIRS
	special HoennSootopolisRestoreIce
	special DrawWholeMapView
	end

SootopolisCity_Gym_1F_TY_Fall::
	lockall
	delay 20
	applymovement LOCALID_PLAYER, SootopolisCity_Gym_1F_TY_FallMovement
	waitmovement 0
	playse SE_FALL
	delay 60
	warphole MAP_SOOTOPOLIS_CITY_GYM_B1F
	waitstate
	end

SootopolisCity_Gym_1F_TY_FallMovement::
	set_invisible
	step_end
@ END PATCH
