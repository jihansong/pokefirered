DewfordTown_Gym_MapScripts::
	.byte 0

DewfordTown_Gym_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_BRAWLY_1, DewfordTown_Gym_Text_H0_0, DewfordTown_Gym_Text_H0_1
	msgbox DewfordTown_Gym_Text_H0_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_TAKAO, DewfordTown_Gym_Text_H1_0, DewfordTown_Gym_Text_H1_1
	msgbox DewfordTown_Gym_Text_H1_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_JOCELYN, DewfordTown_Gym_Text_H2_0, DewfordTown_Gym_Text_H2_1
	msgbox DewfordTown_Gym_Text_H2_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_LAURA, DewfordTown_Gym_Text_H3_0, DewfordTown_Gym_Text_H3_1
	msgbox DewfordTown_Gym_Text_H3_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H4::
	msgbox DewfordTown_Gym_Text_H4, MSGBOX_NPC
	end

DewfordTown_Gym_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_CRISTIAN, DewfordTown_Gym_Text_H5_0, DewfordTown_Gym_Text_H5_1
	msgbox DewfordTown_Gym_Text_H5_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_LILITH, DewfordTown_Gym_Text_H6_0, DewfordTown_Gym_Text_H6_1
	msgbox DewfordTown_Gym_Text_H6_2, MSGBOX_AUTOCLOSE
	end

DewfordTown_Gym_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_BRENDEN, DewfordTown_Gym_Text_H7_0, DewfordTown_Gym_Text_H7_1
	msgbox DewfordTown_Gym_Text_H7_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Event 3: BRAWLY, and HOENN's first BADGE for a champion who starts over.
@ HOENN's badges are flags of their own, so this one changes nothing in the
@ engine; the register keeper at SLATEPORT's harbour is what reads it back.
DewfordTown_Gym_EventScript_Brawly::
	trainerbattle_single TRAINER_HOENN_BRAWLY_1, DewfordTown_Gym_Text_BrawlyIntro, DewfordTown_Gym_Text_BrawlyDefeat, DewfordTown_Gym_EventScript_DefeatedBrawly, NO_MUSIC
	goto_if_unset FLAG_HOENN_GOT_TM08_FROM_BRAWLY, DewfordTown_Gym_EventScript_GiveTM08
	msgbox DewfordTown_Gym_Text_BrawlyPostBattle
	call DewfordTown_Gym_EventScript_BrawlyPikachu
	release
	end

DewfordTown_Gym_EventScript_DefeatedBrawly::
	setflag FLAG_HOENN_BADGE02_GET
	goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 3, DewfordTown_Gym_EventScript_GiveTM08
	setvar VAR_HOENN_STAGE1_PROGRESS, 3
	goto DewfordTown_Gym_EventScript_GiveTM08
	end

DewfordTown_Gym_EventScript_GiveTM08::
	msgbox DewfordTown_Gym_Text_TakeThisTM
	checkitemspace ITEM_TM08
	goto_if_eq VAR_RESULT, FALSE, DewfordTown_Gym_EventScript_NoRoomForTM08
	giveitem_msg DewfordTown_Gym_Text_ReceivedTM08, ITEM_TM08
	setflag FLAG_HOENN_GOT_TM08_FROM_BRAWLY
	msgbox DewfordTown_Gym_Text_ExplainTM08
	call DewfordTown_Gym_EventScript_BrawlyPikachu
	release
	end

DewfordTown_Gym_EventScript_NoRoomForTM08::
	msgbox DewfordTown_Gym_Text_NoRoomForTM08
	release
	end

@ Event 7: BRAWLY has never had an electric type walk into this gym
DewfordTown_Gym_EventScript_BrawlyPikachu::
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	goto_if_eq VAR_RESULT, PARTY_SIZE, EventScript_Return
	goto_if_set FLAG_HOENN_PIKACHU_GYM_SEEN, EventScript_Return
	setflag FLAG_HOENN_PIKACHU_GYM_SEEN
	msgbox DewfordTown_Gym_Text_BrawlyPikachu
	return
@ END PATCH
