@ v0.11.0 E4/E5 (docs/v0.11.0-plan.md 4.4-4.5): NORMAN waits in the lobby
@ (no battle before v0.12.0). The first talk brings WALLY in; the catching
@ demo plays on ROUTE 102 (Route102_EventScript_WallyDemo) and the scene ends
@ back here, in the lobby, on this map's frame script. VAR_HOENN_SCENE_WALLY:
@ 0 before, 1 while the scene runs, 2 after.
.equ LOCALID_PETALBURG_GYM_WALLY, 9

PetalburgCity_Gym_OnTransition::
	special HoennZ3_SetupObjects
	end

PetalburgCity_Gym_OnFrame::
	map_script_2 VAR_HOENN_SCENE_WALLY, 1, PetalburgCity_Gym_EventScript_WallyBack
	.2byte 0

PetalburgCity_Gym_EventScript_Norman::
	lock
	faceplayer
	checktrainerflag TRAINER_HOENN_NORMAN_1
	goto_if TRUE, PetalburgCity_Gym_EventScript_DefeatedNorman
	goto_if_eq VAR_HOENN_SCENE_WALLY, 0, PetalburgCity_Gym_EventScript_NormanFirst
	goto_if_eq VAR_HOENN_SCENE_WALLY, 1, PetalburgCity_Gym_EventScript_NormanWallyWaiting
	specialvar VAR_RESULT, CountHoennBadges
	goto_if_ge VAR_RESULT, 4, PetalburgCity_Gym_EventScript_NormanBattle
	msgbox PetalburgCity_Gym_Text_NormanAfter
	call PetalburgCity_Gym_EventScript_NormanBadges
	release
	end

PetalburgCity_Gym_EventScript_NormanBadges::
	specialvar VAR_RESULT, CountHoennBadges
	goto_if_ge VAR_RESULT, 4, PetalburgCity_Gym_EventScript_NormanBadgesReady
	switch VAR_RESULT
	case 0, PetalburgCity_Gym_EventScript_NormanBadges0
	case 1, PetalburgCity_Gym_EventScript_NormanBadges1
	case 2, PetalburgCity_Gym_EventScript_NormanBadges2
	msgbox PetalburgCity_Gym_Text_NormanBadges3
	return

PetalburgCity_Gym_EventScript_NormanBadges0::
	msgbox PetalburgCity_Gym_Text_NormanBadges0
	return

PetalburgCity_Gym_EventScript_NormanBadges1::
	msgbox PetalburgCity_Gym_Text_NormanBadges1
	return

PetalburgCity_Gym_EventScript_NormanBadges2::
	msgbox PetalburgCity_Gym_Text_NormanBadges2
	return

PetalburgCity_Gym_EventScript_NormanPikachu::
	msgbox PetalburgCity_Gym_Text_NormanPikachu
	return

PetalburgCity_Gym_EventScript_WallyPikachu::
	msgbox PetalburgCity_Gym_Text_WallyPikachu
	return

PetalburgCity_Gym_EventScript_NormanFirst::
	msgbox PetalburgCity_Gym_Text_NormanFirst
	call PetalburgCity_Gym_EventScript_NormanBadges
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	copyvar VAR_0x8008, VAR_RESULT
	call_if_ne VAR_0x8008, PARTY_SIZE, PetalburgCity_Gym_EventScript_NormanPikachu
	closemessage
	playbgm MUS_RS_FOLLOW_ME, FALSE
	clearflag FLAG_HIDE_HOENN_WALLY_PETALBURG
	addobject LOCALID_PETALBURG_GYM_WALLY
	applymovement LOCALID_PETALBURG_GYM_WALLY, PetalburgCity_Gym_Movement_WallyEnters
	waitmovement 0
	msgbox PetalburgCity_Gym_Text_WallyExcuseMe
	msgbox PetalburgCity_Gym_Text_NormanHelloWally
	msgbox PetalburgCity_Gym_Text_WallyWantsPokemon
	msgbox PetalburgCity_Gym_Text_NormanLendsZigzagoon
	call_if_ne VAR_0x8008, PARTY_SIZE, PetalburgCity_Gym_EventScript_WallyPikachu
	closemessage
	setvar VAR_HOENN_SCENE_WALLY, 1
	fadescreen FADE_TO_BLACK
	warp MAP_ROUTE102, 11, 5
	waitstate
	release
	end

@ Back from ROUTE 102 with the RALTS: WALLY thanks the player and leaves
@ for VERDANTURF. (With VAR 1 and no RALTS, the demo is played again.)
PetalburgCity_Gym_EventScript_WallyBack::
	lockall
	goto_if_unset FLAG_HOENN_WALLY_CAUGHT_RALTS, PetalburgCity_Gym_EventScript_WallyDemoAgain
	playbgm MUS_RS_FOLLOW_ME, FALSE
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	msgbox PetalburgCity_Gym_Text_WallyThanks
	closemessage
	setvar VAR_HOENN_SCENE_WALLY, 2
	applymovement LOCALID_PETALBURG_GYM_WALLY, PetalburgCity_Gym_Movement_WallyLeaves
	waitmovement 0
	playse SE_EXIT
	removeobject LOCALID_PETALBURG_GYM_WALLY
	setflag FLAG_HIDE_HOENN_WALLY_PETALBURG
	clearflag FLAG_HIDE_HOENN_WALLY_VERDANTURF
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

PetalburgCity_Gym_EventScript_WallyDemoAgain::
	fadescreen FADE_TO_BLACK
	warp MAP_ROUTE102, 11, 5
	waitstate
	releaseall
	end

@ From the door (4,110) up to the player's side
PetalburgCity_Gym_Movement_WallyEnters:
	walk_up
	walk_in_place_faster_up
	step_end

PetalburgCity_Gym_Movement_WallyLeaves:
	walk_down
	step_end

PetalburgCity_Gym_EventScript_NormanWallyWaiting::
	msgbox PetalburgCity_Gym_Text_NormanWallyWaiting
	release
	end

PetalburgCity_Gym_EventScript_NormanBadgesReady::
	msgbox PetalburgCity_Gym_Text_NormanBadgesReady
	return

PetalburgCity_Gym_EventScript_NormanBattle::
	trainerbattle_single TRAINER_HOENN_NORMAN_1, PetalburgCity_Gym_Text_NormanBattleIntro, PetalburgCity_Gym_Text_NormanDefeat, PetalburgCity_Gym_EventScript_DefeatedNorman, NO_MUSIC
	goto PetalburgCity_Gym_EventScript_DefeatedNorman
	end

PetalburgCity_Gym_EventScript_DefeatedNorman::
	goto_if_set FLAG_HOENN_BADGE05_GET, PetalburgCity_Gym_EventScript_NormanCheckTM42
	setflag FLAG_HOENN_BADGE05_GET
	msgbox PetalburgCity_Gym_Text_ReceivedBalanceBadge
PetalburgCity_Gym_EventScript_NormanCheckTM42::
	goto_if_set FLAG_HOENN_GOT_TM42_FROM_NORMAN, PetalburgCity_Gym_EventScript_NormanPostBattle
	msgbox PetalburgCity_Gym_Text_NormanTakeTM42
	additem ITEM_TM42
	goto_if_eq VAR_RESULT, FALSE, PetalburgCity_Gym_EventScript_NormanNoRoom
	setflag FLAG_HOENN_GOT_TM42_FROM_NORMAN
	msgreceiveditem PetalburgCity_Gym_Text_ReceivedTM42, ITEM_TM42
	msgbox PetalburgCity_Gym_Text_NormanExplainTM42
	goto PetalburgCity_Gym_EventScript_NormanPostBattle
	end

PetalburgCity_Gym_EventScript_NormanNoRoom::
	msgbox PetalburgCity_Gym_Text_NormanNoRoom
	release
	end

PetalburgCity_Gym_EventScript_NormanPostBattle::
	msgbox PetalburgCity_Gym_Text_NormanPostBattle
	release
	end
