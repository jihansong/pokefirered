MossdeepCity_Gym_MapScripts::
	.byte 0

MossdeepCity_Gym_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_PRESTON, MossdeepCity_Gym_Text_H1_0, MossdeepCity_Gym_Text_H1_1
	msgbox MossdeepCity_Gym_Text_H1_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_BLAKE, MossdeepCity_Gym_Text_H2_0, MossdeepCity_Gym_Text_H2_1
	msgbox MossdeepCity_Gym_Text_H2_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_MAURA, MossdeepCity_Gym_Text_H3_0, MossdeepCity_Gym_Text_H3_1
	msgbox MossdeepCity_Gym_Text_H3_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_SAMANTHA, MossdeepCity_Gym_Text_H4_0, MossdeepCity_Gym_Text_H4_1
	msgbox MossdeepCity_Gym_Text_H4_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_VIRGIL, MossdeepCity_Gym_Text_H5_0, MossdeepCity_Gym_Text_H5_1
	msgbox MossdeepCity_Gym_Text_H5_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_HANNAH, MossdeepCity_Gym_Text_H6_0, MossdeepCity_Gym_Text_H6_1
	msgbox MossdeepCity_Gym_Text_H6_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H7::
	msgbox MossdeepCity_Gym_Text_H7, MSGBOX_NPC
	end

MossdeepCity_Gym_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_NATE, MossdeepCity_Gym_Text_H9_0, MossdeepCity_Gym_Text_H9_1
	msgbox MossdeepCity_Gym_Text_H9_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_SYLVIA, MossdeepCity_Gym_Text_H10_0, MossdeepCity_Gym_Text_H10_1
	msgbox MossdeepCity_Gym_Text_H10_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H11::
	trainerbattle_single TRAINER_HOENN_CLIFFORD, MossdeepCity_Gym_Text_H11_0, MossdeepCity_Gym_Text_H11_1
	msgbox MossdeepCity_Gym_Text_H11_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H12::
	trainerbattle_single TRAINER_HOENN_MACEY, MossdeepCity_Gym_Text_H12_0, MossdeepCity_Gym_Text_H12_1
	msgbox MossdeepCity_Gym_Text_H12_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H13::
	trainerbattle_single TRAINER_HOENN_KATHLEEN, MossdeepCity_Gym_Text_H13_0, MossdeepCity_Gym_Text_H13_1
	msgbox MossdeepCity_Gym_Text_H13_2, MSGBOX_AUTOCLOSE
	end

MossdeepCity_Gym_EventScript_H14::
	trainerbattle_single TRAINER_HOENN_NICHOLAS, MossdeepCity_Gym_Text_H14_0, MossdeepCity_Gym_Text_H14_1
	msgbox MossdeepCity_Gym_Text_H14_2, MSGBOX_AUTOCLOSE
	end

@ BEGIN PATCH (tools/hoenn_import/patches)


@ THYL_LEAGUE_V1
MossdeepCity_Gym_EventScript_H0::
	goto MossdeepCity_Gym_TY_Boss

MossdeepCity_Gym_EventScript_H8::
	goto MossdeepCity_Gym_TY_Boss

MossdeepCity_Gym_TY_Boss::
	goto_if_defeated TRAINER_HOENN_TATE_AND_LIZA_1, MossdeepCity_Gym_TY_Reward
	trainerbattle_double TRAINER_HOENN_TATE_AND_LIZA_1, MossdeepCity_Gym_Text_H0_0, MossdeepCity_Gym_Text_H0_1, MossdeepCity_Gym_TY_TooFew, MossdeepCity_Gym_TY_Reward
	goto MossdeepCity_Gym_TY_Reward

MossdeepCity_Gym_TY_Reward::
	lock
	faceplayer
	goto_if_not_defeated TRAINER_HOENN_TATE_AND_LIZA_1, MossdeepCity_Gym_TY_Done
	setflag FLAG_HOENN_BADGE07_GET
	goto_if_set FLAG_HOENN_GOT_TM04, MossdeepCity_Gym_TY_Post
	msgbox MossdeepCity_Gym_TY_Badge
	checkitemspace ITEM_TM04
	goto_if_eq VAR_RESULT, FALSE, MossdeepCity_Gym_TY_Full
	giveitem ITEM_TM04
	goto_if_eq VAR_RESULT, FALSE, MossdeepCity_Gym_TY_Full
	setflag FLAG_HOENN_GOT_TM04
MossdeepCity_Gym_TY_Post::
	msgbox MossdeepCity_Gym_Text_H0_2
MossdeepCity_Gym_TY_Done::
	release
	end

MossdeepCity_Gym_TY_Full::
	msgbox MossdeepCity_Gym_TY_BagFull
	release
	end
@ END PATCH
