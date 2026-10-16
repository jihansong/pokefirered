SSAnne_Exterior_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SSAnne_Exterior_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, SSAnne_Exterior_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SSAnne_Exterior_OnFrame
	map_script MAP_SCRIPT_ON_RESUME, SSAnne_Exterior_DockOnResume
	.byte 0

@ Once the ship has sailed, the gangway no longer leads aboard
SSAnne_Exterior_OnLoad::
	setflag FLAG_HIDE_VERMILION_CITY_MEW
	call_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, SSAnne_Exterior_DockTruckShifted
	call_if_ge VAR_MAP_SCENE_VERMILION_CITY, 3, SSAnne_Exterior_EventScript_CloseGangway
	end

SSAnne_Exterior_EventScript_CloseGangway::
	setmetatile 32, 14, METATILE_VermilionCity_SSAnneWarp, TRUE
	return

SSAnne_Exterior_OnTransition::
	setflag FLAG_HIDE_VERMILION_CITY_MEW
	setworldmapflag FLAG_WORLD_MAP_SSANNE_EXTERIOR
	end

SSAnne_Exterior_OnFrame::
	map_script_2 VAR_MAP_SCENE_VERMILION_CITY, 1, SSAnne_Exterior_ExitSSAnne
	.2byte 0

SSAnne_Exterior_ExitSSAnne::
	lockall
	getplayerxy VAR_0x8004, VAR_0x8005
	call_if_le VAR_0x8005, 6, SSAnne_Exterior_WalkDown
	call_if_ge VAR_0x8005, 7, SSAnne_Exterior_WalkInPlaceDown
	fadenewbgm MUS_SURF
	delay 50
	special DoSSAnneDepartureCutscene
	waitstate
	removeobject LOCALID_SS_ANNE
	applymovement LOCALID_PLAYER, SSAnne_Exterior_Movement_Exit
	waitmovement 0
	setvar VAR_MAP_SCENE_VERMILION_CITY, 2
	setvar VAR_VERMILION_CITY_TICKET_CHECK_TRIGGER, 0
	warp MAP_VERMILION_CITY, 23, 34
	waitstate
	releaseall
	end

SSAnne_Exterior_WalkDown::
	applymovement LOCALID_PLAYER, SSAnne_Exterior_Movement_WalkDown
	waitmovement 0
	return

SSAnne_Exterior_WalkInPlaceDown::
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	return

SSAnne_Exterior_Movement_Exit::
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	step_end

SSAnne_Exterior_Movement_WalkDown::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

SSAnne_Exterior_DockOnResume::
	setflag FLAG_HIDE_VERMILION_CITY_MEW
	removeobject LOCALID_SSANNE_DOCK_MEW
	call_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, SSAnne_Exterior_DockTruckShifted
	end

SSAnne_Exterior_EventScript_DockTruck::
	goto_if_questlog EventScript_ReleaseEnd
	lockall
	goto_if_set FLAG_GOT_MEW_EGG, SSAnne_Exterior_DockMewGone
	goto_if_set FLAG_FOUGHT_MEW, SSAnne_Exterior_DockMewGone
	goto_if_ne VAR_VERMILION_CITY_TRUCK_PUSHED, 0, SSAnne_Exterior_DockMewGone
	goto_if_lt VAR_MAP_SCENE_VERMILION_CITY, 3, SSAnne_Exterior_DockTruckWontBudge
	checkpartymove MOVE_STRENGTH
	goto_if_eq VAR_RESULT, PARTY_SIZE, SSAnne_Exterior_DockTruckWontBudge
	setfieldeffectargument 0, VAR_RESULT
	msgbox VermilionCity_Text_TruckLooksHeavy, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SSAnne_Exterior_DockDeclined
	closemessage
	special QuestLog_CutRecording
	dofieldeffect FLDEFF_USE_STRENGTH
	waitstate
	playse SE_M_STRENGTH
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 2
	special ShakeScreen
	applymovement LOCALID_PLAYER, SSAnne_Exterior_DockPushMovement
	waitmovement 0
	call SSAnne_Exterior_DockTruckShifted
	special DrawWholeMapView
	setvar VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_WEST
	delay 16
	addobject LOCALID_SSANNE_DOCK_MEW
	applymovement LOCALID_SSANNE_DOCK_MEW, SSAnne_Exterior_DockMewJump
	waitmovement 0
	applymovement LOCALID_SSANNE_DOCK_MEW, Common_Movement_ExclamationMark
	waitmovement 0
	waitse
	playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 20
	setflag FLAG_FOUGHT_MEW
	seteventmon SPECIES_MEW, 30
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, SSAnne_Exterior_DockMewFled
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, SSAnne_Exterior_DockMewFled
	goto_if_eq VAR_RESULT, B_OUTCOME_MON_FLED, SSAnne_Exterior_DockMewFled
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_DOCK_MEW
	fadescreen FADE_FROM_BLACK
	releaseall
	end

SSAnne_Exterior_DockMewFled::
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_DOCK_MEW
	fadescreen FADE_FROM_BLACK
	bufferspeciesname STR_VAR_1, SPECIES_MEW
	msgbox Text_MonFlewAway
	releaseall
	end

SSAnne_Exterior_DockMewGone::
	msgbox VermilionCity_Text_TruckPinkHair
	releaseall
	end

SSAnne_Exterior_DockTruckWontBudge::
	msgbox VermilionCity_Text_TruckWontBudge
	releaseall
	end

SSAnne_Exterior_DockDeclined::
	closemessage
	releaseall
	end

SSAnne_Exterior_DockPushMovement::
	walk_in_place_left
	walk_in_place_left
	step_end

SSAnne_Exterior_DockMewJump::
	jump_in_place_right
	step_end

SSAnne_Exterior_DockTruckShifted::
	setmetatile 54, 1, 0x313, TRUE
	setmetatile 55, 1, 0x314, TRUE
	setmetatile 56, 1, 0x12B, TRUE
	setmetatile 54, 2, 0x315, TRUE
	setmetatile 55, 2, 0x316, TRUE
	setmetatile 56, 2, 0x317, TRUE
	setmetatile 57, 2, 0x31B, FALSE
	setmetatile 54, 3, 0x318, TRUE
	setmetatile 55, 3, 0x319, TRUE
	setmetatile 56, 3, 0x31A, TRUE
	setmetatile 57, 3, 0x1C1, FALSE
	return
