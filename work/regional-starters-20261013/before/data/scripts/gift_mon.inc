@ Gives VAR_TEMP_1 (species) at the level in the label's name, with the usual
@ fanfare, nickname offer and PC message. Sets VAR_RESULT to TRUE, or FALSE if
@ there was no room.
EventScript_GiveGiftMonLv5::
	givemon VAR_TEMP_1, 5
	goto EventScript_GiftMonGiven

EventScript_GiveGiftMonLv25::
	givemon VAR_TEMP_1, 25
EventScript_GiftMonGiven::
	goto_if_eq VAR_RESULT, 2, EventScript_GiftMonNoRoom
	copyvar VAR_0x8006, VAR_RESULT
	bufferspeciesname STR_VAR_1, VAR_TEMP_1
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message Text_PlayerReceivedGiftMon
	waitmessage
	waitfanfare
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_GiftMonNamed
	goto_if_eq VAR_0x8006, 1, EventScript_GiftMonNameBoxMon
	call EventScript_GetGiftMonPartySlot
	call EventScript_ChangePokemonNickname
	goto EventScript_GiftMonNamed

EventScript_GiftMonNameBoxMon::
	call EventScript_NameReceivedBoxMon
EventScript_GiftMonNamed::
	call_if_eq VAR_0x8006, 1, EventScript_TransferredToPC
	setvar VAR_RESULT, TRUE
	return

EventScript_GiftMonNoRoom::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_NoMoreRoomForPokemon
	setvar VAR_RESULT, FALSE
	return

Text_PlayerReceivedGiftMon::
    .string "{PLAYER} received the {STR_VAR_1}!$"
