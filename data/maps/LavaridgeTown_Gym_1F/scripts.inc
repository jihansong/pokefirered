LavaridgeTown_Gym_1F_MapScripts::
map_script MAP_SCRIPT_ON_TRANSITION, LavaridgeTown_Gym_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, LavaridgeTown_Gym_1F_MountainResume
	map_script MAP_SCRIPT_ON_RETURN_TO_FIELD, LavaridgeTown_Gym_1F_MountainReturn
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
LavaridgeTown_Gym_1F_OnTransition::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

LavaridgeTown_Gym_1F_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

LavaridgeTown_Gym_1F_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

@ Z4 reward bridge: old trainer victories recover the same rewards.
LavaridgeTown_Gym_1F_EventScript_H0::
	goto_if_defeated TRAINER_HOENN_FLANNERY_1, LavaridgeTown_Gym_1F_EventScript_DefeatedFlannery
	special HoennMountain_GetPhase
	goto_if_ge VAR_RESULT, 2, LavaridgeTown_Gym_1F_Mountain_BattleReady
	lock
	faceplayer
	msgbox LavaridgeTown_Gym_1F_Mountain_TextWait
	release
	end

LavaridgeTown_Gym_1F_Mountain_BattleReady::
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
