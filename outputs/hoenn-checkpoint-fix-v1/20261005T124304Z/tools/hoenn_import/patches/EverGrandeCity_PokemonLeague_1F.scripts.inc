

@ THYL_LEAGUE_V1
EverGrandeCity_PokemonLeague_1F_OnTransition::
	setobjectxyperm 3, 9, 2
	setobjectxyperm 4, 10, 2
	setvar VAR_HOENN_LEAGUE_PROGRESS, 0
	cleartrainerflag TRAINER_HOENN_SIDNEY
	cleartrainerflag TRAINER_HOENN_PHOEBE
	cleartrainerflag TRAINER_HOENN_GLACIA
	cleartrainerflag TRAINER_HOENN_DRAKE
	cleartrainerflag TRAINER_HOENN_WALLACE
	end

EverGrandeCity_PokemonLeague_1F_EventScript_H1::
	goto TYHoennLeague_Enter

EverGrandeCity_PokemonLeague_1F_EventScript_H2::
	goto TYHoennLeague_Enter

TYHoennLeague_CheckBadges::
	goto_if_unset FLAG_HOENN_BADGE01_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE02_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE03_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE04_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE05_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE06_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE07_GET, TYHoennLeague_NoBadges
	goto_if_unset FLAG_HOENN_BADGE08_GET, TYHoennLeague_NoBadges
	setvar VAR_RESULT, TRUE
	return

TYHoennLeague_NoBadges::
	setvar VAR_RESULT, FALSE
	return

TYHoennLeague_Enter::
	lockall
	call TYHoennLeague_CheckBadges
	goto_if_eq VAR_RESULT, FALSE, TYHoennLeague_NeedBadges
	msgbox TYHoennLeague_Text_Challenge, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, TYHoennLeague_Release
	cleartrainerflag TRAINER_HOENN_SIDNEY
	cleartrainerflag TRAINER_HOENN_PHOEBE
	cleartrainerflag TRAINER_HOENN_GLACIA
	cleartrainerflag TRAINER_HOENN_DRAKE
	cleartrainerflag TRAINER_HOENN_WALLACE
	setvar VAR_HOENN_LEAGUE_PROGRESS, 1
	setrespawn HEAL_LOCATION_HOENN_EVER_GRANDE_CITY_POKEMON_LEAGUE
	warp MAP_EVER_GRANDE_CITY_SIDNEYS_ROOM, 6, 10
	waitstate
	releaseall
	end

TYHoennLeague_NeedBadges::
	msgbox TYHoennLeague_Text_NeedBadges
TYHoennLeague_Release::
	releaseall
	end

TYHoennLeague_InvalidEntry::
	lockall
	msgbox TYHoennLeague_Text_Invalid
	warp MAP_EVER_GRANDE_CITY_POKEMON_LEAGUE_1F, 9, 6
	waitstate
	releaseall
	end
