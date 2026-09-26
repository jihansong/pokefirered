CeladonCity_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CeladonCity_Gym_OnTransition
	.byte 0

CeladonCity_Gym_OnTransition::
	setflag FLAG_TEMP_1
	setflag FLAG_TEMP_2
	goto_if_set FLAG_ROCKET_CELADON_GYM, CeladonCity_Gym_EventScript_NoRockets
	goto_if_unset FLAG_BADGE04_GET, CeladonCity_Gym_EventScript_NoRockets
	clearflag FLAG_TEMP_1
	setvar VAR_TEMP_1, 1
CeladonCity_Gym_EventScript_NoRockets::
	end

@ Thunder Yellow v0.5.0, TEAM ROCKET event 6: after the RAINBOW BADGE, a "new
@ trainee" greets the player at the CELADON GYM - JAMES in disguise, after PIKACHU
@ and the gym's secret perfume formula. MEOWTH spills the perfume, a double
@ battle, and ERIKA gives the player a MIRACLE SEED.
CeladonCity_Gym_EventScript_RocketPerfume::
	lockall
	setvar VAR_TEMP_1, 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	goto_if_eq VAR_ROCKET_RETRY, 7, CeladonCity_Gym_EventScript_RocketRetry
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox CeladonCity_Gym_Text_TraineeGreeting
	closemessage
	clearflag FLAG_TEMP_2
	addobject LOCALID_CELADON_GYM_JESSIE
	addobject LOCALID_CELADON_GYM_MEOWTH
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CeladonCity_Gym_Text_MeowthNowJames
	closemessage
	fadescreenspeed FADE_TO_WHITE, 1
	removeobject LOCALID_CELADON_GYM_TRAINEE
	addobject LOCALID_CELADON_GYM_JAMES
	fadescreenspeed FADE_FROM_WHITE, 1
	playbgm MUS_ENCOUNTER_ROCKET, 0
	msgbox CeladonCity_Gym_Text_JamesReveal
	msgbox CeladonCity_Gym_Text_JamesVictreebel
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox CeladonCity_Gym_Text_JessiePerfumePlan
	textcolor NPC_TEXT_COLOR_MALE
	msgbox CeladonCity_Gym_Text_MeowthSpills
	closemessage
	playse SE_M_POISON_POWDER
	fadescreenspeed FADE_TO_WHITE, 3
	fadescreenspeed FADE_FROM_WHITE, 3
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox CeladonCity_Gym_Text_PerfumeCloud
	closemessage
	applymovement LOCALID_CELADON_GYM_JESSIE, CeladonCity_Gym_Movement_Cough
	applymovement LOCALID_CELADON_GYM_JAMES, CeladonCity_Gym_Movement_Cough
	applymovement LOCALID_CELADON_GYM_MEOWTH, CeladonCity_Gym_Movement_Cough
	waitmovement 0
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox CeladonCity_Gym_Text_JessieFurious
	closemessage
CeladonCity_Gym_EventScript_RocketBattle::
	setvar VAR_0x8004, 7
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_CELADON_GYM_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_CELADON_GYM, CeladonCity_Gym_Text_RocketDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	setvar VAR_0x8008, LOCALID_CELADON_GYM_JESSIE
	setvar VAR_0x8009, LOCALID_CELADON_GYM_JAMES
	setvar VAR_0x800A, LOCALID_CELADON_GYM_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_CELADON_GYM_JESSIE
	removeobject LOCALID_CELADON_GYM_JAMES
	removeobject LOCALID_CELADON_GYM_MEOWTH
	setflag FLAG_ROCKET_CELADON_GYM
	fadedefaultbgm
	setvar VAR_0x8004, 792
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, CeladonCity_Gym_EventScript_RocketCoins
	setvar VAR_0x8004, 1848
CeladonCity_Gym_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox CeladonCity_Gym_Text_ErikaThanks
	giveitem ITEM_MIRACLE_SEED
	setvar VAR_0x8004, ROCKET_HELD_MIRACLE_SEED
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_FEMALE
	call_if_ne VAR_0x8007, FALSE, CeladonCity_Gym_EventScript_ErikaMiracleSeed
	msgbox CeladonCity_Gym_Text_ErikaLeafStone
	giveitem ITEM_LEAF_STONE
	setvar VAR_0x8004, ROCKET_BONUS_LEAF_STONE
	call EventScript_RocketRewardResult
	releaseall
	end

@ What the first reward does, told only when it went into the bag (not
@ when the OFFICER at VIRIDIAN keeps it for now).
CeladonCity_Gym_EventScript_ErikaMiracleSeed::
	msgbox CeladonCity_Gym_Text_ErikaMiracleSeed
	return

@ After a loss: JAMES drops the disguise straight away.
CeladonCity_Gym_EventScript_RocketRetry::
	clearflag FLAG_TEMP_2
	addobject LOCALID_CELADON_GYM_JESSIE
	addobject LOCALID_CELADON_GYM_MEOWTH
	fadescreenspeed FADE_TO_WHITE, 1
	removeobject LOCALID_CELADON_GYM_TRAINEE
	addobject LOCALID_CELADON_GYM_JAMES
	fadescreenspeed FADE_FROM_WHITE, 1
	playbgm MUS_ENCOUNTER_ROCKET, 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	call EventScript_RocketTrioRetry
	goto CeladonCity_Gym_EventScript_RocketBattle

CeladonCity_Gym_Movement_Cough:
	walk_in_place_faster_down
	walk_in_place_faster_down
	walk_in_place_faster_down
	step_end

CeladonCity_Gym_EventScript_Erika::
	famechecker FAMECHECKER_ERIKA, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	trainerbattle_single TRAINER_LEADER_ERIKA, CeladonCity_Gym_Text_ErikaIntro, CeladonCity_Gym_Text_ErikaDefeat, CeladonCity_Gym_EventScript_DefeatedErika, NO_MUSIC
	goto_if_unset FLAG_GOT_TM19_FROM_ERIKA, CeladonCity_Gym_EventScript_GiveTM19
	famechecker FAMECHECKER_ERIKA, 4
	msgbox CeladonCity_Gym_Text_ErikaPostBattle
	release
	end

CeladonCity_Gym_EventScript_DefeatedErika::
	famechecker FAMECHECKER_ERIKA, 1
	clearflag FLAG_HIDE_FAME_CHECKER_ERIKA_JOURNALS
	setflag FLAG_DEFEATED_ERIKA
	setflag FLAG_BADGE04_GET
	set_gym_trainers 4
	goto CeladonCity_Gym_EventScript_GiveTM19
	end

CeladonCity_Gym_EventScript_GiveTM19::
	msgbox CeladonCity_Gym_Text_ExplainRainbowBadgeTakeThis
	checkitemspace ITEM_TM19
	goto_if_eq VAR_RESULT, FALSE, CeladonCity_Gym_EventScript_NoRoomForTM19
	giveitem_msg CeladonCity_Gym_Text_ReceivedTM19FromErika, ITEM_TM19
	setflag FLAG_GOT_TM19_FROM_ERIKA
	msgbox CeladonCity_Gym_Text_ExplainTM19
	release
	end

CeladonCity_Gym_EventScript_NoRoomForTM19::
	msgbox CeladonCity_Gym_Text_ShouldMakeRoomForThis
	release
	end

CeladonCity_Gym_EventScript_Kay::
	trainerbattle_single TRAINER_LASS_KAY, CeladonCity_Gym_Text_KayIntro, CeladonCity_Gym_Text_KayDefeat
	msgbox CeladonCity_Gym_Text_KayPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Lisa::
	trainerbattle_single TRAINER_LASS_LISA, CeladonCity_Gym_Text_LisaIntro, CeladonCity_Gym_Text_LisaDefeat
	famechecker FAMECHECKER_ERIKA, 2
	msgbox CeladonCity_Gym_Text_LisaPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Tina::
	trainerbattle_single TRAINER_PICNICKER_TINA, CeladonCity_Gym_Text_TinaIntro, CeladonCity_Gym_Text_TinaDefeat
	msgbox CeladonCity_Gym_Text_TinaPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Bridget::
	trainerbattle_single TRAINER_BEAUTY_BRIDGET, CeladonCity_Gym_Text_BridgetIntro, CeladonCity_Gym_Text_BridgetDefeat
	msgbox CeladonCity_Gym_Text_BridgetPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Tamia::
	trainerbattle_single TRAINER_BEAUTY_TAMIA, CeladonCity_Gym_Text_TamiaIntro, CeladonCity_Gym_Text_TamiaDefeat
	famechecker FAMECHECKER_ERIKA, 3
	msgbox CeladonCity_Gym_Text_TamiaPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Lori::
	trainerbattle_single TRAINER_BEAUTY_LORI, CeladonCity_Gym_Text_LoriIntro, CeladonCity_Gym_Text_LoriDefeat
	msgbox CeladonCity_Gym_Text_LoriPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_Mary::
	trainerbattle_single TRAINER_COOLTRAINER_MARY, CeladonCity_Gym_Text_MaryIntro, CeladonCity_Gym_Text_MaryDefeat
	msgbox CeladonCity_Gym_Text_MaryPostBattle, MSGBOX_AUTOCLOSE
	end

CeladonCity_Gym_EventScript_GymStatue::
	lockall
	goto_if_set FLAG_BADGE04_GET, CeladonCity_Gym_EventScript_GymStatuePostVictory
	msgbox CeladonCity_Gym_Text_GymStatue
	releaseall
	end

CeladonCity_Gym_EventScript_GymStatuePostVictory::
	msgbox CeladonCity_Gym_Text_GymStatuePlayerWon
	releaseall
	end
