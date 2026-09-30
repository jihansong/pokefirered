Route109_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route109_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route109_OnFrame
	.byte 0

Route109_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_DAVID, Route109_Text_H0_0, Route109_Text_H0_1
	msgbox Route109_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_ALICE, Route109_Text_H1_0, Route109_Text_H1_1
	msgbox Route109_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_HUEY, Route109_Text_H2_0, Route109_Text_H2_1
	msgbox Route109_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_EDMOND, Route109_Text_H3_0, Route109_Text_H3_1
	msgbox Route109_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_RICKY_1, Route109_Text_H4_0, Route109_Text_H4_1
	msgbox Route109_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_LOLA_1, Route109_Text_H5_0, Route109_Text_H5_1
	msgbox Route109_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H6::
	msgbox Route109_Text_H6, MSGBOX_NPC
	end

Route109_EventScript_HItem16::
	finditem ITEM_PP_UP
	end

Route109_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_GWEN, Route109_Text_H7_0, Route109_Text_H7_1
	msgbox Route109_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_AUSTINA, Route109_Text_H8_0, Route109_Text_H8_1
	msgbox Route109_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_CARTER, Route109_Text_H9_0, Route109_Text_H9_1
	msgbox Route109_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H10::
	msgbox Route109_Text_H10, MSGBOX_NPC
	end

Route109_EventScript_H11::
	msgbox Route109_Text_H11, MSGBOX_NPC
	end

Route109_EventScript_H12::
	msgbox Route109_Text_H12, MSGBOX_NPC
	end

Route109_EventScript_H13::
	trainerbattle_double TRAINER_HOENN_MEL_AND_PAUL, Route109_Text_H13_0, Route109_Text_H13_1, Route109_Text_H13_1
	msgbox Route109_Text_H13_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H15::
	msgbox Route109_Text_H15, MSGBOX_NPC
	end

Route109_EventScript_H16::
	msgbox Route109_Text_H16, MSGBOX_NPC
	end

Route109_EventScript_H17::
	trainerbattle_single TRAINER_HOENN_HAILEY, Route109_Text_H17_0, Route109_Text_H17_1
	msgbox Route109_Text_H17_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H18::
	trainerbattle_single TRAINER_HOENN_CHANDLER, Route109_Text_H18_0, Route109_Text_H18_1
	msgbox Route109_Text_H18_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_HItem17::
	finditem ITEM_POTION
	end

Route109_EventScript_H19::
	trainerbattle_single TRAINER_HOENN_ELIJAH, Route109_Text_H19_0, Route109_Text_H19_1
	msgbox Route109_Text_H19_2, MSGBOX_AUTOCLOSE
	end

Route109_EventScript_H20::
	msgbox Route109_Text_H20, MSGBOX_SIGN
	end

Route109_EventScript_H21::
	msgbox Route109_Text_H21, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
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
@ END PATCH
