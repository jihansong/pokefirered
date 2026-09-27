LittlerootTown_BrendansHouse_1F_MapScripts::
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ v0.11.0: the boarding house (user decision 2026-09-27). MRS. WREN puts the
@ KANTO CHAMPION up; her bed upstairs heals the party.
LittlerootTown_BrendansHouse_1F_EventScript_Landlady::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_MET_LANDLADY, LittlerootTown_BrendansHouse_1F_EventScript_LandladyRepeat
	setflag FLAG_HOENN_MET_LANDLADY
	msgbox LittlerootTown_BrendansHouse_1F_Text_LandladyFirstMeet
	msgbox LittlerootTown_BrendansHouse_1F_Text_LandladyBedHint
	release
	end

@ The bed hint again only when the party needs it
LittlerootTown_BrendansHouse_1F_EventScript_LandladyRepeat::
	msgbox LittlerootTown_BrendansHouse_1F_Text_LandladyRepeat
	special IsPlayerPartyHurt
	goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
	msgbox LittlerootTown_BrendansHouse_1F_Text_LandladyBedHint
	release
	end

LittlerootTown_BrendansHouse_1F_EventScript_Pippa::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_MET_LANDLADY, LittlerootTown_BrendansHouse_1F_EventScript_PippaRepeat
	msgbox LittlerootTown_BrendansHouse_1F_Text_PippaFirstMeet
	release
	end

LittlerootTown_BrendansHouse_1F_EventScript_PippaRepeat::
	msgbox LittlerootTown_BrendansHouse_1F_Text_PippaRepeat
	release
	end
@ END PATCH
