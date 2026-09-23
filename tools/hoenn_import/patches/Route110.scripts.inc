@ The roadside board shows the run the south gate keeps (event 1).
Route110_EventScript_Board::
	special CyclingRoad_GetRecord
	goto_if_eq VAR_RESULT, 0, Route110_EventScript_BoardEmpty
	buffernumberstring STR_VAR_1, VAR_RESULT
	msgbox Route110_Text_BoardRecord, MSGBOX_SIGN
	end

Route110_EventScript_BoardEmpty::
	msgbox Route110_Text_BoardEmpty, MSGBOX_SIGN
	end
