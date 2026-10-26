LavaridgeTown_EventScript_H6::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_LAVARIDGE_WYNAUT_EGG, LavaridgeTown_EventScript_H6_Received
	msgbox LavaridgeTown_Text_H6, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, LavaridgeTown_EventScript_H6_Declined
	giveegg SPECIES_WYNAUT
	goto_if_eq VAR_RESULT, 2, LavaridgeTown_EventScript_H6_NoRoom
	copyvar VAR_0x8006, VAR_RESULT
	setflag FLAG_HOENN_GOT_LAVARIDGE_WYNAUT_EGG
	playfanfare MUS_OBTAIN_ITEM
	message LavaridgeTown_Text_H6EggReceived
	waitmessage
	waitfanfare
	call_if_eq VAR_0x8006, 1, LavaridgeTown_EventScript_H6_SentToPC
LavaridgeTown_EventScript_H6_Received::
	msgbox LavaridgeTown_Text_H6TakeCare, MSGBOX_DEFAULT
	release
	end

LavaridgeTown_EventScript_H6_SentToPC::
	msgbox LavaridgeTown_Text_H6SentToPC, MSGBOX_DEFAULT
	return

LavaridgeTown_EventScript_H6_Declined::
	msgbox LavaridgeTown_Text_H6Declined, MSGBOX_DEFAULT
	release
	end

LavaridgeTown_EventScript_H6_NoRoom::
	msgbox LavaridgeTown_Text_H6NoRoom, MSGBOX_DEFAULT
	release
	end
