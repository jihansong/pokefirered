SkyPillar_Top_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SkyPillar_Top_TY_RestoreCleanFloor
	map_script MAP_SCRIPT_ON_TRANSITION, SkyPillar_Top_TY_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, SkyPillar_Top_TY_OnResume
	map_script MAP_SCRIPT_ON_RETURN_TO_FIELD, SkyPillar_Top_TY_OnReturnToField
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Thunder Yellow Hoenn sea-sky chapter v1
SkyPillar_Top_EventScript_TY_Rayquaza::
	goto_if_questlog EventScript_ReleaseEnd
	goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, SkyPillar_Top_TY_Encounter
	goto_if_set FLAG_HOENN_BADGE08_GET, SkyPillar_Top_TY_Wake
	goto_if_unset FLAG_HOENN_SEAFLOOR_CLEARED, SkyPillar_Top_TY_Sleep
SkyPillar_Top_TY_Wake::
	lockall
	msgbox SkyPillar_Top_Text_TY_Wake, MSGBOX_DEFAULT
	applymovement 1, SkyPillar_Top_Movement_TY_Awake
	waitmovement 0
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_NORMAL
	waitmoncry
	applymovement 1, SkyPillar_Top_Movement_TY_Call
	waitmovement 0
	delay 30
	applymovement 1, SkyPillar_Top_Movement_TY_Rise
	waitmovement 0
	removeobject 1
	setvar VAR_TEMP_E, 0x5251
	setflag FLAG_HOENN_RAYQUAZA_AWAKENED
	msgbox SkyPillar_Top_Text_TY_After, MSGBOX_DEFAULT
	releaseall
	end

SkyPillar_Top_TY_Sleep::
	msgbox SkyPillar_Top_Text_TY_Sleep, MSGBOX_SIGN
	end

SkyPillar_Top_TY_Done::
	end

@ Keep the existing awakening actor/local ID. Once it returns, the shared
@ Tanoby terminal flag owns the Lv70 encounter as well as the old Lv50 one.
SkyPillar_Top_TY_Encounter::
	goto_if_set FLAG_FOUGHT_RAYQUAZA, SkyPillar_Top_TY_Done
	special QuestLog_CutRecording
	lockall
	waitse
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_ENCOUNTER
	message SkyPillar_Top_Text_TY_Challenge
	waitmessage
	waitmoncry
	delay 20
	waitbuttonpress
	setwildbattle SPECIES_RAYQUAZA, 70
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, SkyPillar_Top_TY_Caught
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, SkyPillar_Top_TY_Defeated
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, SkyPillar_Top_TY_Retreated
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, SkyPillar_Top_TY_Retreated
	goto_if_eq VAR_RESULT, B_OUTCOME_MON_FLED, SkyPillar_Top_TY_Retreated
@ Native loss goes to CB2_WhiteOut before this script resumes. Unknown
@ outcomes must not consume the encounter by a broad terminal fallback.
	releaseall
	end

SkyPillar_Top_TY_Caught::
	setflag FLAG_FOUGHT_RAYQUAZA
	setflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	removeobject 1
	releaseall
	end

SkyPillar_Top_TY_Defeated::
	setflag FLAG_FOUGHT_RAYQUAZA
	setflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	goto EventScript_RemoveStaticMon
	end

SkyPillar_Top_TY_Retreated::
	setvar VAR_TEMP_E, 0x5251
	setvar VAR_0x8004, SPECIES_RAYQUAZA
	goto EventScript_MonFlewAway
	end

@ Exact map-local marker distinguishes this visit's departure from an old
@ save's default TEMP values. A normal map re-entry starts a fresh visit.
SkyPillar_Top_TY_OnTransition::
	goto_if_questlog SkyPillar_Top_TY_Done
	setvar VAR_TEMP_E, 0
	call SkyPillar_Top_TY_PrepareActor
	end

SkyPillar_Top_TY_OnResume::
	goto_if_questlog SkyPillar_Top_TY_Done
	call SkyPillar_Top_TY_PrepareActor
	end

@ ON_RESUME runs before the engine recreates saved sprites. Rebuild only
@ after that pass; otherwise addobject leaves an orphan duplicate sprite.
SkyPillar_Top_TY_OnReturnToField::
	goto_if_questlog SkyPillar_Top_TY_Done
	goto_if_unset FLAG_SYS_SPECIAL_WILD_BATTLE, SkyPillar_Top_TY_ResumeActor
@ Only the current scripted wild-battle gate may interpret BattleOutcome.
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, SkyPillar_Top_TY_Done
	setflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	removeobject 1
	end

SkyPillar_Top_TY_ResumeActor::
@ setobjectmovementtype changes only the template. Rebuild this single actor
@ so an old Continue's active sleeping pose also adopts the new phase.
@ removeobject sets its derived hide flag, so PrepareActor follows removal.
	removeobject 1
	call SkyPillar_Top_TY_PrepareActor
	goto_if_set FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA, SkyPillar_Top_TY_Done
	addobject 1
	end

SkyPillar_Top_TY_PrepareActor::
@ Prior Tanoby captures must not suppress the main story's sleeping actor.
	goto_if_unset FLAG_HOENN_RAYQUAZA_AWAKENED, SkyPillar_Top_TY_PrepareSleeping
	goto_if_set FLAG_FOUGHT_RAYQUAZA, SkyPillar_Top_TY_PrepareHidden
	goto_if_eq VAR_TEMP_E, 0x5251, SkyPillar_Top_TY_PrepareHidden
	clearflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	setobjectmovementtype 1, MOVEMENT_TYPE_WALK_IN_PLACE_RIGHT
	return

SkyPillar_Top_TY_PrepareSleeping::
	clearflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	setobjectmovementtype 1, MOVEMENT_TYPE_FACE_DOWN
	return

SkyPillar_Top_TY_PrepareHidden::
	setflag FLAG_HIDE_HOENN_SKY_PILLAR_RAYQUAZA
	return

SkyPillar_Top_Movement_TY_Awake::
	walk_in_place_fast_left
	step_end

SkyPillar_Top_Movement_TY_Call::
	walk_in_place_left
	step_end

SkyPillar_Top_Movement_TY_Rise::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

SkyPillar_Top_TY_RestoreCleanFloor::
	special HoennSkyPillarRestoreFloor
	end
@ END PATCH
