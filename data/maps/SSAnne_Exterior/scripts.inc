SSAnne_Exterior_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, SSAnne_Exterior_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, SSAnne_Exterior_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, SSAnne_Exterior_OnFrame
	.byte 0

@ Once the ship has sailed, the gangway no longer leads aboard
SSAnne_Exterior_OnLoad::
	call_if_ge VAR_MAP_SCENE_VERMILION_CITY, 3, SSAnne_Exterior_EventScript_CloseGangway
	end

SSAnne_Exterior_EventScript_CloseGangway::
	setmetatile 32, 14, METATILE_VermilionCity_SSAnneWarp, TRUE
	return

SSAnne_Exterior_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SSANNE_EXTERIOR
	setflag FLAG_HIDE_SSANNE_EXTERIOR_MEW
	call_if_eq VAR_SSANNE_EXTERIOR_TRUCK_PUSHED, DIR_SOUTH, SSAnne_Exterior_EventScript_TruckPushedSouth
	call_if_eq VAR_SSANNE_EXTERIOR_TRUCK_PUSHED, DIR_NORTH, SSAnne_Exterior_EventScript_TruckPushedNorth
	call_if_eq VAR_SSANNE_EXTERIOR_TRUCK_PUSHED, DIR_WEST, SSAnne_Exterior_EventScript_TruckPushedWest
	call_if_eq VAR_SSANNE_EXTERIOR_TRUCK_PUSHED, DIR_EAST, SSAnne_Exterior_EventScript_TruckPushedEast
	end

SSAnne_Exterior_EventScript_TruckPushedSouth::
	setobjectxyperm LOCALID_SSANNE_TRUCK, 57, 24
	setobjectxyperm LOCALID_SSANNE_TRUCK_BACK, 58, 24
	return

SSAnne_Exterior_EventScript_TruckPushedNorth::
	setobjectxyperm LOCALID_SSANNE_TRUCK, 57, 22
	setobjectxyperm LOCALID_SSANNE_TRUCK_BACK, 58, 22
	return

SSAnne_Exterior_EventScript_TruckPushedWest::
	setobjectxyperm LOCALID_SSANNE_TRUCK, 56, 23
	setobjectxyperm LOCALID_SSANNE_TRUCK_BACK, 57, 23
	return

SSAnne_Exterior_EventScript_TruckPushedEast::
	setobjectxyperm LOCALID_SSANNE_TRUCK, 58, 23
	setobjectxyperm LOCALID_SSANNE_TRUCK_BACK, 59, 23
	return

@ Pokémon Yellow's truck by the S.S. Anne, with Mew hiding under it.
@ Once the ship has sailed, a Pokémon that knows STRENGTH can push the truck
@ aside and Mew jumps out of the spot it covered.
SSAnne_Exterior_EventScript_Truck::
	goto_if_questlog EventScript_ReleaseEnd
	lockall
	goto_if_set FLAG_FOUGHT_MEW, SSAnne_Exterior_EventScript_TruckWontBudge
	goto_if_lt VAR_MAP_SCENE_VERMILION_CITY, 3, SSAnne_Exterior_EventScript_TruckWontBudge
	checkpartymove MOVE_STRENGTH
	goto_if_eq VAR_RESULT, PARTY_SIZE, SSAnne_Exterior_EventScript_TruckWontBudge
	setfieldeffectargument 0, VAR_RESULT
	setvar VAR_0x8004, LOCALID_SSANNE_TRUCK
	setvar VAR_0x8005, LOCALID_SSANNE_TRUCK_BACK
	specialvar VAR_RESULT, CanPushTruck
	goto_if_eq VAR_RESULT, FALSE, SSAnne_Exterior_EventScript_TruckWontBudge
	msgbox SSAnne_Exterior_Text_TruckLooksHeavy, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SSAnne_Exterior_EventScript_DontPushTruck
	closemessage
	special QuestLog_CutRecording
	dofieldeffect FLDEFF_USE_STRENGTH
	waitstate
	special PushTruck
	waitstate
	delay 16
	setobjectxyperm LOCALID_SSANNE_MEW, VAR_0x8006, VAR_0x8007
	addobject LOCALID_SSANNE_MEW
	specialvar VAR_RESULT, GetPlayerFacingDirection
	copyvar VAR_0x8008, VAR_RESULT
	call_if_eq VAR_RESULT, DIR_SOUTH, SSAnne_Exterior_EventScript_MewJumpsOutUp
	call_if_eq VAR_RESULT, DIR_NORTH, SSAnne_Exterior_EventScript_MewJumpsOutDown
	call_if_eq VAR_RESULT, DIR_WEST, SSAnne_Exterior_EventScript_MewJumpsOutRight
	call_if_eq VAR_RESULT, DIR_EAST, SSAnne_Exterior_EventScript_MewJumpsOutLeft
	applymovement LOCALID_SSANNE_MEW, Common_Movement_ExclamationMark
	waitmovement 0
	waitse
	playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 20
	setwildbattle SPECIES_MEW, 30
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	setflag FLAG_FOUGHT_MEW
	copyvar VAR_SSANNE_EXTERIOR_TRUCK_PUSHED, VAR_0x8008
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, SSAnne_Exterior_EventScript_MewFledAway
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, SSAnne_Exterior_EventScript_MewFledAway
	goto_if_eq VAR_RESULT, B_OUTCOME_MON_FLED, SSAnne_Exterior_EventScript_MewFledAway
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_MEW
	fadescreen FADE_FROM_BLACK
	releaseall
	end

SSAnne_Exterior_EventScript_MewFledAway::
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SSANNE_MEW
	fadescreen FADE_FROM_BLACK
	bufferspeciesname STR_VAR_1, SPECIES_MEW
	msgbox Text_MonFlewAway
	releaseall
	end

SSAnne_Exterior_EventScript_MewJumpsOutUp::
	applymovement LOCALID_SSANNE_MEW, SSAnne_Exterior_Movement_MewJumpOutUp
	waitmovement 0
	return

SSAnne_Exterior_EventScript_MewJumpsOutDown::
	applymovement LOCALID_SSANNE_MEW, SSAnne_Exterior_Movement_MewJumpOutDown
	waitmovement 0
	return

SSAnne_Exterior_EventScript_MewJumpsOutRight::
	applymovement LOCALID_SSANNE_MEW, SSAnne_Exterior_Movement_MewJumpOutRight
	waitmovement 0
	return

SSAnne_Exterior_EventScript_MewJumpsOutLeft::
	applymovement LOCALID_SSANNE_MEW, SSAnne_Exterior_Movement_MewJumpOutLeft
	waitmovement 0
	return

SSAnne_Exterior_EventScript_TruckWontBudge::
	msgbox SSAnne_Exterior_Text_TruckWontBudge
	releaseall
	end

SSAnne_Exterior_EventScript_DontPushTruck::
	closemessage
	releaseall
	end

SSAnne_Exterior_Movement_MewJumpOutUp::
	jump_in_place_up
	step_end

SSAnne_Exterior_Movement_MewJumpOutDown::
	jump_in_place_down
	step_end

SSAnne_Exterior_Movement_MewJumpOutRight::
	jump_in_place_right
	step_end

SSAnne_Exterior_Movement_MewJumpOutLeft::
	jump_in_place_left
	step_end

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
