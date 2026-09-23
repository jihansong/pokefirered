SlateportCity_Harbor_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SlateportCity_Harbor_OnFrame
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
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

@ Event 1: the plane from KANTO puts the player down here, and CAPTAIN STERN
@ is waiting. He points at the two NPCs that carry HOENN's hints from here on.
.equ LOCALID_SLATEPORT_HARBOR_STERN, 4

SlateportCity_Harbor_OnFrame::
	map_script_2 VAR_HOENN_SCENE_HARBOR, 0, SlateportCity_Harbor_EventScript_ArrivalScene
	.2byte 0

SlateportCity_Harbor_EventScript_ArrivalScene::
	lockall
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	applymovement LOCALID_SLATEPORT_HARBOR_STERN, Common_Movement_ExclamationMark
	waitmovement 0
	delay 30
	msgbox SlateportCity_Harbor_Text_SternArrival
	closemessage
	setflag FLAG_HOENN_MET_STERN
	setvar VAR_HOENN_SCENE_HARBOR, 1
	setvar VAR_HOENN_STAGE1_PROGRESS, 1
	releaseall
	end

SlateportCity_Harbor_EventScript_Stern::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_MUSEUM_DEFENDED, SlateportCity_Harbor_EventScript_SternAfterMuseum
	msgbox SlateportCity_Harbor_Text_SternMuseum
	release
	end

SlateportCity_Harbor_EventScript_SternAfterMuseum::
	msgbox SlateportCity_Harbor_Text_SternThanks
	release
	end
@ END PATCH
