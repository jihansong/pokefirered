@ v0.11.0 E1 (docs/v0.11.0-plan.md 4.1): PROF. BIRCH chased by a POOCHYENA.
@ Both ends of the route start it: the south end as in Emerald, the north end
@ for players coming down from OLDALE. BIRCH and the POOCHYENA wait on the
@ ledge at (9,13) and (10,13) and are moved off it first, as Emerald's script
@ does. MUS_HELP plays from the shout until BIRCH has gone.
.equ LOCALID_ROUTE101_BIRCH, 2
.equ LOCALID_ROUTE101_POOCHYENA, 3

Route101_OnTransition::
	special HoennZ3_SetupObjects
	end

Route101_EventScript_BirchRescueSouth::
	lockall
	playbgm MUS_HELP, TRUE
	msgbox Route101_Text_BirchHelp
	closemessage
	setvar VAR_0x8009, 0
	setobjectxyperm LOCALID_ROUTE101_BIRCH, 0, 15
	setobjectxyperm LOCALID_ROUTE101_POOCHYENA, 0, 16
	call Route101_EventScript_PlaceChase
	setobjectxy LOCALID_ROUTE101_BIRCH, 0, 15
	setobjectxy LOCALID_ROUTE101_POOCHYENA, 0, 16
	applymovement LOCALID_PLAYER, Route101_Movement_PlayerEnterSouth
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchRunAwaySouth
	applymovement LOCALID_ROUTE101_POOCHYENA, Route101_Movement_PoochyenaChaseSouth
	waitmovement 0
	applymovement LOCALID_ROUTE101_POOCHYENA, Route101_Movement_PoochyenaCirclesSouth
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchCirclesSouth
	waitmovement 0
	goto Route101_EventScript_BirchRescue
	end

@ From OLDALE: the player comes down two steps and BIRCH runs round in the
@ open ground to the west, (4,2)-(7,4)
Route101_EventScript_BirchRescueNorth::
	lockall
	playbgm MUS_HELP, TRUE
	msgbox Route101_Text_BirchHelp
	closemessage
	setvar VAR_0x8009, 1
	setobjectxyperm LOCALID_ROUTE101_BIRCH, 2, 4
	setobjectxyperm LOCALID_ROUTE101_POOCHYENA, 2, 5
	call Route101_EventScript_PlaceChase
	setobjectxy LOCALID_ROUTE101_BIRCH, 2, 4
	setobjectxy LOCALID_ROUTE101_POOCHYENA, 2, 5
	applymovement LOCALID_PLAYER, Route101_Movement_PlayerEnterNorth
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchRunAwayNorth
	applymovement LOCALID_ROUTE101_POOCHYENA, Route101_Movement_PoochyenaChaseNorth
	waitmovement 0
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchCirclesNorth
	applymovement LOCALID_ROUTE101_POOCHYENA, Route101_Movement_PoochyenaCirclesNorth
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	goto Route101_EventScript_BirchRescue
	end

@ The rescue is recorded before the battle: if the player loses (a whited-out
@ party of weak POKéMON), BIRCH got away by himself (plan 4.1) and is waiting
@ in the LAB, so nothing is left half done.
Route101_EventScript_BirchRescue::
	applymovement LOCALID_ROUTE101_BIRCH, Common_Movement_WalkInPlaceFasterRight
	applymovement LOCALID_ROUTE101_POOCHYENA, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	msgbox Route101_Text_BirchStillChased
	setflag FLAG_HOENN_BIRCH_RESCUED
	setvar VAR_HOENN_SCENE_BIRCH, 1
	setflag FLAG_HIDE_HOENN_BIRCH_ROUTE101
	clearflag FLAG_HIDE_HOENN_BIRCH_LAB
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	copyvar VAR_0x8008, VAR_RESULT
	call_if_ne VAR_0x8008, PARTY_SIZE, Route101_EventScript_PikachuJumpsIn
	call_if_eq VAR_0x8008, PARTY_SIZE, Route101_EventScript_PlayerStepsIn
	setwildbattle SPECIES_POOCHYENA, 5
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	call_if_eq VAR_RESULT, B_OUTCOME_RAN, Route101_EventScript_PoochyenaWandersOff
	call_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, Route101_EventScript_PoochyenaWandersOff
	removeobject LOCALID_ROUTE101_POOCHYENA
	applymovement LOCALID_ROUTE101_BIRCH, Common_Movement_FacePlayer
	waitmovement 0
	msgbox Route101_Text_BirchThanks
	call_if_ne VAR_0x8008, PARTY_SIZE, Route101_EventScript_BirchPikachu
	msgbox Route101_Text_BirchComeToLab
	closemessage
	call_if_eq VAR_0x8009, 0, Route101_EventScript_BirchLeavesSouth
	call_if_eq VAR_0x8009, 1, Route101_EventScript_BirchLeavesNorth
	removeobject LOCALID_ROUTE101_BIRCH
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

@ Off towards LITTLEROOT: down the open ground in the south, along the
@ path's west edge in the north
Route101_EventScript_BirchLeavesSouth::
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchLeavesSouth
	waitmovement 0
	return

Route101_EventScript_BirchLeavesNorth::
	applymovement LOCALID_ROUTE101_BIRCH, Route101_Movement_BirchLeavesNorth
	waitmovement 0
	return

@ From the north the pair on the ledge are out of sight and not spawned yet:
@ addobject puts them where their templates now say. Seen from the south they
@ are already out; addobject leaves them be and setobjectxy moves them.
Route101_EventScript_PlaceChase::
	addobject LOCALID_ROUTE101_BIRCH
	addobject LOCALID_ROUTE101_POOCHYENA
	return

Route101_EventScript_PikachuJumpsIn::
	msgbox Route101_Text_PikachuJumpsIn
	return

Route101_EventScript_PlayerStepsIn::
	msgbox Route101_Text_PlayerStepsIn
	return

Route101_EventScript_PoochyenaWandersOff::
	msgbox Route101_Text_PoochyenaWandersOff
	return

Route101_EventScript_BirchPikachu::
	msgbox Route101_Text_BirchPikachu
	return

Route101_Movement_PlayerEnterSouth:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_in_place_faster_left
	step_end

Route101_Movement_BirchRunAwaySouth:
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_up
	walk_fast_up
	step_end

Route101_Movement_PoochyenaChaseSouth:
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_up
	step_end

@ Emerald's chase: BIRCH from (4,13) round (4,10)-(7,12), ending at (4,12);
@ the POOCHYENA one step behind, ending at (5,12)
Route101_Movement_BirchCirclesSouth:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

Route101_Movement_PoochyenaCirclesSouth:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	step_end

Route101_Movement_PlayerEnterNorth:
	walk_down
	walk_down
	step_end

Route101_Movement_BirchRunAwayNorth:
	walk_fast_right
	walk_fast_right
	step_end

Route101_Movement_PoochyenaChaseNorth:
	walk_fast_right
	walk_fast_up
	step_end

@ BIRCH (4,4) -> up to (4,2) -> right to (7,2) -> down to (7,4) -> back to
@ (4,4), twice; the POOCHYENA one step behind, ending at (5,4)
Route101_Movement_BirchCirclesNorth:
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end

Route101_Movement_PoochyenaCirclesNorth:
	walk_fast_right
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_down
	walk_fast_down
	walk_fast_left
	walk_fast_left
	step_end

Route101_Movement_BirchLeavesSouth:
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

Route101_Movement_BirchLeavesNorth:
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	walk_fast_left
	step_end
