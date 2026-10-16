Route116_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route116_OnTransition
	.byte 0

Route116_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_JOEY, Route116_Text_H0_0, Route116_Text_H0_1
	msgbox Route116_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_JOSE, Route116_Text_H1_0, Route116_Text_H1_1
	msgbox Route116_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_HItem38::
	finditem ITEM_ETHER
	end

Route116_EventScript_HItem39::
	finditem ITEM_REPEL
	end

Route116_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_CLARK, Route116_Text_H2_0, Route116_Text_H2_1
	msgbox Route116_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_HItem40::
	finditem ITEM_HP_UP
	end

Route116_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_JANICE, Route116_Text_H3_0, Route116_Text_H3_1
	msgbox Route116_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_KAREN_1, Route116_Text_H4_0, Route116_Text_H4_1
	msgbox Route116_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_JERRY_1, Route116_Text_H5_0, Route116_Text_H5_1
	msgbox Route116_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_HItem41::
	finditem ITEM_X_SPECIAL
	end

Route116_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_SARAH, Route116_Text_H6_0, Route116_Text_H6_1
	msgbox Route116_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_DAWSON, Route116_Text_H7_0, Route116_Text_H7_1
	msgbox Route116_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_HItem42::
	finditem ITEM_POTION
	end

Route116_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_JOHNSON, Route116_Text_H8_0, Route116_Text_H8_1
	msgbox Route116_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_DEVAN, Route116_Text_H9_0, Route116_Text_H9_1
	msgbox Route116_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route116_EventScript_H10::
	msgbox Route116_Text_H10, MSGBOX_SIGN
	end

Route116_EventScript_H12::
	msgbox Route116_Text_H12, MSGBOX_SIGN
	end

Route116_EventScript_H13::
	msgbox Route116_Text_H13, MSGBOX_SIGN
	end

Route116_EventScript_H14::
	msgbox Route116_Text_H14, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ MR. BRINEY waits beside the entrance while PEEKO is missing. His existing
@ shared hide flag moves him back to his cottage and boat after the rescue.
Route116_OnTransition::
	special HoennZ3_SetupObjects
	end

Route116_EventScript_BrineyPeekoMissing::
	lock
	faceplayer
	msgbox Route116_Text_BrineyPeekoMissing
	release
	end

@ E12: the employee's own thank-you for retrieving the DEVON GOODS.
@ Keep the reward pending if the ball stack is full.
Route116_EventScript_RepeatBallWorker::
	lock
	faceplayer
	goto_if_lt VAR_HOENN_SCENE_DEVON, 3, Route116_EventScript_RepeatBallBeforeRescue
	goto_if_set FLAG_HOENN_GOT_REPEAT_BALL, Route116_EventScript_RepeatBallDone
	msgbox Route116_Text_RepeatBallThanks
	giveitem ITEM_REPEAT_BALL
	goto_if_eq VAR_RESULT, FALSE, Route116_EventScript_RepeatBallNoRoom
	setflag FLAG_HOENN_GOT_REPEAT_BALL
Route116_EventScript_RepeatBallDone::
	msgbox Route116_Text_RepeatBallDone
	release
	end

Route116_EventScript_RepeatBallBeforeRescue::
	msgbox Route116_Text_RepeatBallBeforeRescue
	release
	end

Route116_EventScript_RepeatBallNoRoom::
	msgbox Route116_Text_RepeatBallNoRoom
	release
	end

Route116_EventScript_H11::
	goto_if_set FLAG_HOENN_RUSTURF_OPEN, Route116_EventScript_TunnelSignFinished
	msgbox Route116_Text_H11, MSGBOX_SIGN
	end

Route116_EventScript_TunnelSignFinished::
	msgbox Route116_Text_TunnelSignFinished, MSGBOX_SIGN
	end
@ END PATCH
