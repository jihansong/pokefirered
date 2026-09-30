@ v0.11.0 (docs/v0.11.0-plan.md 4.9, 4.11, 4.12): MR. BRINEY's boat, the
@ MUDKIP in the inlet below his pier, and the gifts the imported dialogue
@ promised.

Route104_OnTransition::
	special HoennZ3_SetupObjects
	end

Route104_OnFrame::
	map_script_2 VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE104 | BRINEY_ARRIVING, Route104_EventScript_BrineyArrivedHere
	.2byte 0

@ ---------------------------------------------------------------- E9
@ MR. BRINEY at any of his three docks (ROUTE 104, DEWFORD, ROUTE 109; the
@ other two maps name this script too). He offers the two docks he isn't at;
@ the trip is a fade and a warp (plan Q4 (a)), and the dock map greets the
@ player on arrival (BRINEY_ARRIVING in VAR_HOENN_BRINEY_STATE until then).
Route104_EventScript_Briney::
	lock
	faceplayer
	message Route104_Text_BrineyWhereTo
	waitmessage
	goto_if_eq VAR_HOENN_BRINEY_STATE, BRINEY_AT_DEWFORD, Route104_EventScript_BrineyFromDewford
	goto_if_eq VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE109, Route104_EventScript_BrineyFromRoute109
	multichoice 0, 0, MULTICHOICE_BRINEY_FROM_ROUTE104, FALSE
	goto_if_eq VAR_RESULT, 0, Route104_EventScript_BrineySailDewford
	goto_if_eq VAR_RESULT, 1, Route104_EventScript_BrineySailRoute109
	goto Route104_EventScript_BrineyStay

Route104_EventScript_BrineyFromDewford::
	multichoice 0, 0, MULTICHOICE_BRINEY_FROM_DEWFORD, FALSE
	goto_if_eq VAR_RESULT, 0, Route104_EventScript_BrineySailRoute104
	goto_if_eq VAR_RESULT, 1, Route104_EventScript_BrineySailRoute109
	goto Route104_EventScript_BrineyStay

Route104_EventScript_BrineyFromRoute109::
	multichoice 0, 0, MULTICHOICE_BRINEY_FROM_ROUTE109, FALSE
	goto_if_eq VAR_RESULT, 0, Route104_EventScript_BrineySailRoute104
	goto_if_eq VAR_RESULT, 1, Route104_EventScript_BrineySailDewford
	goto Route104_EventScript_BrineyStay

Route104_EventScript_BrineyStay::
	msgbox Route104_Text_BrineyStay
	release
	end

Route104_EventScript_BrineySailRoute104::
	bufferstring STR_VAR_1, Route104_Text_BrineyMenuRoute104
	call Route104_EventScript_BrineySetSail
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE104 | BRINEY_ARRIVING
	warp MAP_ROUTE104, 12, 52
	waitstate
	release
	end

Route104_EventScript_BrineySailDewford::
	bufferstring STR_VAR_1, Route104_Text_BrineyMenuDewford
	call Route104_EventScript_BrineySetSail
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_DEWFORD | BRINEY_ARRIVING
	warp MAP_DEWFORD_TOWN, 13, 9
	waitstate
	release
	end

Route104_EventScript_BrineySailRoute109::
	bufferstring STR_VAR_1, Route104_Text_BrineyMenuRoute109
	call Route104_EventScript_BrineySetSail
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE109 | BRINEY_ARRIVING
	warp MAP_ROUTE109, 22, 24
	waitstate
	release
	end

Route104_EventScript_BrineySetSail::
	msgbox Route104_Text_BrineySetSail
	closemessage
	playse SE_EXIT
	fadescreen FADE_TO_BLACK
	return

Route104_EventScript_BrineyArrivedHere::
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_ROUTE104
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	goto Route104_EventScript_BrineyArrived
	end

@ Shared by the three docks' frame scripts, which set the state first
Route104_EventScript_BrineyArrived::
	lockall
	msgbox Route104_Text_BrineyArrived
	releaseall
	end

@ ---------------------------------------------------------------- E11
@ The MUDKIP in the inlet, any time; givemon as CELIO's starters. Party and
@ BOXES full: the flag stays off and it waits.
Route104_EventScript_Water::
	lockall
	goto_if_set FLAG_HOENN_GOT_MUDKIP_ON_BEACH, Route104_EventScript_WaterAfter
	msgbox Route104_Text_WaterRipples
	closemessage
	showmonpic SPECIES_MUDKIP, 10, 3
	playmoncry SPECIES_MUDKIP, CRY_MODE_WEAK
	msgbox Route104_Text_MudkipFound
	waitmoncry
	hidemonpic
	msgbox Route104_Text_MudkipTended
	setvar VAR_TEMP_1, SPECIES_MUDKIP
	call EventScript_GiveGiftMonLv5
	goto_if_eq VAR_RESULT, FALSE, Route104_EventScript_MudkipNoRoom
	setflag FLAG_HOENN_GOT_MUDKIP_ON_BEACH
	releaseall
	end

Route104_EventScript_MudkipNoRoom::
	msgbox Route104_Text_MudkipNoRoom
	releaseall
	end

Route104_EventScript_WaterAfter::
	msgbox Route104_Text_WaterAfter
	releaseall
	end

@ ---------------------------------------------------------------- E12
Route104_EventScript_H13::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_TM09, Route104_EventScript_Tm09After
	msgbox Route104_Text_H13
	giveitem ITEM_TM09
	goto_if_eq VAR_RESULT, FALSE, Route104_EventScript_Tm09BagFull
	setflag FLAG_HOENN_GOT_TM09
Route104_EventScript_Tm09After::
	msgbox Route104_Text_Tm09After
	release
	end

Route104_EventScript_Tm09BagFull::
	msgbox Route104_Text_Tm09BagFull
	release
	end

Route104_EventScript_H7::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_CHESTO_BERRY, Route104_EventScript_ChestoAfter
	msgbox Route104_Text_H7
	giveitem ITEM_CHESTO_BERRY
	goto_if_eq VAR_RESULT, FALSE, Route104_EventScript_ChestoBagFull
	setflag FLAG_HOENN_GOT_CHESTO_BERRY
Route104_EventScript_ChestoAfter::
	msgbox Route104_Text_ChestoAfter
	release
	end

Route104_EventScript_ChestoBagFull::
	msgbox Route104_Text_ChestoBagFull
	release
	end

@ Always out, not only after three BADGES as in Emerald (user decision
@ 2026-09-27, dialogue doc Q1 (a))
Route104_EventScript_WhiteHerbFlorist::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_WHITE_HERB, Route104_EventScript_WhiteHerbAfter
	msgbox Route104_Text_WhiteHerbOffer
	giveitem ITEM_WHITE_HERB
	goto_if_eq VAR_RESULT, FALSE, Route104_EventScript_WhiteHerbBagFull
	setflag FLAG_HOENN_GOT_WHITE_HERB
Route104_EventScript_WhiteHerbAfter::
	msgbox Route104_Text_WhiteHerbAfter
	release
	end

Route104_EventScript_WhiteHerbBagFull::
	msgbox Route104_Text_WhiteHerbBagFull
	release
	end
