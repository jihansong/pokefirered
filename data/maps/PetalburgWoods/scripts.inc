PetalburgWoods_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PetalburgWoods_OnTransition
	.byte 0

PetalburgWoods_EventScript_HItem94::
	finditem ITEM_GREAT_BALL
	end

PetalburgWoods_EventScript_HItem95::
	finditem ITEM_X_ATTACK
	end

PetalburgWoods_EventScript_HItem96::
	finditem ITEM_ETHER
	end

PetalburgWoods_EventScript_H0::
	msgbox PetalburgWoods_Text_H0, MSGBOX_NPC
	end

PetalburgWoods_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_LYLE, PetalburgWoods_Text_H1_0, PetalburgWoods_Text_H1_1
	msgbox PetalburgWoods_Text_H1_2, MSGBOX_AUTOCLOSE
	end

PetalburgWoods_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_JAMES_1, PetalburgWoods_Text_H2_0, PetalburgWoods_Text_H2_1
	msgbox PetalburgWoods_Text_H2_2, MSGBOX_AUTOCLOSE
	end

PetalburgWoods_EventScript_H3::
	msgbox PetalburgWoods_Text_H3, MSGBOX_NPC
	end

PetalburgWoods_EventScript_HItem97::
	finditem ITEM_PARALYZE_HEAL
	end

PetalburgWoods_EventScript_H5::
	msgbox PetalburgWoods_Text_H5, MSGBOX_SIGN
	end

PetalburgWoods_EventScript_H6::
	msgbox PetalburgWoods_Text_H6, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ v0.11.0 E6 (docs/v0.11.0-plan.md 4.6, 5.3): a DEVON researcher chased by a
@ TEAM AQUA grunt; after the grunt, JESSIE & JAMES (TEAM ROCKET #15, a double
@ battle with the v0.9.0 shared motto, retry, coins and reward scripts); then
@ the researcher's GREAT BALL. TREECKO waits at the big tree once the woods
@ are quiet again (the grunt beaten).
@ Losing to the grunt whites out with nothing changed: the scene is there
@ again. Losing to the trio leaves them in the grass (the grunt's defeat is
@ what shows them): talking to any of them is the short retry.
.equ LOCALID_WOODS_GRUNT, 10
.equ LOCALID_WOODS_RESEARCHER, 11
.equ LOCALID_WOODS_JESSIE, 12
.equ LOCALID_WOODS_JAMES, 13
.equ LOCALID_WOODS_MEOWTH, 14
.equ ROCKET_EVENT_WOODS, 15

PetalburgWoods_OnTransition::
	special HoennZ3_SetupObjects
	end

@ ---------------------------------------------------------------- E6
@ (26,23)/(27,23) while VAR_HOENN_SCENE_DEVON = 0. Once the grunt is beaten
@ (the researcher's BAG-full wait, or the trio still to beat) nothing happens.
PetalburgWoods_EventScript_ResearcherHelp::
	goto_if_defeated TRAINER_HOENN_GRUNT_PETALBURG_WOODS, PetalburgWoods_EventScript_SceneDone
	lockall
	applymovement LOCALID_WOODS_RESEARCHER, PetalburgWoods_Movement_ResearcherRunsDown
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	msgbox PetalburgWoods_Text_ResearcherHelp
	closemessage
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	applymovement LOCALID_WOODS_GRUNT, PetalburgWoods_Movement_GruntComesDown
	waitmovement 0
	msgbox PetalburgWoods_Text_GruntHandThemOver
	msgbox PetalburgWoods_Text_GruntIntro
	closemessage
	trainerbattle_no_intro TRAINER_HOENN_GRUNT_PETALBURG_WOODS, PetalburgWoods_Text_GruntDefeat
	goto_if_set FLAG_HOENN_ROCKET_WOODS, PetalburgWoods_EventScript_GruntLeaves
	msgbox PetalburgWoods_Text_JessieHoldIt
	closemessage
	clearflag FLAG_HIDE_HOENN_ROCKET_WOODS
	addobject LOCALID_WOODS_JESSIE
	addobject LOCALID_WOODS_JAMES
	addobject LOCALID_WOODS_MEOWTH
	applymovement LOCALID_WOODS_JESSIE, PetalburgWoods_Movement_JessieComes
	applymovement LOCALID_WOODS_JAMES, PetalburgWoods_Movement_JamesComes
	applymovement LOCALID_WOODS_MEOWTH, PetalburgWoods_Movement_MeowthComes
	waitmovement 0
	call EventScript_RocketTrioMotto
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	textcolor NPC_TEXT_COLOR_NEUTRAL
	call_if_ne VAR_RESULT, PARTY_SIZE, PetalburgWoods_EventScript_RocketFollowed
	call_if_eq VAR_RESULT, PARTY_SIZE, PetalburgWoods_EventScript_RocketFollowedNoPikachu
	msgbox PetalburgWoods_Text_GruntSlipsAway
	closemessage
	applymovement LOCALID_WOODS_GRUNT, PetalburgWoods_Movement_GruntRunsOff
	waitmovement 0
	removeobject LOCALID_WOODS_GRUNT
	goto PetalburgWoods_EventScript_RocketBattle

PetalburgWoods_EventScript_SceneDone::
	end

PetalburgWoods_EventScript_GruntLeaves::
	applymovement LOCALID_WOODS_GRUNT, PetalburgWoods_Movement_GruntRunsOff
	waitmovement 0
	removeobject LOCALID_WOODS_GRUNT
	fadedefaultbgm
	goto PetalburgWoods_EventScript_ResearcherReward

PetalburgWoods_EventScript_RocketFollowed::
	msgbox PetalburgWoods_Text_RocketFollowed
	return

PetalburgWoods_EventScript_RocketFollowedNoPikachu::
	msgbox PetalburgWoods_Text_RocketFollowedNoPikachu
	return

@ Talking to JESSIE, JAMES or MEOWTH after losing to them
PetalburgWoods_EventScript_Jessie::
PetalburgWoods_EventScript_James::
PetalburgWoods_EventScript_Meowth::
	lockall
	playbgm MUS_ENCOUNTER_ROCKET, FALSE
	call EventScript_RocketTrioRetry
PetalburgWoods_EventScript_RocketBattle::
	setvar VAR_0x8004, ROCKET_EVENT_WOODS
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_WOODS_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_PETALBURG_WOODS, PetalburgWoods_Text_RocketDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PetalburgWoods_Text_RocketBlastOff
	setvar VAR_0x8008, LOCALID_WOODS_JESSIE
	setvar VAR_0x8009, LOCALID_WOODS_JAMES
	setvar VAR_0x800A, LOCALID_WOODS_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_WOODS_JESSIE
	removeobject LOCALID_WOODS_JAMES
	removeobject LOCALID_WOODS_MEOWTH
	setflag FLAG_HOENN_ROCKET_WOODS
	fadedefaultbgm
	@ MEOWTH 67: 8 x 67 for each of the five POKéMON after the first, and the
	@ half of the prize a single battle loses (4,288 / 2) when it was one
	setvar VAR_0x8004, 2680
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, PetalburgWoods_EventScript_RocketCoins
	setvar VAR_0x8004, 4824
PetalburgWoods_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox PetalburgWoods_Text_SilverPowderDropped
	giveitem ITEM_SILVER_POWDER
	setvar VAR_0x8004, ROCKET_BONUS_SILVER_POWDER
	call EventScript_RocketRewardResult
	goto_if_eq VAR_HOENN_SCENE_DEVON, 0, PetalburgWoods_EventScript_ResearcherReward
	releaseall
	end

@ The researcher: his plea until the woods are clear, then the GREAT BALL.
@ A full BAG leaves him waiting (VAR_HOENN_SCENE_DEVON stays 0).
PetalburgWoods_EventScript_Researcher::
	lock
	faceplayer
	goto_if_not_defeated TRAINER_HOENN_GRUNT_PETALBURG_WOODS, PetalburgWoods_EventScript_ResearcherStillScared
	goto_if_unset FLAG_HOENN_ROCKET_WOODS, PetalburgWoods_EventScript_ResearcherStillScared
PetalburgWoods_EventScript_ResearcherReward::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox PetalburgWoods_Text_ResearcherThanks
	giveitem ITEM_GREAT_BALL
	goto_if_eq VAR_RESULT, FALSE, PetalburgWoods_EventScript_ResearcherBagFull
	setvar VAR_HOENN_SCENE_DEVON, 1
	setflag FLAG_HOENN_WOODS_RESEARCHER_SAVED
	textcolor NPC_TEXT_COLOR_MALE
	msgbox PetalburgWoods_Text_ResearcherLeaves
	closemessage
	applymovement LOCALID_WOODS_RESEARCHER, PetalburgWoods_Movement_ResearcherLeaves
	waitmovement 0
	removeobject LOCALID_WOODS_RESEARCHER
	releaseall
	end

PetalburgWoods_EventScript_ResearcherStillScared::
	msgbox PetalburgWoods_Text_ResearcherHelp
	release
	end

PetalburgWoods_EventScript_ResearcherBagFull::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox PetalburgWoods_Text_ResearcherBagFull
	releaseall
	end

@ ---------------------------------------------------------------- TREECKO
@ The big tree (40,23)/(41,23). Quiet until the grunt is beaten; then a wild
@ TREECKO Lv5 battle, and unless it was caught it joins anyway (plan 4.6 (5)).
@ Losing whites out with the flag off: it is there again next time.
PetalburgWoods_EventScript_BigTree::
	lockall
	goto_if_set FLAG_HOENN_GOT_TREECKO_IN_WOODS, PetalburgWoods_EventScript_BigTreeAfter
	goto_if_not_defeated TRAINER_HOENN_GRUNT_PETALBURG_WOODS, PetalburgWoods_EventScript_BigTreeQuiet
	msgbox PetalburgWoods_Text_BigTreeRustle
	closemessage
	showmonpic SPECIES_TREECKO, 10, 3
	playmoncry SPECIES_TREECKO, CRY_MODE_NORMAL
	msgbox PetalburgWoods_Text_TreeckoGlares
	waitmoncry
	hidemonpic
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	call_if_ne VAR_RESULT, PARTY_SIZE, PetalburgWoods_EventScript_TreeckoPikachu
	closemessage
	special CreatePerfectScriptedTreecko
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, PetalburgWoods_EventScript_TreeckoCaught
	msgbox PetalburgWoods_Text_TreeckoJoins
	setvar VAR_TEMP_1, SPECIES_TREECKO
	call EventScript_GivePerfectRegionalStarterLv5
	goto_if_eq VAR_RESULT, FALSE, PetalburgWoods_EventScript_TreeckoNoRoom
PetalburgWoods_EventScript_TreeckoCaught::
	setflag FLAG_HOENN_GOT_TREECKO_IN_WOODS
	releaseall
	end

PetalburgWoods_EventScript_TreeckoPikachu::
	msgbox PetalburgWoods_Text_TreeckoPikachu
	return

PetalburgWoods_EventScript_TreeckoNoRoom::
	msgbox PetalburgWoods_Text_TreeckoNoRoom
	releaseall
	end

PetalburgWoods_EventScript_BigTreeQuiet::
	msgbox PetalburgWoods_Text_BigTreeQuiet
	releaseall
	end

PetalburgWoods_EventScript_BigTreeAfter::
	msgbox PetalburgWoods_Text_BigTreeAfter
	releaseall
	end

@ ---------------------------------------------------------------- E12
@ The LASS's MIRACLE SEED, for the STONE BADGE (Emerald's condition)
PetalburgWoods_EventScript_H4::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_MIRACLE_SEED, PetalburgWoods_EventScript_LassAfter
	goto_if_unset FLAG_HOENN_BADGE01_GET, PetalburgWoods_EventScript_LassNoBadge
	msgbox PetalburgWoods_Text_H4
	giveitem ITEM_MIRACLE_SEED
	goto_if_eq VAR_RESULT, FALSE, PetalburgWoods_EventScript_LassBagFull
	setflag FLAG_HOENN_GOT_MIRACLE_SEED
PetalburgWoods_EventScript_LassAfter::
	msgbox PetalburgWoods_Text_LassAfter
	release
	end

PetalburgWoods_EventScript_LassNoBadge::
	msgbox PetalburgWoods_Text_LassNoBadge
	release
	end

PetalburgWoods_EventScript_LassBagFull::
	msgbox PetalburgWoods_Text_LassBagFull
	release
	end

PetalburgWoods_Movement_ResearcherRunsDown:
	walk_fast_down
	walk_fast_down
	walk_in_place_faster_down
	step_end

PetalburgWoods_Movement_GruntComesDown:
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

PetalburgWoods_Movement_GruntRunsOff:
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end

@ Out of the grass to (23,19), (24,19), (25,19)
PetalburgWoods_Movement_JessieComes:
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_in_place_faster_right
	step_end

PetalburgWoods_Movement_JamesComes:
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_in_place_faster_right
	step_end

PetalburgWoods_Movement_MeowthComes:
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_in_place_faster_right
	step_end

PetalburgWoods_Movement_ResearcherLeaves:
	walk_up
	walk_up
	step_end
@ END PATCH
