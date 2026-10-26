@ Complete the existing attendant's offer using the existing upper station.
Route112_CableCarStation_EventScript_H0::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	msgbox Route112_CableCarStation_Text_H0, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route112_CableCarStation_TY_Declined
	closemessage
	getplayerxy VAR_0x8005, VAR_0x8006
	goto_if_ne VAR_0x8005, 6, Route112_CableCarStation_TY_Declined
	goto_if_ne VAR_0x8006, 7, Route112_CableCarStation_TY_Declined
	applymovement 1, Route112_CableCarStation_Cable_Lead
	applymovement LOCALID_PLAYER, Route112_CableCarStation_Cable_Board
	waitmovement 0
	setvar VAR_0x8004, 0
	specialvar VAR_RESULT, HoennCableCarRide
	goto_if_eq VAR_RESULT, FALSE, Route112_CableCarStation_Cable_Abort
	waitstate
	end

Route112_CableCarStation_TY_Declined::
	release
	end

Route112_CableCarStation_Cable_Abort::
	applymovement LOCALID_PLAYER, Route112_CableCarStation_Cable_Exit
	applymovement 1, Route112_CableCarStation_Cable_Follow
	waitmovement 0
	releaseall
	end
Route112_CableCarStation_Cable_Lead:
	walk_up
	walk_right
	walk_in_place_faster_left
	step_end
Route112_CableCarStation_Cable_Board:
	walk_up
	walk_up
	delay_16
	step_end
Route112_CableCarStation_Cable_Exit:
	walk_down
	walk_down
	delay_16
	step_end
Route112_CableCarStation_Cable_Follow:
	delay_16
	walk_left
	walk_down
	step_end
