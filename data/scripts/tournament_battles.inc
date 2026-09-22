@ The INDIGO PLATEAU tournament's matches (tools/make_tournament.py).
@ Tournament_SetUpMatch puts the entrant's index in VAR_0x8008 and their name in
@ STR_VAR_2, then this switch runs that entrant's battle.

EventScript_TourneyBattle::
	switch VAR_0x8008
	case 0, EventScript_TourneyBattleBrock
	case 1, EventScript_TourneyBattleMisty
	case 2, EventScript_TourneyBattleLtsurge
	case 3, EventScript_TourneyBattleErika
	case 4, EventScript_TourneyBattleKoga
	case 5, EventScript_TourneyBattleSabrina
	case 6, EventScript_TourneyBattleBlaine
	case 7, EventScript_TourneyBattleGiovanni
	case 8, EventScript_TourneyBattleLorelei
	case 9, EventScript_TourneyBattleBruno
	case 10, EventScript_TourneyBattleAgatha
	case 11, EventScript_TourneyBattleLance
	case 12, EventScript_TourneyBattleBlue
	case 13, EventScript_TourneyBattleOak
	case 14, EventScript_TourneyBattleN
	case 15, EventScript_TourneyBattleJessieJames
	end

EventScript_TourneyBattleBrock::
	cleartrainerflag TRAINER_TOURNEY_BROCK
	trainerbattle_no_intro TRAINER_TOURNEY_BROCK, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_BROCK
	return

EventScript_TourneyBattleMisty::
	cleartrainerflag TRAINER_TOURNEY_MISTY
	trainerbattle_no_intro TRAINER_TOURNEY_MISTY, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_MISTY
	return

EventScript_TourneyBattleLtsurge::
	cleartrainerflag TRAINER_TOURNEY_LTSURGE
	trainerbattle_no_intro TRAINER_TOURNEY_LTSURGE, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_LTSURGE
	return

EventScript_TourneyBattleErika::
	cleartrainerflag TRAINER_TOURNEY_ERIKA
	trainerbattle_no_intro TRAINER_TOURNEY_ERIKA, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_ERIKA
	return

EventScript_TourneyBattleKoga::
	cleartrainerflag TRAINER_TOURNEY_KOGA
	trainerbattle_no_intro TRAINER_TOURNEY_KOGA, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_KOGA
	return

EventScript_TourneyBattleSabrina::
	cleartrainerflag TRAINER_TOURNEY_SABRINA
	trainerbattle_no_intro TRAINER_TOURNEY_SABRINA, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_SABRINA
	return

EventScript_TourneyBattleBlaine::
	cleartrainerflag TRAINER_TOURNEY_BLAINE
	trainerbattle_no_intro TRAINER_TOURNEY_BLAINE, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_BLAINE
	return

EventScript_TourneyBattleGiovanni::
	cleartrainerflag TRAINER_TOURNEY_GIOVANNI
	trainerbattle_no_intro TRAINER_TOURNEY_GIOVANNI, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_GIOVANNI
	return

EventScript_TourneyBattleLorelei::
	cleartrainerflag TRAINER_TOURNEY_LORELEI
	trainerbattle_no_intro TRAINER_TOURNEY_LORELEI, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_LORELEI
	return

EventScript_TourneyBattleBruno::
	cleartrainerflag TRAINER_TOURNEY_BRUNO
	trainerbattle_no_intro TRAINER_TOURNEY_BRUNO, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_BRUNO
	return

EventScript_TourneyBattleAgatha::
	cleartrainerflag TRAINER_TOURNEY_AGATHA
	trainerbattle_no_intro TRAINER_TOURNEY_AGATHA, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_AGATHA
	return

EventScript_TourneyBattleLance::
	cleartrainerflag TRAINER_TOURNEY_LANCE
	trainerbattle_no_intro TRAINER_TOURNEY_LANCE, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_LANCE
	return

EventScript_TourneyBattleBlue::
	cleartrainerflag TRAINER_TOURNEY_BLUE
	trainerbattle_no_intro TRAINER_TOURNEY_BLUE, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_BLUE
	return

EventScript_TourneyBattleOak::
	cleartrainerflag TRAINER_TOURNEY_OAK
	trainerbattle_no_intro TRAINER_TOURNEY_OAK, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_OAK
	return

EventScript_TourneyBattleN::
	cleartrainerflag TRAINER_TOURNEY_N
	trainerbattle_no_intro TRAINER_TOURNEY_N, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_N
	return

EventScript_TourneyBattleJessieJames::
	cleartrainerflag TRAINER_TOURNEY_JESSIE_JAMES
	trainerbattle_no_intro TRAINER_TOURNEY_JESSIE_JAMES, Text_TourneyDefeat
	cleartrainerflag TRAINER_TOURNEY_JESSIE_JAMES
	return

Text_TourneyDefeat::
	.string "A fine battle. The tournament\n"
	.string "belongs to the strong!$"
