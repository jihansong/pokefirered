SootopolisCity_Gym_1F_MapScripts::
	.byte 0

SootopolisCity_Gym_1F_EventScript_H1::
	msgbox SootopolisCity_Gym_1F_Text_H1, MSGBOX_NPC
	end

@ BEGIN PATCH (tools/hoenn_import/patches)


@ THYL_LEAGUE_V1
SootopolisCity_Gym_1F_EventScript_H0::
	goto SootopolisCity_Gym_1F_TY_Boss

SootopolisCity_Gym_1F_TY_Boss::
	goto_if_defeated TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_TY_Reward
	trainerbattle_single TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_Text_H0_0, SootopolisCity_Gym_1F_Text_H0_1, SootopolisCity_Gym_1F_TY_Reward
	goto SootopolisCity_Gym_1F_TY_Reward

SootopolisCity_Gym_1F_TY_Reward::
	lock
	faceplayer
	goto_if_not_defeated TRAINER_HOENN_JUAN_1, SootopolisCity_Gym_1F_TY_Done
	setflag FLAG_HOENN_BADGE08_GET
	goto_if_set FLAG_HOENN_GOT_TM03, SootopolisCity_Gym_1F_TY_Post
	msgbox SootopolisCity_Gym_1F_TY_Badge
	checkitemspace ITEM_TM03
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_Gym_1F_TY_Full
	giveitem ITEM_TM03
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_Gym_1F_TY_Full
	setflag FLAG_HOENN_GOT_TM03
SootopolisCity_Gym_1F_TY_Post::
	msgbox SootopolisCity_Gym_1F_Text_H0_2
SootopolisCity_Gym_1F_TY_Done::
	release
	end

SootopolisCity_Gym_1F_TY_Full::
	msgbox SootopolisCity_Gym_1F_TY_BagFull
	release
	end
@ END PATCH
