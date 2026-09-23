@ The timed run down the CYCLING ROAD (v0.8.0). The original road was only a
@ road; the gates now hold a clock and a record board.
Route110_SeasideCyclingRoadNorthEntrance_EventScript_Attendant::
	lock
	faceplayer
	goto_if_eq VAR_HOENN_CYCLING_STATE, 1, Route110_SeasideCyclingRoadNorthEntrance_EventScript_AlreadyRunning
	msgbox Route110_SeasideCyclingRoadNorthEntrance_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route110_SeasideCyclingRoadNorthEntrance_EventScript_Declined
	special CyclingRoad_StartRun
	msgbox Route110_SeasideCyclingRoadNorthEntrance_Text_Go
	release
	end

Route110_SeasideCyclingRoadNorthEntrance_EventScript_AlreadyRunning::
	msgbox Route110_SeasideCyclingRoadNorthEntrance_Text_StillRunning
	release
	end

Route110_SeasideCyclingRoadNorthEntrance_EventScript_Declined::
	msgbox Route110_SeasideCyclingRoadNorthEntrance_Text_Declined
	release
	end
