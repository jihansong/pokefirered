

@ THYL_LEAGUE_V1
EverGrandeCity_HallOfFame_TY_Position::
	setobjectxyperm 1, 6, 5
	setvar VAR_TEMP_1, 0
	end

EverGrandeCity_HallOfFame_TY_OnFrame::
	map_script_2 VAR_TEMP_1, 0, EverGrandeCity_HallOfFame_TY_Record
	.2byte 0

EverGrandeCity_HallOfFame_TY_Record::
	setvar VAR_TEMP_1, 1
	lockall
	call TYHoennLeague_CheckBadges
	goto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
	goto_if_ne VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_SIDNEY, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_PHOEBE, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_GLACIA, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_DRAKE, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_WALLACE, TYHoennLeague_InvalidEntry
	msgbox EverGrandeCity_HallOfFame_TY_Welcome
	setflag FLAG_HOENN_LEAGUE_CLEAR
	setvar VAR_HOENN_LEAGUE_PROGRESS, 7
	setrespawn HEAL_LOCATION_HOENN_EVER_GRANDE_CITY_POKEMON_LEAGUE
	fadescreen FADE_TO_BLACK
	special EnterHallOfFame
	waitstate
	end

EverGrandeCity_HallOfFame_TY_Greeting::
	msgbox EverGrandeCity_HallOfFame_TY_Welcome, MSGBOX_NPC
	end
