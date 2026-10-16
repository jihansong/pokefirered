EverGrandeCity_PhoebesRoom_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, EverGrandeCity_PhoebesRoom_TY_OnFrame
	map_script MAP_SCRIPT_ON_TRANSITION, EverGrandeCity_PhoebesRoom_TY_OnTransition
	.byte 0

EverGrandeCity_PhoebesRoom_EventScript_H0::
	msgbox EverGrandeCity_PhoebesRoom_Text_H0, MSGBOX_NPC
	end

@ BEGIN PATCH (tools/hoenn_import/patches)


@ THYL_LEAGUE_V1
EverGrandeCity_PhoebesRoom_TY_OnTransition::
	setvar VAR_TEMP_1, 0
	end

EverGrandeCity_PhoebesRoom_TY_OnFrame::
	map_script_2 VAR_TEMP_1, 0, EverGrandeCity_PhoebesRoom_TY_Validate
	.2byte 0

EverGrandeCity_PhoebesRoom_TY_Validate::
	setvar VAR_TEMP_1, 1
	call TYHoennLeague_CheckBadges
	goto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
	goto_if_lt VAR_HOENN_LEAGUE_PROGRESS, 2, TYHoennLeague_InvalidEntry
	goto_if_gt VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_SIDNEY, TYHoennLeague_InvalidEntry
	end

EverGrandeCity_PhoebesRoom_TY_Boss::
	lock
	faceplayer
	call TYHoennLeague_CheckBadges
	goto_if_eq VAR_RESULT, FALSE, TYHoennLeague_InvalidEntry
	goto_if_lt VAR_HOENN_LEAGUE_PROGRESS, 2, TYHoennLeague_InvalidEntry
	goto_if_gt VAR_HOENN_LEAGUE_PROGRESS, 6, TYHoennLeague_InvalidEntry
	goto_if_not_defeated TRAINER_HOENN_SIDNEY, TYHoennLeague_InvalidEntry
	goto_if_defeated TRAINER_HOENN_PHOEBE, EverGrandeCity_PhoebesRoom_TY_Advance
	msgbox EverGrandeCity_PhoebesRoom_TY_Intro
	trainerbattle_no_intro TRAINER_HOENN_PHOEBE, EverGrandeCity_PhoebesRoom_TY_Defeat
	goto_if_not_defeated TRAINER_HOENN_PHOEBE, EverGrandeCity_PhoebesRoom_TY_Release
	goto_if_ge VAR_HOENN_LEAGUE_PROGRESS, 3, EverGrandeCity_PhoebesRoom_TY_Won
	setvar VAR_HOENN_LEAGUE_PROGRESS, 3
EverGrandeCity_PhoebesRoom_TY_Won::
	msgbox EverGrandeCity_PhoebesRoom_TY_Victory
EverGrandeCity_PhoebesRoom_TY_Release::
	release
	end

EverGrandeCity_PhoebesRoom_TY_Advance::
	goto_if_ge VAR_HOENN_LEAGUE_PROGRESS, 3, EverGrandeCity_PhoebesRoom_TY_Ready
	setvar VAR_HOENN_LEAGUE_PROGRESS, 3
EverGrandeCity_PhoebesRoom_TY_Ready::
	msgbox EverGrandeCity_PhoebesRoom_TY_GoOn, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EverGrandeCity_PhoebesRoom_TY_Release
	warp MAP_EVER_GRANDE_CITY_GLACIAS_ROOM, 6, 10
	waitstate
	releaseall
	end
@ END PATCH
