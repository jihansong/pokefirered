SixIsland_WaterPath_Cabin_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SixIsland_WaterPath_Cabin_OnTransition
	.byte 0

SixIsland_WaterPath_Cabin_OnTransition::
	setflag FLAG_TEMP_1
	goto_if_set FLAG_BEAT_N_FINAL, SixIsland_WaterPath_Cabin_EventScript_TransitionEnd
	call_if_set FLAG_SYS_GAME_CLEAR, SixIsland_WaterPath_Cabin_EventScript_ShowN
SixIsland_WaterPath_Cabin_EventScript_TransitionEnd::
	end

SixIsland_WaterPath_Cabin_EventScript_ShowN::
	clearflag FLAG_TEMP_1
	return

@ v0.6.0: after the HALL OF FAME, N waits in his cabin for a last battle. He
@ leaves N's LETTER behind (data/scripts/n.inc has the shared scenes).
SixIsland_WaterPath_Cabin_EventScript_N::
	lock
	faceplayer
	msgbox SixIsland_WaterPath_Cabin_Text_NYouCame
	call EventScript_NHearsPikachu
	msgbox SixIsland_WaterPath_Cabin_Text_NLastBattle
	trainerbattle_no_intro TRAINER_N_FINAL, SixIsland_WaterPath_Cabin_Text_NDefeat
	msgbox SixIsland_WaterPath_Cabin_Text_NFarewell
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_N_CABIN
	setflag FLAG_BEAT_N_FINAL
	fadescreen FADE_FROM_BLACK
	msgbox SixIsland_WaterPath_Cabin_Text_LetterOnTable
	giveitem ITEM_N_LETTER
	msgbox SixIsland_WaterPath_Cabin_Text_LetterReads
	release
	end
