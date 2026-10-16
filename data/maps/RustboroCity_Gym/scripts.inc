RustboroCity_Gym_MapScripts::
	.byte 0

RustboroCity_Gym_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_JOSH, RustboroCity_Gym_Text_H1_0, RustboroCity_Gym_Text_H1_1
	msgbox RustboroCity_Gym_Text_H1_2, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_TOMMY, RustboroCity_Gym_Text_H2_0, RustboroCity_Gym_Text_H2_1
	msgbox RustboroCity_Gym_Text_H2_2, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_H3::
	msgbox RustboroCity_Gym_Text_H3, MSGBOX_NPC
	end

RustboroCity_Gym_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_MARC, RustboroCity_Gym_Text_H4_0, RustboroCity_Gym_Text_H4_1
	msgbox RustboroCity_Gym_Text_H4_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ The battle flag may already be set by a pre-Z3 save. Re-enter the reward
@ path on conversation as well as victory, without starting a rematch.
RustboroCity_Gym_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_ROXANNE_1, RustboroCity_Gym_Text_H0_0, RustboroCity_Gym_Text_H0_1, RustboroCity_Gym_EventScript_DefeatedRoxanne, NO_MUSIC
	goto RustboroCity_Gym_EventScript_DefeatedRoxanne
	end

RustboroCity_Gym_EventScript_DefeatedRoxanne::
	setflag FLAG_HOENN_DEFEATED_RUSTBORO_GYM
	goto_if_set FLAG_HOENN_BADGE01_GET, RustboroCity_Gym_EventScript_CheckTM39
	setflag FLAG_HOENN_BADGE01_GET
	msgbox RustboroCity_Gym_Text_ReceivedStoneBadge

RustboroCity_Gym_EventScript_CheckTM39::
	goto_if_set FLAG_HOENN_GOT_TM39_FROM_ROXANNE, RustboroCity_Gym_EventScript_PostBattle
	msgbox RustboroCity_Gym_Text_TakeTM39
	additem ITEM_TM39
	goto_if_eq VAR_RESULT, FALSE, RustboroCity_Gym_EventScript_NoRoomForTM39
	msgreceiveditem RustboroCity_Gym_Text_ReceivedTM39, ITEM_TM39
	setflag FLAG_HOENN_GOT_TM39_FROM_ROXANNE
	msgbox RustboroCity_Gym_Text_ExplainTM39
	call RustboroCity_Gym_EventScript_Pikachu
	release
	end

RustboroCity_Gym_EventScript_NoRoomForTM39::
	msgbox RustboroCity_Gym_Text_NoRoomForTM39
	release
	end

RustboroCity_Gym_EventScript_PostBattle::
	msgbox RustboroCity_Gym_Text_H0_2
	call RustboroCity_Gym_EventScript_Pikachu
	release
	end

@ The approved revision keeps the PIKACHU remark after the battle.
RustboroCity_Gym_EventScript_Pikachu::
	goto_if_set FLAG_HOENN_PIKACHU_ROXANNE_SEEN, EventScript_Return
	setvar VAR_0x8004, SPECIES_PIKACHU
	specialvar VAR_RESULT, PartyHasSpecies
	goto_if_eq VAR_RESULT, FALSE, EventScript_Return
	msgbox RustboroCity_Gym_Text_Pikachu
	setflag FLAG_HOENN_PIKACHU_ROXANNE_SEEN
	return
@ END PATCH
