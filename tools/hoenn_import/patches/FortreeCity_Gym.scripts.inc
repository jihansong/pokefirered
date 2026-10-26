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
