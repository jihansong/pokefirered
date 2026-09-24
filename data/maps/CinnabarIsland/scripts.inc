CinnabarIsland_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CinnabarIsland_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CinnabarIsland_OnFrame
	.byte 0

CinnabarIsland_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_CINNABAR_ISLAND
	call CinnabarIsland_EventScript_ReadyRocketMagmar
	call CinnabarIsland_EventScript_CheckUnlockGym
	call_if_eq VAR_MAP_SCENE_CINNABAR_ISLAND, 1, CinnabarIsland_EventScript_ReadyObjectsSailToOneIsland
	call_if_eq VAR_MAP_SCENE_CINNABAR_ISLAND, 3, CinnabarIsland_EventScript_ReadyObjectsReturnFromSeviiIslands
	call_if_eq VAR_MAP_SCENE_CINNABAR_ISLAND_2, 1, CinnabarIsland_EventScript_ReadyObjectsSailToOneIslandFromPokeCenter
	end

CinnabarIsland_EventScript_ReadyObjectsSailToOneIslandFromPokeCenter::
	savebgm MUS_FOLLOW_ME
	setflag FLAG_TEMP_2
	setobjectxyperm LOCALID_CINNABAR_BILL, 15, 12
	setobjectmovementtype LOCALID_CINNABAR_BILL, MOVEMENT_TYPE_FACE_LEFT
	setobjectxyperm LOCALID_CINNABAR_SEAGALLOP, 30, 12
	return

CinnabarIsland_EventScript_ReadyObjectsSailToOneIsland::
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_ge VAR_0x8004, 18, CinnabarIsland_EventScript_MoveSeagallopDown
	setflag FLAG_TEMP_2
	setobjectxyperm LOCALID_CINNABAR_BILL, 18, 12
	setobjectmovementtype LOCALID_CINNABAR_BILL, MOVEMENT_TYPE_FACE_UP
	setobjectxyperm LOCALID_CINNABAR_SEAGALLOP, 30, 12
	return

CinnabarIsland_EventScript_MoveSeagallopDown::
	setobjectxyperm LOCALID_CINNABAR_SEAGALLOP, 30, 8
	return

CinnabarIsland_EventScript_ReadyObjectsReturnFromSeviiIslands::
	setobjectxyperm LOCALID_CINNABAR_BILL, 21, 8
	setobjectmovementtype LOCALID_CINNABAR_BILL, MOVEMENT_TYPE_FACE_UP
	return

CinnabarIsland_EventScript_CheckUnlockGym::
	goto_if_set FLAG_HIDE_POKEMON_MANSION_B1F_SECRET_KEY, CinnabarIsland_EventScript_UnlockGym
	return

CinnabarIsland_EventScript_UnlockGym::
	setvar VAR_TEMP_1, 1
	return

CinnabarIsland_OnFrame::
	map_script_2 VAR_MAP_SCENE_CINNABAR_ISLAND_2, 1, CinnabarIsland_EventScript_ExitPokeCenterForOneIsland
	map_script_2 VAR_MAP_SCENE_CINNABAR_ISLAND, 1, CinnabarIsland_EventScript_BillScene
	map_script_2 VAR_MAP_SCENE_CINNABAR_ISLAND, 3, CinnabarIsland_EventScript_ReturnFromSeviiIslands
	.2byte 0

CinnabarIsland_EventScript_ExitPokeCenterForOneIsland::
	lockall
	clearflag FLAG_DONT_TRANSITION_MUSIC
	savebgm MUS_DUMMY
	textcolor NPC_TEXT_COLOR_MALE
	setvar VAR_MAP_SCENE_CINNABAR_ISLAND_2, 2
	delay 20
	call CinnabarIsland_EventScript_SailToOneIsland
	releaseall
	end

CinnabarIsland_EventScript_ReturnFromSeviiIslands::
	lockall
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CinnabarIsland_Text_IfYouHaveTriPassYouCanGoAgain
	closemessage
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillExit
	waitmovement 0
	removeobject LOCALID_CINNABAR_BILL
	setvar VAR_MAP_SCENE_CINNABAR_ISLAND, 4
	setflag FLAG_HIDE_TWO_ISLAND_GAME_CORNER_LOSTELLE
	clearflag FLAG_HIDE_LOSTELLE_IN_HER_HOME
	releaseall
	end

CinnabarIsland_Movement_BillExit::
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

CinnabarIsland_EventScript_BillScene::
	lockall
	textcolor NPC_TEXT_COLOR_MALE
	call_if_unset FLAG_TEMP_2, CinnabarIsland_EventScript_BillFacePlayer1
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_BillFacePlayer2
	playse SE_PIN
	applymovement LOCALID_CINNABAR_BILL, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_CINNABAR_BILL, Common_Movement_Delay48
	waitmovement 0
	call_if_unset FLAG_TEMP_2, CinnabarIsland_EventScript_BillApproachPlayer1
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_BillApproachPlayer2
	msgbox CinnabarIsland_Text_HeyIfItIsntPlayer
	msgbox CinnabarIsland_Text_ComeWithMeToOneIsland, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, CinnabarIsland_EventScript_AgreeSailToOneIsland
	goto_if_eq VAR_RESULT, NO, CinnabarIsland_EventScript_DeclineSailToOneIsland
	end

CinnabarIsland_EventScript_BillFacePlayer1::
	applymovement LOCALID_CINNABAR_BILL, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	return

CinnabarIsland_EventScript_BillFacePlayer2::
	applymovement LOCALID_CINNABAR_BILL, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	return

CinnabarIsland_EventScript_BillApproachPlayer1::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillApproachPlayer1
	waitmovement 0
	return

CinnabarIsland_EventScript_BillApproachPlayer2::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillApproachPlayer2
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	return

CinnabarIsland_EventScript_AgreeSailToOneIsland::
	msgbox CinnabarIsland_Text_AllRightLetsGo
	closemessage
	call CinnabarIsland_EventScript_SailToOneIsland
	releaseall
	end

CinnabarIsland_EventScript_DeclineSailToOneIsland::
	msgbox CinnabarIsland_Text_IllBeWaitingInPokeCenter
	closemessage
	call_if_unset FLAG_TEMP_2, CinnabarIsland_EventScript_BillExitToPokeCenter
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_BillReturnToPokeCenter
	removeobject LOCALID_CINNABAR_BILL
	setvar VAR_MAP_SCENE_CINNABAR_ISLAND, 2
	clearflag FLAG_HIDE_CINNABAR_POKECENTER_BILL
	releaseall
	end

CinnabarIsland_EventScript_BillExitToPokeCenter::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillExitToPokeCenter
	waitmovement 0
	return

CinnabarIsland_Movement_BillExitToPokeCenter::
	walk_right
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

CinnabarIsland_EventScript_BillReturnToPokeCenter::
	applymovement LOCALID_PLAYER, CinnabarIsland_Movement_PlayerWatchBillExit
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillApproachDoor
	waitmovement 0
	opendoor 14, 11
	waitdooranim
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillReEnterPokeCenter
	waitmovement 0
	closedoor 14, 11
	waitdooranim
	return

CinnabarIsland_Movement_PlayerWatchBillExit::
	walk_left
	walk_in_place_faster_right
	step_end

CinnabarIsland_Movement_BillApproachDoor::
	delay_16
	walk_left
	walk_in_place_faster_up
	step_end

CinnabarIsland_Movement_BillReEnterPokeCenter::
	walk_up
	delay_4
	set_invisible
	step_end

@ Can be triggered outside, or after talking to Bill in the poke center
CinnabarIsland_EventScript_SailToOneIsland::
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_ApproachShore
	addobject LOCALID_CINNABAR_SEAGALLOP
	call_if_unset FLAG_TEMP_2, CinnabarIsland_EventScript_BoatArrive
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_BoatArriveExitedPokeCenter
	msgbox CinnabarIsland_Text_MyPalsBoatArrived
	closemessage
	call_if_unset FLAG_TEMP_2, CinnabarIsland_EventScript_BoardBoat
	call_if_set FLAG_TEMP_2, CinnabarIsland_EventScript_BoardBoatExitedPokeCenter
	setvar VAR_MAP_SCENE_CINNABAR_ISLAND, 2
	removeobject LOCALID_CINNABAR_BILL
	delay 40
	setflag FLAG_HIDE_CINNABAR_SEAGALLOP
	setvar VAR_MAP_SCENE_ONE_ISLAND_HARBOR, 1
	setvar VAR_0x8004, SEAGALLOP_CINNABAR_ISLAND
	setvar VAR_0x8006, SEAGALLOP_ONE_ISLAND
	goto EventScript_SetSail
	end

CinnabarIsland_EventScript_ApproachShore::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_ApproachShore
	applymovement LOCALID_PLAYER, CinnabarIsland_Movement_ApproachShore
	waitmovement 0
	return

CinnabarIsland_EventScript_BoatArrive::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillFaceBoat
	applymovement LOCALID_CINNABAR_SEAGALLOP, CinnabarIsland_Movement_BoatArrive
	waitmovement 0
	return

CinnabarIsland_EventScript_BoatArriveExitedPokeCenter::
	applymovement LOCALID_CINNABAR_SEAGALLOP, CinnabarIsland_Movement_BoatArrive
	waitmovement 0
	return

CinnabarIsland_EventScript_BoardBoat::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillBoardBoat
	applymovement LOCALID_PLAYER, CinnabarIsland_Movement_PlayerBoardBoat
	waitmovement 0
	return

CinnabarIsland_EventScript_BoardBoatExitedPokeCenter::
	applymovement LOCALID_CINNABAR_BILL, CinnabarIsland_Movement_BillBoardBoatFromShore
	applymovement LOCALID_PLAYER, CinnabarIsland_Movement_PlayerBoardBoatFromShore
	waitmovement 0
	return

CinnabarIsland_Movement_BoatArrive::
	delay_16
	delay_16
	walk_fast_left
	walk_fast_left
	walk_left
	walk_slower_left
	walk_slower_left
	step_end

CinnabarIsland_Movement_BillBoardBoat::
	walk_right
	walk_down
	walk_down
	walk_right
	delay_4
	set_invisible
	step_end

CinnabarIsland_Movement_BillApproachPlayer1::
	walk_up
	step_end

CinnabarIsland_Movement_BillApproachPlayer2::
	walk_left
	walk_left
	walk_left
	step_end

CinnabarIsland_Movement_BillFaceBoat::
	delay_16
	delay_16
	delay_8
	walk_in_place_faster_right
	step_end

CinnabarIsland_Movement_ApproachShore::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

CinnabarIsland_Movement_BillBoardBoatFromShore::
	walk_right
	delay_4
	set_invisible
	step_end

CinnabarIsland_Movement_PlayerBoardBoat::
	walk_down
	walk_right
	walk_down
	walk_down
	walk_in_place_faster_right
	delay_4
	walk_right
	delay_4
	set_invisible
	step_end

CinnabarIsland_Movement_PlayerBoardBoatFromShore::
	walk_right
	delay_4
	walk_right
	delay_4
	set_invisible
	step_end

@ Triggered when VAR_TEMP_1 is 0
CinnabarIsland_EventScript_GymDoorLocked::
	lockall
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	delay 20
	msgbox CinnabarIsland_Text_DoorIsLocked
	closemessage
	applymovement LOCALID_PLAYER, CinnabarIsland_Movement_ForcePlayerFromDoor
	waitmovement 0
	releaseall
	end

CinnabarIsland_Movement_ForcePlayerFromDoor::
	walk_down
	step_end

CinnabarIsland_EventScript_Woman::
	lock
	faceplayer
	famechecker FAMECHECKER_BLAINE, 3
	msgbox CinnabarIsland_Text_BlaineLivedHereSinceBeforeLab
	release
	end

CinnabarIsland_EventScript_OldMan::
	msgbox CinnabarIsland_Text_ScientistsExperimentInMansion, MSGBOX_NPC
	end

CinnabarIsland_EventScript_IslandSign::
	msgbox CinnabarIsland_Text_IslandSign, MSGBOX_SIGN
	end

CinnabarIsland_EventScript_PokemonLabSign::
	msgbox CinnabarIsland_Text_PokemonLab, MSGBOX_SIGN
	end

CinnabarIsland_EventScript_GymSign::
	lockall
	famechecker FAMECHECKER_BLAINE, 0
	msgbox CinnabarIsland_Text_GymSign
	releaseall
	end

@ Thunder Yellow v0.5.0, TEAM ROCKET event 8: after the MARSH BADGE, the trio are at
@ the POKéMON MANSION's door with a machine to lure the fire POKéMON of the
@ volcano. A double battle; afterwards the machine they drop draws out a furious
@ MAGMAR, which the player can battle and catch, once.
CinnabarIsland_EventScript_ReadyRocketMagmar::
	setflag FLAG_TEMP_3
	goto_if_set FLAG_ROCKET_CINNABAR, EventScript_Return
	goto_if_unset FLAG_BADGE06_GET, EventScript_Return
	clearflag FLAG_TEMP_3
	setvar VAR_TEMP_2, 1
	return

CinnabarIsland_EventScript_RocketMagmar::
	lockall
	setvar VAR_TEMP_2, 0
	goto_if_eq VAR_ROCKET_RETRY, 10, CinnabarIsland_EventScript_RocketMagmarRetry
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox CinnabarIsland_Text_JessieMagmarCaller
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CinnabarIsland_Text_JamesFireArmy
	closemessage
	applymovement LOCALID_CINNABAR_JESSIE, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_CINNABAR_MEOWTH, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_CINNABAR_JAMES, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	applymovement LOCALID_CINNABAR_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CinnabarIsland_Text_MeowthTwerpAgain
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox CinnabarIsland_Text_RocketMagmarIntro
	closemessage
CinnabarIsland_EventScript_RocketMagmarBattle::
	setvar VAR_0x8004, 10
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_CINNABAR_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_CINNABAR, CinnabarIsland_Text_RocketMagmarDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	setvar VAR_0x8008, LOCALID_CINNABAR_JESSIE
	setvar VAR_0x8009, LOCALID_CINNABAR_JAMES
	setvar VAR_0x800A, LOCALID_CINNABAR_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_CINNABAR_JESSIE
	removeobject LOCALID_CINNABAR_MEOWTH
	removeobject LOCALID_CINNABAR_JAMES
	setflag FLAG_ROCKET_CINNABAR
	addmoney 1600
	setvar VAR_0x8004, 1600
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, CinnabarIsland_EventScript_RocketCoins
	addmoney 1600
	setvar VAR_0x8004, 3200
CinnabarIsland_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	msgbox CinnabarIsland_Text_FossilInLoot
	call CinnabarIsland_EventScript_RocketFossil
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox CinnabarIsland_Text_CallerStillBuzzing
	closemessage
	setvar VAR_0x8004, 2
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 3
	special ShakeScreen
	waitstate
	playmoncry SPECIES_MAGMAR, CRY_MODE_ENCOUNTER
	waitmoncry
	msgbox CinnabarIsland_Text_MagmarBurstsOut
	closemessage
	setwildbattle SPECIES_MAGMAR, 45
	dowildbattle
	fadedefaultbgm
	msgbox CinnabarIsland_Text_CallerFallsSilent
	releaseall
	end

CinnabarIsland_EventScript_RocketMagmarRetry::
	applymovement LOCALID_CINNABAR_JESSIE, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_CINNABAR_MEOWTH, Common_Movement_WalkInPlaceFasterDown
	applymovement LOCALID_CINNABAR_JAMES, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	call EventScript_RocketTrioRetry
	goto CinnabarIsland_EventScript_RocketMagmarBattle

@ v0.9.0: the trio stole a FOSSIL from the LAB. The player gets the one not
@ picked at MT. MOON. With neither picked yet there is no telling which to
@ give (and giving one could leave two of a kind and no KABUTO ever), so the
@ OFFICER at the VIRIDIAN POKéMON CENTER keeps it until the player has picked.
CinnabarIsland_EventScript_RocketFossil::
	goto_if_unset FLAG_GOT_FOSSIL_FROM_MT_MOON, CinnabarIsland_EventScript_RocketFossilToOfficer
	goto_if_set FLAG_GOT_DOME_FOSSIL, CinnabarIsland_EventScript_RocketHelixFossil
	goto_if_set FLAG_GOT_HELIX_FOSSIL, CinnabarIsland_EventScript_RocketDomeFossil
CinnabarIsland_EventScript_RocketFossilToOfficer::
	msgbox CinnabarIsland_Text_FossilToOfficer
	return

CinnabarIsland_EventScript_RocketHelixFossil::
	giveitem ITEM_HELIX_FOSSIL
	goto_if_eq VAR_0x8007, FALSE, CinnabarIsland_EventScript_RocketFossilHeld
	setflag FLAG_GOT_HELIX_FOSSIL
	goto CinnabarIsland_EventScript_RocketFossilGiven

CinnabarIsland_EventScript_RocketDomeFossil::
	giveitem ITEM_DOME_FOSSIL
	goto_if_eq VAR_0x8007, FALSE, CinnabarIsland_EventScript_RocketFossilHeld
	setflag FLAG_GOT_DOME_FOSSIL
CinnabarIsland_EventScript_RocketFossilGiven::
	setvar VAR_0x8004, ROCKET_BONUS_FOSSIL
	special SetRocketRewardBit
	return

CinnabarIsland_EventScript_RocketFossilHeld::
	setvar VAR_0x8004, ROCKET_BONUS_FOSSIL
	goto EventScript_RocketRewardHeld

