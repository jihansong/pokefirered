KantoAirport_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, KantoAirport_OnTransition
	.byte 0

@ Until the player has watched it once, the airliner waits out on the runway
@ and walking into the window lounge sets off its taxi to the gate.
KantoAirport_OnTransition::
	goto_if_set FLAG_SAW_AIRPORT_PLANE_TAXI, KantoAirport_EventScript_PlaneAtGate
	setobjectxyperm LOCALID_KANTO_AIRPORT_PLANE, 30, 1
	setvar VAR_TEMP_1, 1
	end

KantoAirport_EventScript_PlaneAtGate::
	end

@ The first time the player steps into the lounge: walk up to the glass and
@ watch the plane roll down the runway, turn onto the apron and stop at the gate.
KantoAirport_EventScript_PlaneTaxi::
	lockall
	setvar VAR_TEMP_1, 0
	getplayerxy VAR_0x8004, VAR_0x8005
KantoAirport_EventScript_PlaneTaxiWalkUp::
	goto_if_le VAR_0x8005, 4, KantoAirport_EventScript_PlaneTaxiWatch
	applymovement LOCALID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	subvar VAR_0x8005, 1
	goto KantoAirport_EventScript_PlaneTaxiWalkUp

KantoAirport_EventScript_PlaneTaxiWatch::
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	delay 20
	playse SE_M_GUST
	applymovement LOCALID_KANTO_AIRPORT_PLANE, KantoAirport_Movement_PlaneTaxi
	waitmovement LOCALID_KANTO_AIRPORT_PLANE
	copyobjectxytoperm LOCALID_KANTO_AIRPORT_PLANE
	setflag FLAG_SAW_AIRPORT_PLANE_TAXI
	msgbox KantoAirport_Text_PlaneArrived
	releaseall
	end

KantoAirport_Movement_PlaneTaxi:
	walk_slower_down
	walk_slower_down
	face_left
	delay_16
	walk_slower_left
	walk_slower_left
	walk_slower_left
	delay_16
	face_down
	step_end

KantoAirport_EventScript_PlaneSpotter::
	lock
	faceplayer
	goto_if_set FLAG_SAW_AIRPORT_PLANE_TAXI, KantoAirport_EventScript_PlaneSpotterSaw
	msgbox KantoAirport_Text_PlaneSpotter
	release
	end

KantoAirport_EventScript_PlaneSpotterSaw::
	msgbox KantoAirport_Text_PlaneSpotterSaw
	release
	end

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
