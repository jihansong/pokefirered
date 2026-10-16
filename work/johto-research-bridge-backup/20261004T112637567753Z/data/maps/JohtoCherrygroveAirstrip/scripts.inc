JohtoCherrygroveAirstrip_MapScripts::
	.byte 0

JohtoCherrygroveAirstrip_ReturnClerk::
	lock
	faceplayer
	msgbox JohtoCherrygroveAirstrip_Text_Return, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, JohtoCherrygroveAirstrip_Cancel
	closemessage
	setvar VAR_0x8004, AIRPLANE_DEST_KANTO
	goto EventScript_TakeAirplane
	end

JohtoCherrygroveAirstrip_Cancel::
	msgbox JohtoCherrygroveAirstrip_Text_Cancel
	release
	end

JohtoCherrygroveAirstrip_Guide::
	msgbox JohtoCherrygroveAirstrip_Text_Guide, MSGBOX_NPC
	end

JohtoCherrygroveAirstrip_Sign::
	msgbox JohtoCherrygroveAirstrip_Text_Sign, MSGBOX_NPC
	end

