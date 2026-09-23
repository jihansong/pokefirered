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

@ HOENN's own BADGES are flags (see constants/flags_hoenn_story.h); this keeper
@ reads them out, since the trainer card's badge row belongs to KANTO.
SlateportCity_Harbor_EventScript_BadgeKeeper::
	lock
	faceplayer
	specialvar VAR_RESULT, CountHoennBadges
	buffernumberstring STR_VAR_1, VAR_RESULT
	goto_if_eq VAR_RESULT, 0, SlateportCity_Harbor_EventScript_BadgeKeeperNone
	msgbox SlateportCity_Harbor_Text_BadgeCount
	goto_if_unset FLAG_HOENN_BADGE02_GET, EventScript_ReleaseEnd
	msgbox SlateportCity_Harbor_Text_BadgeKnuckle
	release
	end

SlateportCity_Harbor_EventScript_BadgeKeeperNone::
	msgbox SlateportCity_Harbor_Text_BadgeNone
	release
	end
