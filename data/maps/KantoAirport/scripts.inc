KantoAirport_MapScripts::
	.byte 0

@ VERMILION AIRPORT (THUNDER YELLOW): flights to HOENN leave from the first
@ counter once the player is the CHAMPION. The flight lands at SLATEPORT.
KantoAirport_EventScript_HoennClerk::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, KantoAirport_EventScript_NotChampion
	msgbox KantoAirport_Text_FlyToHoenn, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, KantoAirport_EventScript_ComeAgain
	msgbox KantoAirport_Text_Boarding
	closemessage
	setvar VAR_0x8004, AIRPLANE_DEST_HOENN
	goto EventScript_TakeAirplane
	end

KantoAirport_EventScript_NotChampion::
	msgbox KantoAirport_Text_ChampionsOnly
	release
	end

KantoAirport_EventScript_ComeAgain::
	msgbox KantoAirport_Text_ComeAgain
	release
	end

KantoAirport_EventScript_JohtoClerk::
	msgbox KantoAirport_Text_JohtoSoon, MSGBOX_NPC
	end

KantoAirport_EventScript_InfoClerk::
	msgbox KantoAirport_Text_Info, MSGBOX_NPC
	end

KantoAirport_EventScript_Traveler::
	msgbox KantoAirport_Text_Traveler, MSGBOX_NPC
	end

KantoAirport_EventScript_Woman::
	msgbox KantoAirport_Text_Woman, MSGBOX_NPC
	end
