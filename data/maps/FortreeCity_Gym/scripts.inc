FortreeCity_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FortreeCity_Gym_RotatingGate_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, FortreeCity_Gym_RotatingGate_OnResume
	.byte 0

FortreeCity_Gym_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_JARED, FortreeCity_Gym_Text_H1_0, FortreeCity_Gym_Text_H1_1
	msgbox FortreeCity_Gym_Text_H1_2, MSGBOX_AUTOCLOSE
	end

FortreeCity_Gym_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_FLINT, FortreeCity_Gym_Text_H2_0, FortreeCity_Gym_Text_H2_1
	msgbox FortreeCity_Gym_Text_H2_2, MSGBOX_AUTOCLOSE
	end

FortreeCity_Gym_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_ASHLEY, FortreeCity_Gym_Text_H3_0, FortreeCity_Gym_Text_H3_1
	msgbox FortreeCity_Gym_Text_H3_2, MSGBOX_AUTOCLOSE
	end

FortreeCity_Gym_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_EDWARDO, FortreeCity_Gym_Text_H4_0, FortreeCity_Gym_Text_H4_1
	msgbox FortreeCity_Gym_Text_H4_2, MSGBOX_AUTOCLOSE
	end

FortreeCity_Gym_EventScript_H5::
	msgbox FortreeCity_Gym_Text_H5, MSGBOX_NPC
	end

FortreeCity_Gym_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_HUMBERTO, FortreeCity_Gym_Text_H6_0, FortreeCity_Gym_Text_H6_1
	msgbox FortreeCity_Gym_Text_H6_2, MSGBOX_AUTOCLOSE
	end

FortreeCity_Gym_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_DARIUS, FortreeCity_Gym_Text_H7_0, FortreeCity_Gym_Text_H7_1
	msgbox FortreeCity_Gym_Text_H7_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Z5 reward bridge: a pre-Z5 save may already record WINONA's defeat.
@ The post-battle fallthrough and the new-victory callback use the same path.
@ Owning TM40 does not record whether WINONA gave it.
FortreeCity_Gym_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_WINONA_1, FortreeCity_Gym_Text_H0_0, FortreeCity_Gym_Text_H0_1, FortreeCity_Gym_EventScript_DefeatedWinona, NO_MUSIC
	goto FortreeCity_Gym_EventScript_DefeatedWinona
	end

FortreeCity_Gym_EventScript_DefeatedWinona::
	goto_if_set FLAG_HOENN_BADGE06_GET, FortreeCity_Gym_EventScript_CheckTM40
	setflag FLAG_HOENN_BADGE06_GET
	msgbox FortreeCity_Gym_Text_ReceivedFeatherBadge

FortreeCity_Gym_EventScript_CheckTM40::
	goto_if_set FLAG_HOENN_GOT_TM40_FROM_WINONA, FortreeCity_Gym_EventScript_PostBattle
	msgbox FortreeCity_Gym_Text_TakeTM40
	additem ITEM_TM40
	goto_if_eq VAR_RESULT, FALSE, FortreeCity_Gym_EventScript_NoRoomForTM40
	@ Commit the receipt only after the item was successfully added.
	setflag FLAG_HOENN_GOT_TM40_FROM_WINONA
	msgreceiveditem FortreeCity_Gym_Text_ReceivedTM40, ITEM_TM40
	msgbox FortreeCity_Gym_Text_ExplainTM40
	release
	end

FortreeCity_Gym_EventScript_NoRoomForTM40::
	msgbox FortreeCity_Gym_Text_NoRoomForTM40
	release
	end

FortreeCity_Gym_EventScript_PostBattle::
	msgbox FortreeCity_Gym_Text_H0_2
	release
	end

FortreeCity_Gym_RotatingGate_OnTransition::
    special RotatingGate_InitPuzzle
    end

FortreeCity_Gym_RotatingGate_OnResume::
    special RotatingGate_InitPuzzleAndGraphics
    end
@ END PATCH
