Route25_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route25_OnTransition
	.byte 0

Route25_OnTransition::
	setflag FLAG_HIDE_ROUTE25_RED_GYARADOS
	goto_if_set FLAG_FOUGHT_RED_GYARADOS, Route25_EventScript_NoRedGyarados
	goto_if_unset FLAG_BADGE02_GET, Route25_EventScript_NoRedGyarados
	clearflag FLAG_HIDE_ROUTE25_RED_GYARADOS
	end

Route25_EventScript_NoRedGyarados::
	end

@ HGSS's red GYARADOS of the Lake of Rage, in the pond by BILL's cottage.
@ A forced-shiny Lv30 GYARADOS; afterwards the player finds a RED SCALE,
@ which BILL trades for an EXP. SHARE (Mr. POKéMON's trade in HGSS).
Route25_EventScript_RedGyarados::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	faceplayer
	waitse
	playmoncry SPECIES_GYARADOS, CRY_MODE_ENCOUNTER
	msgbox Route25_Text_GyaradosGyashaa
	waitmoncry
	setwildbattle SPECIES_GYARADOS, 30
	special MakeScriptedWildMonShiny
	dowildbattle
	setflag FLAG_FOUGHT_RED_GYARADOS
	removeobject LOCALID_ROUTE25_RED_GYARADOS
	giveitem ITEM_RED_SCALE
	release
	end

Route25_EventScript_SeaCottageSign::
	msgbox Route25_Text_SeaCottageSign, MSGBOX_SIGN
	end

Route25_EventScript_Man::
	msgbox Route25_Text_AreYouHereAlone, MSGBOX_NPC
	end
