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
