CeruleanCave_B1F_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, CeruleanCave_B1F_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, CeruleanCave_B1F_OnTransition
	.byte 0

CeruleanCave_B1F_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, CeruleanCave_B1F_EventScript_TryRemoveMewtwo
	end

CeruleanCave_B1F_EventScript_TryRemoveMewtwo::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, EventScript_Return
	removeobject VAR_LAST_TALKED
	return

CeruleanCave_B1F_OnTransition::
	call_if_unset FLAG_FOUGHT_MEWTWO, CeruleanCave_B1F_EventScript_ShowMewtwo
	setflag FLAG_HIDE_CERULEAN_CAVE_B1F_MEWTWO_SHADOW
	setflag FLAG_HIDE_CERULEAN_CAVE_B1F_CAPSULE_SHARDS
	setvar VAR_TEMP_1, 1
	goto_if_unset FLAG_FOUGHT_MEWTWO, CeruleanCave_B1F_EventScript_NoMew3Rumor
	goto_if_set FLAG_GOT_MYSTIC_SHARD, CeruleanCave_B1F_EventScript_NoMew3Rumor
	specialvar VAR_RESULT, HasCaughtMewtwoAndMew
	goto_if_eq VAR_RESULT, FALSE, CeruleanCave_B1F_EventScript_NoMew3Rumor
	clearflag FLAG_HIDE_CERULEAN_CAVE_B1F_CAPSULE_SHARDS
	goto_if_set FLAG_SAW_MEWTWO_SHADOW, CeruleanCave_B1F_EventScript_NoMew3Rumor
	clearflag FLAG_HIDE_CERULEAN_CAVE_B1F_MEWTWO_SHADOW
	setvar VAR_TEMP_1, 0
	end

CeruleanCave_B1F_EventScript_NoMew3Rumor::
	end

CeruleanCave_B1F_EventScript_ShowMewtwo::
	clearflag FLAG_HIDE_MEWTWO
	return

CeruleanCave_B1F_EventScript_Mewtwo::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	faceplayer
	waitse
	playmoncry SPECIES_MEWTWO, CRY_MODE_ENCOUNTER
	message CeruleanCave_B1F_Text_Mew
	waitmessage
	waitmoncry
	delay 20
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	waitbuttonpress
	setwildbattle SPECIES_MEWTWO, 70
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CeruleanCave_B1F_EventScript_DefeatedMewtwo
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, CeruleanCave_B1F_EventScript_RanFromMewtwo
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, CeruleanCave_B1F_EventScript_RanFromMewtwo
	setflag FLAG_FOUGHT_MEWTWO
	release
	end

CeruleanCave_B1F_EventScript_DefeatedMewtwo::
	setflag FLAG_FOUGHT_MEWTWO
	goto EventScript_RemoveStaticMon
	end

CeruleanCave_B1F_EventScript_RanFromMewtwo::
	setvar VAR_0x8004, SPECIES_MEWTWO
	goto EventScript_MonFlewAway
	end

@ The Mew3 rumor: a clone even stronger than MEWTWO. Once MEWTWO and MEW are
@ both caught, a shadow of MEWTWO waits where it stood among broken capsule
@ glass, scoffs at the rumor and fades. The shards are just a keepsake.
CeruleanCave_B1F_EventScript_Mew3Rumor::
	lockall
	setvar VAR_TEMP_1, 1
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox CeruleanCave_B1F_Text_AShadowStandsThere
	msgbox CeruleanCave_B1F_Text_ShadowACloneStrongerThanMe
	playse SE_M_TELEPORT
	applymovement LOCALID_CERULEAN_CAVE_MEWTWO_SHADOW, CeruleanCave_B1F_Movement_ShadowFades
	waitmovement 0
	removeobject LOCALID_CERULEAN_CAVE_MEWTWO_SHADOW
	setflag FLAG_SAW_MEWTWO_SHADOW
	msgbox CeruleanCave_B1F_Text_TheShadowVanished
	releaseall
	end

CeruleanCave_B1F_EventScript_CapsuleShards::
	lock
	msgbox CeruleanCave_B1F_Text_CapsuleShardsScattered
	giveitem ITEM_MYSTIC_SHARD
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	setflag FLAG_GOT_MYSTIC_SHARD
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CERULEAN_CAVE_CAPSULE_SHARDS_1
	removeobject LOCALID_CERULEAN_CAVE_CAPSULE_SHARDS_2
	fadescreen FADE_FROM_BLACK
	msgbox CeruleanCave_B1F_Text_JustARumorAfterAll
	release
	end

CeruleanCave_B1F_Movement_ShadowFades::
	face_down
	delay_16
	set_invisible
	delay_4
	set_visible
	delay_8
	set_invisible
	delay_4
	set_visible
	delay_4
	set_invisible
	delay_16
	step_end
