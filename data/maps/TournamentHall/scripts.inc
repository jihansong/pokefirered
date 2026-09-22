TournamentHall_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, TournamentHall_OnTransition
	.byte 0

@ Thunder Yellow v0.6.0: the champion tournament. Three matches in a row against
@ entrants drawn from the GYM LEADERS, the ELITE FOUR, the RIVAL, PROF. OAK, N
@ and TEAM ROCKET (tools/make_tournament.py, data/scripts/tournament_battles.inc).
@ Losing a match ends the run, so the round counter is cleared on every entry.
TournamentHall_OnTransition::
	special Tournament_Reset
	end

TournamentHall_EventScript_Announcer::
	lock
	faceplayer
	msgbox TournamentHall_Text_AnnouncerIntro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, TournamentHall_EventScript_Leave
	special Tournament_Draw
	msgbox TournamentHall_Text_DrawMade
TournamentHall_EventScript_NextMatch::
	special Tournament_SetUpMatch
	msgbox TournamentHall_Text_MatchAnnounce
	closemessage
	call EventScript_TourneyBattle
	special HealPlayerParty
	specialvar VAR_RESULT, Tournament_NextRound
	goto_if_eq VAR_RESULT, TRUE, TournamentHall_EventScript_Won
	msgbox TournamentHall_Text_WonMatch
	goto TournamentHall_EventScript_NextMatch

TournamentHall_EventScript_Won::
	special Tournament_Reset
	playfanfare MUS_OBTAIN_BADGE
	msgbox TournamentHall_Text_WonTournament
	waitfanfare
	goto_if_set FLAG_WON_CHAMPION_TOURNAMENT, TournamentHall_EventScript_WonAgain
	setflag FLAG_WON_CHAMPION_TOURNAMENT
	msgbox TournamentHall_Text_FirstTrophy
	giveitem ITEM_RARE_CANDY, 3
	release
	end

TournamentHall_EventScript_WonAgain::
	giveitem ITEM_RARE_CANDY
	release
	end

TournamentHall_EventScript_Leave::
	msgbox TournamentHall_Text_ComeBack
	closemessage
	warp MAP_INDIGO_PLATEAU_POKEMON_CENTER_1F, 21, 13
	waitstate
	release
	end
