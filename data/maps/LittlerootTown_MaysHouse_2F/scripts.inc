LittlerootTown_MaysHouse_2F_MapScripts::
	.byte 0

LittlerootTown_MaysHouse_2F_EventScript_H0::
	msgbox LittlerootTown_MaysHouse_2F_Text_H0, MSGBOX_SIGN
	end

LittlerootTown_MaysHouse_2F_EventScript_H1::
	msgbox LittlerootTown_MaysHouse_2F_Text_H1, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
LittlerootTown_MaysHouse_2F_EventScript_PC::
	msgbox LittlerootTown_MaysHouse_2F_Text_PC, MSGBOX_SIGN
	end

LittlerootTown_MaysHouse_2F_EventScript_WallClock::
	msgbox LittlerootTown_MaysHouse_2F_Text_WallClock, MSGBOX_SIGN
	end
@ END PATCH
