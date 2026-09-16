HiddenGrotto_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, HiddenGrotto_OnTransition
	.byte 0

@ BW2's Hidden Grottoes: a narrow gap in the trees leads to a small clearing
@ holding a POKéMON or an item, which returns over time (5% per 256 steps).
@ The clearing map is shared; VAR_HIDDEN_GROTTO_ID says which grotto it is.
HiddenGrotto_OnTransition::
	special PrepareHiddenGrotto
	end

HiddenGrotto_EventScript_EnterViridianForest::
	setvar VAR_0x8008, 1
	setdynamicwarp MAP_VIRIDIAN_FOREST, 1, 8
	goto HiddenGrotto_EventScript_TryEnter
	end

HiddenGrotto_EventScript_EnterRoute11::
	setvar VAR_0x8008, 2
	setdynamicwarp MAP_ROUTE11, 30, 2
	goto HiddenGrotto_EventScript_TryEnter
	end

HiddenGrotto_EventScript_EnterRoute13::
	setvar VAR_0x8008, 3
	setdynamicwarp MAP_ROUTE13, 8, 5
	goto HiddenGrotto_EventScript_TryEnter
	end

HiddenGrotto_EventScript_EnterRoute15::
	setvar VAR_0x8008, 4
	setdynamicwarp MAP_ROUTE15, 6, 7
	goto HiddenGrotto_EventScript_TryEnter
	end

HiddenGrotto_EventScript_TryEnter::
	lockall
	msgbox HiddenGrotto_Text_NarrowPathBetweenTrees, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, HiddenGrotto_EventScript_DontEnter
	copyvar VAR_HIDDEN_GROTTO_ID, VAR_0x8008
	closemessage
	warp MAP_HIDDEN_GROTTO, 7, 9
	waitstate
	releaseall
	end

HiddenGrotto_EventScript_DontEnter::
	releaseall
	end

HiddenGrotto_EventScript_Exit::
	lockall
	setvar VAR_TEMP_1, 1
	special LeaveHiddenGrotto
	waitstate
	releaseall
	end

HiddenGrotto_EventScript_Pokemon::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	special CreateHiddenGrottoWildMon
	goto_if_eq VAR_0x8004, SPECIES_NONE, EventScript_ReleaseEnd
	msgbox HiddenGrotto_Text_SomethingJumpedOut
	waitse
	playmoncry VAR_0x8004, CRY_MODE_ENCOUNTER
	waitmoncry
	special ClearHiddenGrotto
	dowildbattle
	setflag FLAG_HIDE_HIDDEN_GROTTO_POKEMON
	removeobject LOCALID_HIDDEN_GROTTO_POKEMON
	release
	end

HiddenGrotto_EventScript_Item::
	lock
	special GetHiddenGrottoItem
	goto_if_eq VAR_0x8004, ITEM_NONE, EventScript_ReleaseEnd
	giveitem VAR_0x8004
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	special ClearHiddenGrotto
	setflag FLAG_HIDE_HIDDEN_GROTTO_ITEM
	removeobject LOCALID_HIDDEN_GROTTO_ITEM
	release
	end
