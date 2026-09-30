@ v0.11.0: MR. BRINEY's boat at the ROUTE 109 landing when its last trip
@ ended here (E9), and the pair on the beach hear it's running again
Route109_OnTransition::
	special HoennZ3_SetupObjects
	end

Route109_OnFrame::
	map_script_2 VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE109 | BRINEY_ARRIVING, Route109_EventScript_BrineyArrived
	.2byte 0

Route109_EventScript_BrineyArrived::
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE109
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	goto Route104_EventScript_BrineyArrived
	end

Route109_EventScript_H14::
	trainerbattle_double TRAINER_HOENN_MEL_AND_PAUL, Route109_Text_H14_0, Route109_Text_H14_1, Route109_Text_H14_1
	goto_if_set FLAG_HOENN_PEEKO_RESCUED, Route109_EventScript_H14BrineyBack
	msgbox Route109_Text_H14_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H14BrineyBack::
	msgbox Route109_Text_H14_2_BrineyBack, MSGBOX_AUTOCLOSE
	end
