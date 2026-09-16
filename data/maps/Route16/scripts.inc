Route16_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, Route16_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, Route16_OnTransition
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, Route16_OnWarp
	.byte 0

Route16_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, Route16_EventScript_RemoveSnorlax
	end

Route16_EventScript_RemoveSnorlax::
	removeobject VAR_LAST_TALKED
	return

Route16_OnTransition::
	call_if_eq VAR_MAP_SCENE_ROUTE16, 1, Route16_OnTransitionCyclingRoad
	setflag FLAG_HIDE_ROUTE16_DITTO
	setflag FLAG_HIDE_ROUTE16_FAKE_OAK
	call_if_set FLAG_GOT_BICYCLE, Route16_EventScript_TryShowFakeOak
	end

Route16_EventScript_TryShowFakeOak::
	call_if_unset FLAG_FOUGHT_DISGUISED_DITTO, Route16_EventScript_ShowFakeOak
	return

Route16_EventScript_ShowFakeOak::
	clearflag FLAG_HIDE_ROUTE16_FAKE_OAK
	return

Route16_OnTransitionCyclingRoad::
	setflag FLAG_SYS_ON_CYCLING_ROAD
	return

Route16_OnWarp::
	map_script_2 VAR_MAP_SCENE_ROUTE16, 1, Route16_OnWarpCyclingRoad
	.2byte 0

Route16_OnWarpCyclingRoad::
	special ForcePlayerOntoBike
	end

Route16_EventScript_Snorlax::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_POKE_FLUTE, Route16_EventScript_SnorlaxNoPokeFlute
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	msgbox Text_WantToUsePokeFlute, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route16_EventScript_DontUsePokeFlute
	call EventScript_AwakenSnorlax
	setwildbattle SPECIES_SNORLAX, 30
	waitse
	playmoncry SPECIES_SNORLAX, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setflag FLAG_HIDE_ROUTE_16_SNORLAX
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	dowildbattle
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route16_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, Route16_EventScript_FoughtSnorlax
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, Route16_EventScript_FoughtSnorlax
	release
	end

Route16_EventScript_DontUsePokeFlute::
	release
	end

Route16_EventScript_FoughtSnorlax::
	msgbox Text_SnorlaxReturnedToMountains
	release
	end

Route16_EventScript_SnorlaxNoPokeFlute::
	msgbox Route16_Text_MonSprawledOutInSlumber
	release
	end

Route16_EventScript_CyclingRoadSign::
	msgbox Route16_Text_CyclingRoadSign, MSGBOX_SIGN
	end

Route16_EventScript_RouteSign::
	msgbox Route16_Text_RouteSign, MSGBOX_SIGN
	end

@ BW's Zoroark illusions, with a DITTO: once the Cycling Road is open, "PROF. OAK"
@ stands by the house on Route 16 saying odd things. Talking to him shakes the
@ scene and reveals a Lv25 DITTO.
Route16_EventScript_FakeOak::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	msgbox Route16_Text_FakeOakPokemonPokemon
	special QuestLog_CutRecording
	msgbox Route16_Text_OakIsActingStrange
	closemessage
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 6
	setvar VAR_0x8007, 3
	special ShakeScreen
	delay 20
	applymovement LOCALID_ROUTE16_FAKE_OAK, Route16_Movement_IllusionFlicker
	waitmovement 0
	removeobject LOCALID_ROUTE16_FAKE_OAK
	addobject LOCALID_ROUTE16_DITTO
	waitse
	playmoncry SPECIES_DITTO, CRY_MODE_ENCOUNTER
	msgbox Route16_Text_OakWasADitto
	waitmoncry
	setwildbattle SPECIES_DITTO, 25
	dowildbattle
	setflag FLAG_FOUGHT_DISGUISED_DITTO
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE16_DITTO
	fadescreen FADE_FROM_BLACK
	release
	end

Route16_EventScript_RumorWoman::
	lock
	faceplayer
	goto_if_set FLAG_FOUGHT_DISGUISED_DITTO, Route16_EventScript_RumorWomanAfter
	msgbox Route16_Text_RumorWomanOakBeenThereForHours
	release
	end

Route16_EventScript_RumorWomanAfter::
	msgbox Route16_Text_RumorWomanDittoRumor
	release
	end

Route16_Movement_IllusionFlicker::
	set_invisible
	delay_4
	set_visible
	delay_4
	set_invisible
	delay_4
	set_visible
	delay_8
	set_invisible
	delay_8
	step_end
