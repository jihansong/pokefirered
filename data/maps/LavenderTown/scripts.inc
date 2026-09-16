LavenderTown_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LavenderTown_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, LavenderTown_OnResume
	.byte 0

LavenderTown_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_LAVENDER_TOWN
	setvar VAR_MAP_SCENE_S_S_ANNE_2F_CORRIDOR, 1
	setflag FLAG_HIDE_SS_ANNE_RIVAL
	call_if_eq VAR_LAVENDER_SYNDROME, 0, LavenderTown_EventScript_CheckSyndrome
	end

@ Lavender Town Syndrome: after meeting 3 unidentified GHOSTS in the POKéMON TOWER,
@ coming back to town once makes the music bend and the town's edges darken.
@ The CHANNELER at the tower entrance purifies it.
LavenderTown_EventScript_CheckSyndrome::
	goto_if_lt VAR_LAVENDER_GHOST_SIGHTINGS, 3, EventScript_Return
	setvar VAR_LAVENDER_SYNDROME, 1
	return

LavenderTown_OnResume::
	call_if_eq VAR_LAVENDER_SYNDROME, 1, LavenderTown_EventScript_StartSyndrome
	end

LavenderTown_EventScript_StartSyndrome::
	special StartLavenderSyndrome
	return

LavenderTown_EventScript_CanYouHearIt::
	msgbox LavenderTown_Text_CanYouHearIt
	release
	end

LavenderTown_EventScript_LittleGirl::
	lock
	faceplayer
	goto_if_eq VAR_LAVENDER_SYNDROME, 1, LavenderTown_EventScript_CanYouHearIt
	msgbox LavenderTown_Text_DoYouBelieveInGhosts, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, LavenderTown_EventScript_LittleGirlBelieve
	msgbox LavenderTown_Text_JustImaginingWhiteHand
	release
	end

LavenderTown_EventScript_LittleGirlBelieve::
	msgbox LavenderTown_Text_SoThereAreBelievers
	release
	end

LavenderTown_EventScript_WorkerM::
	lock
	faceplayer
	goto_if_eq VAR_LAVENDER_SYNDROME, 1, LavenderTown_EventScript_CanYouHearIt
	msgbox LavenderTown_Text_TownKnownAsMonGraveSite
	release
	end

LavenderTown_EventScript_Boy::
	lock
	faceplayer
	goto_if_eq VAR_LAVENDER_SYNDROME, 1, LavenderTown_EventScript_CanYouHearIt
	msgbox LavenderTown_Text_GhostsAppearedInTower
	release
	end

LavenderTown_EventScript_TownSign::
	msgbox LavenderTown_Text_TownSign, MSGBOX_SIGN
	end

LavenderTown_EventScript_SilphScopeNotice::
	msgbox LavenderTown_Text_SilphScopeNotice, MSGBOX_SIGN
	end

LavenderTown_EventScript_VolunteerHouseSign::
	msgbox LavenderTown_Text_VolunteerPokemonHouse, MSGBOX_SIGN
	end

LavenderTown_EventScript_PokemonTowerSign::
	msgbox LavenderTown_Text_PokemonTowerSign, MSGBOX_SIGN
	end
