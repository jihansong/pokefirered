Route19_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route19_OnTransition
	.byte 0

Route19_OnTransition::
	setflag FLAG_HIDE_ROUTE19_SURF_PIKACHU
	end

@ Yellow's "Pikachu's Beach": a surfer on the beach teaches the starter PIKACHU
@ SURF and FLY once it jumps 7 of 10 waves in a timing minigame.
Route19_EventScript_SurfDude::
	lock
	faceplayer
	goto_if_set FLAG_SURFING_PIKACHU, Route19_EventScript_SurfDudeAfterClear
	specialvar VAR_RESULT, IsStarterPikachuLead
	goto_if_eq VAR_RESULT, FALSE, Route19_EventScript_SurfDudeNoPikachu
	msgbox Route19_Text_SurfDudeWantToTry, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route19_EventScript_SurfDudeDecline
	msgbox Route19_Text_SurfDudeRules
	closemessage
	fadescreen FADE_TO_BLACK
	clearflag FLAG_HIDE_ROUTE19_SURF_PIKACHU
	addobject LOCALID_ROUTE19_SURF_PIKACHU
	special HideFollowerPikachu
	fadescreen FADE_FROM_BLACK
	setvar VAR_0x8004, LOCALID_ROUTE19_SURF_PIKACHU
	special StartSurfingPikachuMinigame
	waitstate
	copyvar VAR_0x8008, VAR_RESULT
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE19_SURF_PIKACHU
	setflag FLAG_HIDE_ROUTE19_SURF_PIKACHU
	special ShowFollowerPikachu
	fadescreen FADE_FROM_BLACK
	buffernumberstring STR_VAR_1, VAR_0x8008
	goto_if_ge VAR_0x8008, 7, Route19_EventScript_SurfDudeCleared
	msgbox Route19_Text_SurfDudeTryAgain
	release
	end

Route19_EventScript_SurfDudeCleared::
	msgbox Route19_Text_SurfDudeCleared
	setflag FLAG_SURFING_PIKACHU
	call Route19_EventScript_TeachSurf
	call Route19_EventScript_TeachFly
	msgbox Route19_Text_SurfDudeRideTheWaves
	release
	end

Route19_EventScript_TeachSurf::
	setvar VAR_0x8005, MOVETUTOR_PIKACHU_SURF
	call Route19_EventScript_ChoosePikachu
	return

Route19_EventScript_TeachFly::
	setvar VAR_0x8005, MOVETUTOR_PIKACHU_FLY
	call Route19_EventScript_ChoosePikachu
	return

Route19_EventScript_ChoosePikachu::
	msgbox Route19_Text_SurfDudeTeachMove
	closemessage
	fadescreen FADE_TO_BLACK
	specialvar VAR_0x8007, GetStarterPikachuPartySlotForScript
	call EventScript_ChooseMoveTutorMon
	return

Route19_EventScript_SurfDudeAfterClear::
	msgbox Route19_Text_SurfDudeAfterClear
	goto_if_set FLAG_TEMP_1, Route19_EventScript_SurfDudeEnd
	setflag FLAG_TEMP_1
	msgbox Route19_Text_SurfDudeRelearn, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route19_EventScript_SurfDudeEnd
	specialvar VAR_RESULT, IsStarterPikachuLead
	goto_if_eq VAR_RESULT, FALSE, Route19_EventScript_SurfDudeNoPikachu
	call Route19_EventScript_TeachSurf
	call Route19_EventScript_TeachFly
Route19_EventScript_SurfDudeEnd::
	release
	end

Route19_EventScript_SurfDudeNoPikachu::
	msgbox Route19_Text_SurfDudeNoPikachu
	release
	end

Route19_EventScript_SurfDudeDecline::
	msgbox Route19_Text_SurfDudeDecline
	release
	end

Route19_EventScript_RouteSign::
	msgbox Route19_Text_RouteSign, MSGBOX_SIGN
	end
