Route114_FossilManiacsHouse_MapScripts::
	.byte 0

Route114_FossilManiacsHouse_EventScript_H1::
	msgbox Route114_FossilManiacsHouse_Text_H1, MSGBOX_SIGN
	end

Route114_FossilManiacsHouse_EventScript_H2::
	msgbox Route114_FossilManiacsHouse_Text_H2, MSGBOX_SIGN
	end

Route114_FossilManiacsHouse_EventScript_H3::
	msgbox Route114_FossilManiacsHouse_Text_H3, MSGBOX_SIGN
	end

Route114_FossilManiacsHouse_EventScript_H4::
	msgbox Route114_FossilManiacsHouse_Text_H4, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
Route114_FossilManiacsHouse_EventScript_H0::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_TM28_FROM_FOSSIL_MANIAC, Route114_FossilManiacsHouse_EventScript_H0_Received
	msgbox Route114_FossilManiacsHouse_Text_H0, MSGBOX_DEFAULT
	giveitem ITEM_TM28, 1
	goto_if_eq VAR_RESULT, FALSE, Route114_FossilManiacsHouse_EventScript_H0_NoRoom
	setflag FLAG_HOENN_GOT_TM28_FROM_FOSSIL_MANIAC
Route114_FossilManiacsHouse_EventScript_H0_Received::
	msgbox Route114_FossilManiacsHouse_Text_H0Dig, MSGBOX_DEFAULT
	release
	end

Route114_FossilManiacsHouse_EventScript_H0_NoRoom::
	msgbox Route114_FossilManiacsHouse_Text_H0NoRoom, MSGBOX_DEFAULT
	release
	end
@ END PATCH
