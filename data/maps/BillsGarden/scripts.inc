BillsGarden_MapScripts::
	.byte 0

@ Once the player has caught 100 POKéMON, Bill opens the back door of the Sea
@ Cottage onto a garden of POKéMON from Johto and Hoenn. Each one can be taken
@ along once, one per game clock day (VAR_BILLS_GARDEN_STEPS, VAR_BILLS_GARDEN_LAST_DAY).
BillsGarden_EventScript_BillCheckGarden::
	goto_if_set FLAG_OPENED_BILLS_GARDEN, BillsGarden_EventScript_BillEnjoyGarden
	setvar VAR_0x8004, 1
	special GetPokedexCount
	goto_if_lt VAR_0x8006, 100, Route25_SeaCottage_EventScript_BillGoLookAtPC
	msgbox BillsGarden_Text_BillSecretGarden
	setflag FLAG_OPENED_BILLS_GARDEN
	setvar VAR_BILLS_GARDEN_STEPS, 1500
	release
	end

BillsGarden_EventScript_BillEnjoyGarden::
	msgbox BillsGarden_Text_BillEnjoyGarden
	release
	end

BillsGarden_EventScript_BackDoor::
	lockall
	goto_if_unset FLAG_OPENED_BILLS_GARDEN, BillsGarden_EventScript_BackDoorLocked
	msgbox BillsGarden_Text_GoOutToGarden, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_ReleaseEnd
	closemessage
	playse SE_EXIT
	warp MAP_BILLS_GARDEN, 7, 11
	waitstate
	releaseall
	end

BillsGarden_EventScript_BackDoorLocked::
	msgbox BillsGarden_Text_BackDoorLocked
	releaseall
	end

BillsGarden_EventScript_Exit::
	lockall
	playse SE_EXIT
	warp MAP_ROUTE25_SEA_COTTAGE, 13, 2
	waitstate
	releaseall
	end

BillsGarden_EventScript_Pichu::
	lock
	faceplayer
	setvar VAR_0x8004, SPECIES_PICHU
	call BillsGarden_EventScript_TryTakeMon
	goto_if_ne VAR_0x8008, TRUE, EventScript_ReleaseEnd
	setflag FLAG_HIDE_BILLS_GARDEN_PICHU
	removeobject LOCALID_BILLS_GARDEN_PICHU
	release
	end

BillsGarden_EventScript_Togepi::
	lock
	faceplayer
	setvar VAR_0x8004, SPECIES_TOGEPI
	call BillsGarden_EventScript_TryTakeMon
	goto_if_ne VAR_0x8008, TRUE, EventScript_ReleaseEnd
	setflag FLAG_HIDE_BILLS_GARDEN_TOGEPI
	removeobject LOCALID_BILLS_GARDEN_TOGEPI
	release
	end

BillsGarden_EventScript_Marill::
	lock
	faceplayer
	setvar VAR_0x8004, SPECIES_MARILL
	call BillsGarden_EventScript_TryTakeMon
	goto_if_ne VAR_0x8008, TRUE, EventScript_ReleaseEnd
	setflag FLAG_HIDE_BILLS_GARDEN_MARILL
	removeobject LOCALID_BILLS_GARDEN_MARILL
	release
	end

BillsGarden_EventScript_Plusle::
	lock
	faceplayer
	setvar VAR_0x8004, SPECIES_PLUSLE
	call BillsGarden_EventScript_TryTakeMon
	goto_if_ne VAR_0x8008, TRUE, EventScript_ReleaseEnd
	setflag FLAG_HIDE_BILLS_GARDEN_PLUSLE
	removeobject LOCALID_BILLS_GARDEN_PLUSLE
	release
	end

BillsGarden_EventScript_Minun::
	lock
	faceplayer
	setvar VAR_0x8004, SPECIES_MINUN
	call BillsGarden_EventScript_TryTakeMon
	goto_if_ne VAR_0x8008, TRUE, EventScript_ReleaseEnd
	setflag FLAG_HIDE_BILLS_GARDEN_MINUN
	removeobject LOCALID_BILLS_GARDEN_MINUN
	release
	end

@ VAR_0x8004: species. Sets VAR_0x8008 to TRUE if the POKéMON was taken.
BillsGarden_EventScript_TryTakeMon::
	setvar VAR_0x8008, FALSE
	call BillsGarden_EventScript_OfferMon
	setvar VAR_TEMP_1, 0
	return

BillsGarden_EventScript_OfferMon::
	copyvar VAR_TEMP_1, VAR_0x8004
	bufferspeciesname STR_VAR_1, VAR_0x8004
	playmoncry VAR_0x8004, CRY_MODE_NORMAL
	waitmoncry
	goto_if_lt VAR_BILLS_GARDEN_STEPS, 1500, BillsGarden_EventScript_NotToday
	msgbox BillsGarden_Text_WantsToComeAlong, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, BillsGarden_EventScript_LeaveMon
	givemon VAR_TEMP_1, 5
	goto_if_eq VAR_RESULT, 2, BillsGarden_EventScript_NoRoom
	copyvar VAR_0x8009, VAR_RESULT
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message BillsGarden_Text_TookMonAlong
	waitmessage
	waitfanfare
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_0x8009, 1, BillsGarden_EventScript_TookMonToPC
	goto_if_eq VAR_RESULT, NO, BillsGarden_EventScript_TookMon
	call EventScript_GetGiftMonPartySlot
	call EventScript_ChangePokemonNickname
	goto BillsGarden_EventScript_TookMon

BillsGarden_EventScript_TookMonToPC::
	call_if_eq VAR_RESULT, YES, EventScript_NameReceivedBoxMon
	call EventScript_TransferredToPC
BillsGarden_EventScript_TookMon::
	special SetBillsGardenTakenToday
	setvar VAR_0x8008, TRUE
	return

BillsGarden_EventScript_NotToday::
	msgbox BillsGarden_Text_PlayingHappily
	return

BillsGarden_EventScript_LeaveMon::
	msgbox BillsGarden_Text_WentBackToPlaying
	return

BillsGarden_EventScript_NoRoom::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_NoMoreRoomForPokemon
	return
