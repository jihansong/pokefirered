

@ Keep two decorative statues clear of the routes to the upper and final warps.
@ Local IDs, objects, trainers and warp definitions retain their original order.
MossdeepCity_Gym_TY_OnLoad::
	call MossdeepCity_Gym_TY_SetPassageStatueTemplates
	end

MossdeepCity_Gym_TY_OnResume::
	call MossdeepCity_Gym_TY_SetPassageStatueTemplates
	setobjectxy 21, 12, 6
	setobjectxy 24, 11, 33
	end

MossdeepCity_Gym_TY_SetPassageStatueTemplates::
	setobjectxyperm 21, 12, 6
	setobjectxyperm 24, 11, 33
	return

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
