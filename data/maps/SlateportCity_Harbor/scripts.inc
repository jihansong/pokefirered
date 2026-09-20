SlateportCity_Harbor_MapScripts::
	.byte 0


@ Airline counter for the flight back to KANTO (VERMILION AIRPORT)
SlateportCity_Harbor_EventScript_AirlineClerk::
	lock
	faceplayer
	msgbox SlateportCity_Harbor_Text_FlyToKanto, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SlateportCity_Harbor_EventScript_AirlineNo
	msgbox KantoAirport_Text_Boarding
	closemessage
	setvar VAR_0x8004, AIRPLANE_DEST_KANTO
	goto EventScript_TakeAirplane
	end

SlateportCity_Harbor_EventScript_FlyWarning::
	msgbox SlateportCity_Harbor_Text_FlyWarning, MSGBOX_NPC
	end

SlateportCity_Harbor_EventScript_AirlineNo::
	msgbox KantoAirport_Text_ComeAgain
	release
	end
