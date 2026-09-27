@ v0.11.0: the player's room at the boarding house. The bed heals the party;
@ whiting out still returns to OLDALE's POKéMON CENTER.
LittlerootTown_BrendansHouse_2F_EventScript_Bed::
	lockall
	msgbox LittlerootTown_BrendansHouse_2F_Text_BedPrompt, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_ReleaseEnd
	closemessage
	fadescreen FADE_TO_BLACK
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	fadescreen FADE_FROM_BLACK
	msgbox LittlerootTown_BrendansHouse_2F_Text_BedRested
	releaseall
	end

LittlerootTown_BrendansHouse_2F_EventScript_PC::
	msgbox LittlerootTown_BrendansHouse_2F_Text_PC, MSGBOX_SIGN
	end

LittlerootTown_BrendansHouse_2F_EventScript_WallClock::
	msgbox LittlerootTown_BrendansHouse_2F_Text_WallClock, MSGBOX_SIGN
	end
