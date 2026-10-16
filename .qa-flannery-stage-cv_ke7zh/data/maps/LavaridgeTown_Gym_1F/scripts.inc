LavaridgeTown_Gym_1F_MapScripts::
	.byte 0

LavaridgeTown_Gym_1F_EventScript_H1::
	msgbox LavaridgeTown_Gym_1F_Text_H1, MSGBOX_NPC
	end

LavaridgeTown_Gym_1F_EventScript_H2::
	msgbox LavaridgeTown_Gym_1F_Text_H2, MSGBOX_NPC
	end

LavaridgeTown_Gym_1F_EventScript_H3::
	msgbox LavaridgeTown_Gym_1F_Text_H3, MSGBOX_NPC
	end

LavaridgeTown_Gym_1F_EventScript_H4::
	msgbox LavaridgeTown_Gym_1F_Text_H4, MSGBOX_NPC
	end

LavaridgeTown_Gym_1F_EventScript_H5::
	msgbox LavaridgeTown_Gym_1F_Text_H5, MSGBOX_NPC
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Z4 reward bridge: old trainer victories recover the same rewards.
LavaridgeTown_Gym_1F_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_FLANNERY_1, LavaridgeTown_Gym_1F_Text_H0_0, LavaridgeTown_Gym_1F_Text_H0_1, LavaridgeTown_Gym_1F_EventScript_DefeatedFlannery, NO_MUSIC
	goto LavaridgeTown_Gym_1F_EventScript_DefeatedFlannery
	end

LavaridgeTown_Gym_1F_EventScript_DefeatedFlannery::
	goto_if_set FLAG_HOENN_BADGE04_GET, LavaridgeTown_Gym_1F_EventScript_CheckTM50
	setflag FLAG_HOENN_BADGE04_GET
	msgbox LavaridgeTown_Gym_1F_Text_ReceivedHeatBadge

LavaridgeTown_Gym_1F_EventScript_CheckTM50::
	goto_if_set FLAG_HOENN_GOT_TM50_FROM_FLANNERY, LavaridgeTown_Gym_1F_EventScript_PostBattle
	msgbox LavaridgeTown_Gym_1F_Text_TakeTM50
	additem ITEM_TM50
	goto_if_eq VAR_RESULT, FALSE, LavaridgeTown_Gym_1F_EventScript_NoRoomForTM50
	setflag FLAG_HOENN_GOT_TM50_FROM_FLANNERY
	msgreceiveditem LavaridgeTown_Gym_1F_Text_ReceivedTM50, ITEM_TM50
	msgbox LavaridgeTown_Gym_1F_Text_ExplainTM50
	release
	end

LavaridgeTown_Gym_1F_EventScript_NoRoomForTM50::
	msgbox LavaridgeTown_Gym_1F_Text_NoRoomForTM50
	release
	end

LavaridgeTown_Gym_1F_EventScript_PostBattle::
	msgbox LavaridgeTown_Gym_1F_Text_H0_2
	release
	end
@ END PATCH
