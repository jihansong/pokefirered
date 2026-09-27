LittlerootTown_MaysHouse_1F_MapScripts::
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ v0.11.0: PROF. BIRCH's family house (user decision 2026-09-27); his wife,
@ the rival's mother
LittlerootTown_MaysHouse_1F_EventScript_Mom::
	lock
	faceplayer
	goto_if_eq VAR_HOENN_SCENE_BIRCH, 0, LittlerootTown_MaysHouse_1F_EventScript_MomBeforeRescue
	goto_if_ge VAR_HOENN_SCENE_BIRCH, 3, LittlerootTown_MaysHouse_1F_EventScript_MomAfterRival
	msgbox LittlerootTown_MaysHouse_1F_Text_MomThanks
	release
	end

LittlerootTown_MaysHouse_1F_EventScript_MomBeforeRescue::
	msgbox LittlerootTown_MaysHouse_1F_Text_MomBeforeRescue
	release
	end

LittlerootTown_MaysHouse_1F_EventScript_MomAfterRival::
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, LittlerootTown_MaysHouse_1F_EventScript_MomAfterRivalBrendan
	msgbox LittlerootTown_MaysHouse_1F_Text_MomAfterRivalMay
	release
	end

LittlerootTown_MaysHouse_1F_EventScript_MomAfterRivalBrendan::
	msgbox LittlerootTown_MaysHouse_1F_Text_MomAfterRivalBrendan
	release
	end
@ END PATCH
