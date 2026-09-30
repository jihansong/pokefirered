Route102_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route102_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route102_OnFrame
	.byte 0

Route102_EventScript_H0::
	msgbox Route102_Text_H0, MSGBOX_NPC
	end

Route102_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_CALVIN_1, Route102_Text_H1_0, Route102_Text_H1_1
	msgbox Route102_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_RICK, Route102_Text_H2_0, Route102_Text_H2_1
	msgbox Route102_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_TIANA, Route102_Text_H3_0, Route102_Text_H3_1
	msgbox Route102_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H4::
	msgbox Route102_Text_H4, MSGBOX_NPC
	end

Route102_EventScript_HItem6::
	finditem ITEM_POTION
	end

Route102_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_ALLEN, Route102_Text_H5_0, Route102_Text_H5_1
	msgbox Route102_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H6::
	msgbox Route102_Text_H6, MSGBOX_SIGN
	end

Route102_EventScript_H7::
	msgbox Route102_Text_H7, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ v0.11.0 E5 (docs/v0.11.0-plan.md 4.5): WALLY's catching demo, the FR/LG old
@ man's tutorial battle with WALLY's back and a RALTS (StartWallyTutorialBattle).
@ The player arrives from the PETALBURG GYM beside WALLY (10,5); afterwards
@ both go back to the GYM lobby, where PetalburgCity_Gym_EventScript_WallyBack
@ ends the scene.
.equ LOCALID_ROUTE102_WALLY, 8

Route102_OnTransition::
	special HoennZ3_SetupObjects
	end

Route102_OnFrame::
	map_script_2 VAR_HOENN_SCENE_WALLY, 1, Route102_EventScript_WallyDemo
	.2byte 0

Route102_EventScript_WallyDemo::
	lockall
	goto_if_set FLAG_HOENN_WALLY_CAUGHT_RALTS, Route102_EventScript_WallyBackToGym
	playbgm MUS_RS_FOLLOW_ME, TRUE
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	msgbox Route102_Text_WallyNervous
	closemessage
	applymovement LOCALID_ROUTE102_WALLY, Route102_Movement_WallyIntoGrass
	waitmovement 0
	special StartWallyTutorialBattle
	waitstate
	applymovement LOCALID_ROUTE102_WALLY, Route102_Movement_WallyBack
	waitmovement 0
	msgbox Route102_Text_WallyCaughtRalts
	closemessage
	setflag FLAG_HOENN_WALLY_CAUGHT_RALTS
Route102_EventScript_WallyBackToGym::
	fadescreen FADE_TO_BLACK
	warp MAP_PETALBURG_CITY_GYM, 4, 109
	waitstate
	releaseall
	end

Route102_Movement_WallyIntoGrass:
	walk_left
	walk_in_place_faster_left
	step_end

Route102_Movement_WallyBack:
	walk_right
	walk_in_place_faster_right
	step_end
@ END PATCH
