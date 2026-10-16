NewBarkTown_RestHouse_MapScripts::
	.byte 0

NewBarkTown_RestHouse_Host::
	lock
	faceplayer
	msgbox NewBarkTown_RestHouse_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, NewBarkTown_RestHouse_Cancel
	closemessage
	fadescreen FADE_TO_BLACK
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	fadescreen FADE_FROM_BLACK
	msgbox NewBarkTown_RestHouse_Text_Done
	release
	end

NewBarkTown_RestHouse_Cancel::
	msgbox NewBarkTown_RestHouse_Text_Cancel
	release
	end
