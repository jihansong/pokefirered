MtPyre_1F_EventScript_H0::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_MT_PYRE_CLEANSE_TAG, MtPyre_1F_EventScript_H0_Received
	msgbox MtPyre_1F_Text_H0, MSGBOX_DEFAULT
	giveitem ITEM_CLEANSE_TAG, 1
	goto_if_eq VAR_RESULT, FALSE, MtPyre_1F_EventScript_H0_NoRoom
	setflag FLAG_HOENN_GOT_MT_PYRE_CLEANSE_TAG
MtPyre_1F_EventScript_H0_Received::
	msgbox MtPyre_1F_Text_H0CleanseTag, MSGBOX_DEFAULT
	release
	end

MtPyre_1F_EventScript_H0_NoRoom::
	msgbox MtPyre_1F_Text_H0NoRoom, MSGBOX_DEFAULT
	release
	end
