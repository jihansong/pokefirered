MtMoon_B2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, MtMoon_B2F_OnTransition
	.byte 0

MtMoon_B2F_OnTransition::
	call MtMoon_B2F_EventScript_HideJessieJames
	call MtMoon_B2F_EventScript_SetUpClefairyDance
	call MtMoon_B2F_EventScript_SetUpJirachiStar
	call_if_unset FLAG_GOT_FOSSIL_FROM_MT_MOON, MtMoon_B2F_EventScript_ShowFossils
	end

MtMoon_B2F_EventScript_ShowFossils::
	clearflag FLAG_HIDE_DOME_FOSSIL
	clearflag FLAG_HIDE_HELIX_FOSSIL
	return

MtMoon_B2F_EventScript_MiguelTrigger::
	lockall
	applymovement LOCALID_MIGUEL, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	call MtMoon_B2F_EventScript_BattleMiguel
	releaseall
	end

MtMoon_B2F_EventScript_Miguel::
	lock
	faceplayer
	goto_if_set FLAG_GOT_FOSSIL_FROM_MT_MOON, MtMoon_B2F_EventScript_MiguelFossilPicked
	goto_if_defeated TRAINER_SUPER_NERD_MIGUEL, MtMoon_B2F_EventScript_MiguelGoPickFossil
	call MtMoon_B2F_EventScript_BattleMiguel
	release
	end

MtMoon_B2F_EventScript_BattleMiguel::
	textcolor NPC_TEXT_COLOR_MALE
	message MtMoon_B2F_Text_MiguelIntro
	waitmessage
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	waitbuttonpress
	setvar VAR_LAST_TALKED, LOCALID_MIGUEL
	trainerbattle_no_intro TRAINER_SUPER_NERD_MIGUEL, MtMoon_B2F_Text_MiguelDefeat
	setvar VAR_MAP_SCENE_MT_MOON_B2F, 1
	msgbox MtMoon_B2F_Text_WellEachTakeAFossil
	return

MtMoon_B2F_EventScript_MiguelFossilPicked::
	msgbox MtMoon_B2F_Text_LabOnCinnabarRegeneratesFossils
	release
	end

MtMoon_B2F_EventScript_MiguelGoPickFossil::
	msgbox MtMoon_B2F_Text_WellEachTakeAFossil
	release
	end

MtMoon_B2F_EventScript_DomeFossil::
	lock
	faceplayer
	msgbox MtMoon_B2F_Text_YouWantDomeFossil, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MtMoon_B2F_EventScript_DontTakeFossil
	removeobject LOCALID_DOME_FOSSIL
	giveitem_msg MtMoon_B2F_Text_ObtainedDomeFossil, ITEM_DOME_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	closemessage
	special QuestLog_CutRecording
	delay 10
	applymovement LOCALID_MIGUEL, MtMoon_B2F_Movement_MiguelToHelixFossil
	waitmovement 0
	copyobjectxytoperm LOCALID_MIGUEL
	textcolor NPC_TEXT_COLOR_MALE
	playfanfare MUS_OBTAIN_KEY_ITEM
	message MtMoon_B2F_Text_ThenThisFossilIsMine
	waitmessage
	waitfanfare
	removeobject LOCALID_HELIX_FOSSIL
	setflag FLAG_GOT_DOME_FOSSIL
	setflag FLAG_GOT_FOSSIL_FROM_MT_MOON
	setvar VAR_MAP_SCENE_MT_MOON_B2F_JESSIE_JAMES, 1
	release
	end

MtMoon_B2F_Movement_MiguelToHelixFossil::
	walk_right
	walk_up
	walk_up
	walk_up
	step_end

MtMoon_B2F_EventScript_HelixFossil::
	lock
	faceplayer
	msgbox MtMoon_B2F_Text_YouWantHelixFossil, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MtMoon_B2F_EventScript_DontTakeFossil
	removeobject LOCALID_HELIX_FOSSIL
	giveitem_msg MtMoon_B2F_Text_ObtainedHelixFossil, ITEM_HELIX_FOSSIL, 1, MUS_OBTAIN_KEY_ITEM
	closemessage
	special QuestLog_CutRecording
	delay 10
	applymovement LOCALID_MIGUEL, MtMoon_B2F_Movement_MiguelToDomeFossil
	waitmovement 0
	copyobjectxytoperm LOCALID_MIGUEL
	textcolor NPC_TEXT_COLOR_MALE
	playfanfare MUS_OBTAIN_KEY_ITEM
	message MtMoon_B2F_Text_ThenThisFossilIsMine
	waitmessage
	waitfanfare
	removeobject LOCALID_DOME_FOSSIL
	setflag FLAG_GOT_HELIX_FOSSIL
	setflag FLAG_GOT_FOSSIL_FROM_MT_MOON
	setvar VAR_MAP_SCENE_MT_MOON_B2F_JESSIE_JAMES, 1
	release
	end

MtMoon_B2F_EventScript_DontTakeFossil::
	release
	end

MtMoon_B2F_Movement_MiguelToDomeFossil::
	walk_up
	walk_up
	walk_up
	step_end

MtMoon_B2F_EventScript_Grunt1::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT, MtMoon_B2F_Text_Grunt1Intro, MtMoon_B2F_Text_Grunt1Defeat
	msgbox MtMoon_B2F_Text_Grunt1PostBattle, MSGBOX_AUTOCLOSE
	end

MtMoon_B2F_EventScript_Grunt2::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_2, MtMoon_B2F_Text_Grunt2Intro, MtMoon_B2F_Text_Grunt2Defeat
	msgbox MtMoon_B2F_Text_Grunt2PostBattle, MSGBOX_AUTOCLOSE
	end

MtMoon_B2F_EventScript_Grunt3::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_3, MtMoon_B2F_Text_Grunt3Intro, MtMoon_B2F_Text_Grunt3Defeat
	msgbox MtMoon_B2F_Text_Grunt3PostBattle, MSGBOX_AUTOCLOSE
	end

MtMoon_B2F_EventScript_Grunt4::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_4, MtMoon_B2F_Text_Grunt4Intro, MtMoon_B2F_Text_Grunt4Defeat
	msgbox MtMoon_B2F_Text_Grunt4PostBattle, MSGBOX_AUTOCLOSE
	end

MtMoon_B2F_EventScript_JessieJamesTrigger0::
	lockall
	setvar VAR_TEMP_1, 0
	goto MtMoon_B2F_EventScript_JessieJames
	end

MtMoon_B2F_EventScript_JessieJamesTrigger1::
	lockall
	setvar VAR_TEMP_1, 1
	goto MtMoon_B2F_EventScript_JessieJames
	end

@ Jessie & James ambush the player, as in Pokémon Yellow.
MtMoon_B2F_EventScript_JessieJames::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playbgm MUS_ENCOUNTER_ROCKET, 0
	msgbox MtMoon_B2F_Text_JessieJamesStop
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	call_if_eq VAR_TEMP_1, 0, MtMoon_B2F_EventScript_JessieJamesAppear0
	call_if_eq VAR_TEMP_1, 1, MtMoon_B2F_EventScript_JessieJamesAppear1
	msgbox MtMoon_B2F_Text_JessieJamesIntro
	closemessage
	setvar VAR_LAST_TALKED, LOCALID_MT_MOON_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_MT_MOON, MtMoon_B2F_Text_JessieJamesDefeat
	msgbox MtMoon_B2F_Text_JessieJamesBlastOff
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_MT_MOON_JESSIE
	removeobject LOCALID_MT_MOON_JAMES
	fadescreen FADE_FROM_BLACK
	setvar VAR_MAP_SCENE_MT_MOON_B2F_JESSIE_JAMES, 2
	releaseall
	end

MtMoon_B2F_EventScript_JessieJamesAppear0::
	setobjectxyperm LOCALID_MT_MOON_JESSIE, 3, 3
	setobjectxyperm LOCALID_MT_MOON_JAMES, 4, 3
	addobject LOCALID_MT_MOON_JESSIE
	addobject LOCALID_MT_MOON_JAMES
	applymovement LOCALID_MT_MOON_JESSIE, MtMoon_B2F_EventScript_JessieJamesMovement0
	applymovement LOCALID_MT_MOON_JAMES, MtMoon_B2F_EventScript_JessieJamesMovement0
	waitmovement 0
	return

MtMoon_B2F_EventScript_JessieJamesMovement0:
	walk_down
	walk_down
	walk_down
	step_end

MtMoon_B2F_EventScript_JessieJamesAppear1::
	setobjectxyperm LOCALID_MT_MOON_JESSIE, 4, 3
	setobjectxyperm LOCALID_MT_MOON_JAMES, 3, 3
	addobject LOCALID_MT_MOON_JESSIE
	addobject LOCALID_MT_MOON_JAMES
	applymovement LOCALID_MT_MOON_JESSIE, MtMoon_B2F_EventScript_JessieJamesMovement1
	applymovement LOCALID_MT_MOON_JAMES, MtMoon_B2F_EventScript_JessieJamesMovement1
	waitmovement 0
	return

MtMoon_B2F_EventScript_JessieJamesMovement1:
	walk_down
	walk_down
	walk_down
	step_end

MtMoon_B2F_EventScript_HideJessieJames::
	setflag FLAG_HIDE_MT_MOON_B2F_JESSIE_JAMES
	return

@ The CLEFAIRY dance, a nod to HGSS's MT. MOON SQUARE. On the full moon of a
@ 30-day lunar month counted in steps (VAR_MOON_PHASE_STEPS), CLEFAIRY dance
@ around a MOON STONE in this room if the player carries a MOON STONE too.
MtMoon_B2F_EventScript_SetUpClefairyDance::
	setflag FLAG_HIDE_MT_MOON_CLEFAIRY_DANCE
	goto_if_set FLAG_SAW_CLEFAIRY_DANCE, MtMoon_B2F_EventScript_NoClefairyDance
	specialvar VAR_RESULT, IsFullMoon
	goto_if_eq VAR_RESULT, FALSE, MtMoon_B2F_EventScript_NoClefairyDance
	checkitem ITEM_MOON_STONE
	goto_if_eq VAR_RESULT, FALSE, MtMoon_B2F_EventScript_NoClefairyDance
	clearflag FLAG_HIDE_MT_MOON_CLEFAIRY_DANCE
MtMoon_B2F_EventScript_NoClefairyDance::
	return

MtMoon_B2F_EventScript_ClefairyDance::
	lockall
	msgbox MtMoon_B2F_Text_ClefairyDancing, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MtMoon_B2F_EventScript_ClefairyScatter
	closemessage
	setflag FLAG_SAW_CLEFAIRY_DANCE
	playmoncry SPECIES_CLEFAIRY, CRY_MODE_NORMAL
	waitmoncry
	applymovement LOCALID_DANCE_CLEFAIRY_N, MtMoon_B2F_Movement_DanceFromN
	applymovement LOCALID_DANCE_CLEFAIRY_E, MtMoon_B2F_Movement_DanceFromE
	applymovement LOCALID_DANCE_CLEFAIRY_S, MtMoon_B2F_Movement_DanceFromS
	applymovement LOCALID_DANCE_CLEFAIRY_W, MtMoon_B2F_Movement_DanceFromW
	waitmovement 0
	applymovement LOCALID_DANCE_CLEFAIRY_N, MtMoon_B2F_Movement_DanceFromN
	applymovement LOCALID_DANCE_CLEFAIRY_E, MtMoon_B2F_Movement_DanceFromE
	applymovement LOCALID_DANCE_CLEFAIRY_S, MtMoon_B2F_Movement_DanceFromS
	applymovement LOCALID_DANCE_CLEFAIRY_W, MtMoon_B2F_Movement_DanceFromW
	waitmovement 0
	applymovement LOCALID_DANCE_CLEFAIRY_N, MtMoon_B2F_Movement_DanceJump
	applymovement LOCALID_DANCE_CLEFAIRY_E, MtMoon_B2F_Movement_DanceJump
	applymovement LOCALID_DANCE_CLEFAIRY_S, MtMoon_B2F_Movement_DanceJump
	applymovement LOCALID_DANCE_CLEFAIRY_W, MtMoon_B2F_Movement_DanceJump
	waitmovement 0
	playmoncry SPECIES_CLEFAIRY, CRY_MODE_NORMAL
	waitmoncry
	msgbox MtMoon_B2F_Text_ClefableCameCloser
	applymovement LOCALID_DANCE_CLEFABLE, Common_Movement_FacePlayer
	waitmovement 0
	playmoncry SPECIES_CLEFABLE, CRY_MODE_NORMAL
	waitmoncry
	random 10
	goto_if_eq VAR_RESULT, 0, MtMoon_B2F_EventScript_ClefableBattle
	msgbox MtMoon_B2F_Text_ClefableHeldOutMoonStone
	giveitem ITEM_MOON_STONE
	goto_if_eq VAR_RESULT, FALSE, MtMoon_B2F_EventScript_NoRoomForMoonStone
	closemessage
	call MtMoon_B2F_EventScript_ClefairyLeave
	call MtMoon_B2F_EventScript_DanceFinished
	releaseall
	end

MtMoon_B2F_EventScript_NoRoomForMoonStone::
	msgbox MtMoon_B2F_Text_NoRoomForMoonStone
	closemessage
	call MtMoon_B2F_EventScript_ClefairyLeave
	call MtMoon_B2F_EventScript_DanceFinished
	releaseall
	end

MtMoon_B2F_EventScript_ClefableBattle::
	msgbox MtMoon_B2F_Text_ClefableAttacked
	closemessage
	setflag FLAG_HIDE_MT_MOON_CLEFAIRY_DANCE
	setwildbattle SPECIES_CLEFABLE, 30
	dowildbattle
	call MtMoon_B2F_EventScript_RemoveDancers
	call MtMoon_B2F_EventScript_DanceFinished
	releaseall
	end

MtMoon_B2F_EventScript_ClefairyScatter::
	msgbox MtMoon_B2F_Text_ClefairyScattered
	closemessage
	setflag FLAG_SAW_CLEFAIRY_DANCE
	applymovement LOCALID_DANCE_CLEFAIRY_N, MtMoon_B2F_Movement_FleeN
	applymovement LOCALID_DANCE_CLEFAIRY_E, MtMoon_B2F_Movement_FleeE
	applymovement LOCALID_DANCE_CLEFAIRY_S, MtMoon_B2F_Movement_FleeS
	applymovement LOCALID_DANCE_CLEFAIRY_W, MtMoon_B2F_Movement_FleeW
	applymovement LOCALID_DANCE_CLEFABLE, MtMoon_B2F_Movement_FleeN
	waitmovement 0
	call MtMoon_B2F_EventScript_RemoveDancers
	releaseall
	end

MtMoon_B2F_EventScript_ClefairyLeave::
	fadescreen FADE_TO_BLACK
	call MtMoon_B2F_EventScript_RemoveDancers
	fadescreen FADE_FROM_BLACK
	return

MtMoon_B2F_EventScript_RemoveDancers::
	setflag FLAG_HIDE_MT_MOON_CLEFAIRY_DANCE
	removeobject LOCALID_DANCE_CLEFAIRY_N
	removeobject LOCALID_DANCE_CLEFAIRY_E
	removeobject LOCALID_DANCE_CLEFAIRY_S
	removeobject LOCALID_DANCE_CLEFAIRY_W
	removeobject LOCALID_DANCE_CLEFABLE
	removeobject LOCALID_DANCE_MOON_STONE
	return

MtMoon_B2F_Movement_DanceFromN::
	walk_right
	walk_down
	walk_down
	walk_left
	walk_left
	walk_up
	walk_up
	walk_right
	face_down
	step_end

MtMoon_B2F_Movement_DanceFromE::
	walk_down
	walk_left
	walk_left
	walk_up
	walk_up
	walk_right
	walk_right
	walk_down
	face_left
	step_end

MtMoon_B2F_Movement_DanceFromS::
	walk_left
	walk_up
	walk_up
	walk_right
	walk_right
	walk_down
	walk_down
	walk_left
	face_up
	step_end

MtMoon_B2F_Movement_DanceFromW::
	walk_up
	walk_right
	walk_right
	walk_down
	walk_down
	walk_left
	walk_left
	walk_up
	face_right
	step_end

MtMoon_B2F_Movement_DanceJump::
	jump_in_place_down
	jump_in_place_down
	step_end

MtMoon_B2F_Movement_FleeN::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

MtMoon_B2F_Movement_FleeE::
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

MtMoon_B2F_Movement_FleeS::
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

MtMoon_B2F_Movement_FleeW::
	walk_fast_down
	walk_fast_down
	walk_fast_left
	step_end

@ JIRACHI: once the player has watched the CLEFAIRY dance to the end, a shooting
@ star falls where the MOON STONE stood. It stays until the full moon is over.
MtMoon_B2F_EventScript_DanceFinished::
	setflag FLAG_WATCHED_CLEFAIRY_DANCE
	goto_if_set FLAG_FOUGHT_JIRACHI, EventScript_Return
	delay 30
	playse SE_M_REFLECT
	msgbox MtMoon_B2F_Text_ShootingStarFell
	closemessage
	clearflag FLAG_HIDE_MT_MOON_JIRACHI_STAR
	addobject LOCALID_MT_MOON_JIRACHI_STAR
	return

MtMoon_B2F_EventScript_SetUpJirachiStar::
	setflag FLAG_HIDE_MT_MOON_JIRACHI_STAR
	goto_if_set FLAG_FOUGHT_JIRACHI, EventScript_Return
	goto_if_unset FLAG_WATCHED_CLEFAIRY_DANCE, EventScript_Return
	goto_if_unset FLAG_SAW_CLEFAIRY_DANCE, EventScript_Return
	specialvar VAR_RESULT, IsFullMoon
	goto_if_eq VAR_RESULT, FALSE, EventScript_Return
	clearflag FLAG_HIDE_MT_MOON_JIRACHI_STAR
	return

MtMoon_B2F_EventScript_JirachiStar::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	msgbox MtMoon_B2F_Text_StarIsTwinkling
	closemessage
	setwildbattle SPECIES_JIRACHI, 30
	waitse
	playmoncry SPECIES_JIRACHI, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 10
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	setflag FLAG_FOUGHT_JIRACHI
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, MtMoon_B2F_EventScript_JirachiFlewAway
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, MtMoon_B2F_EventScript_JirachiFlewAway
	goto EventScript_RemoveStaticMon
	end

MtMoon_B2F_EventScript_JirachiFlewAway::
	setvar VAR_0x8004, SPECIES_JIRACHI
	goto EventScript_MonFlewAway
	end
