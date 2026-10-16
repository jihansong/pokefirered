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
