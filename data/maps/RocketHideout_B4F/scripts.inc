.equ NUM_DOOR_GRUNTS_DEFEATED, VAR_TEMP_1

RocketHideout_B4F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, RocketHideout_B4F_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, RocketHideout_B4F_EventScript_HideJessieJamesOnTransition
	.byte 0

RocketHideout_B4F_EventScript_HideJessieJamesOnTransition::
	call RocketHideout_B4F_EventScript_HideJessieJames
	end

RocketHideout_B4F_OnLoad::
	setvar NUM_DOOR_GRUNTS_DEFEATED, 0
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_16, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_17, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_ne NUM_DOOR_GRUNTS_DEFEATED, 2, RocketHideout_B4F_EventScript_SetBarrier
	end

RocketHideout_B4F_EventScript_CountGruntDefeated::
	addvar NUM_DOOR_GRUNTS_DEFEATED, 1
	return

RocketHideout_B4F_EventScript_Giovanni::
	lock
	faceplayer
	famechecker FAMECHECKER_GIOVANNI, 0
	message RocketHideout_B4F_Text_GiovanniIntro
	waitmessage
	playbgm MUS_ENCOUNTER_ROCKET, 0
	waitbuttonpress
	trainerbattle_no_intro TRAINER_BOSS_GIOVANNI, RocketHideout_B4F_Text_GiovanniDefeat
	msgbox RocketHideout_B4F_Text_GiovanniPostBattle
	fadescreen FADE_TO_BLACK
	closemessage
	removeobject LOCALID_HIDEOUT_GIOVANNI
	addobject LOCALID_SILPH_SCOPE
	clearflag FLAG_HIDE_SILPH_SCOPE
	setflag FLAG_HIDE_CELADON_ROCKETS
	famechecker FAMECHECKER_GIOVANNI, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	fadescreen FADE_FROM_BLACK
	release
	end

RocketHideout_B4F_EventScript_SilphScope::
	lock
	faceplayer
	removeobject LOCALID_SILPH_SCOPE
	giveitem ITEM_SILPH_SCOPE
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	release
	end

RocketHideout_B4F_EventScript_Grunt1::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_18, RocketHideout_B4F_Text_Grunt1Intro, RocketHideout_B4F_Text_Grunt1Defeat, RocketHideout_B4F_EventScript_DefeatedGrunt1
	msgbox RocketHideout_B4F_Text_Grunt1PostBattle
	release
	end

RocketHideout_B4F_EventScript_DefeatedGrunt1::
	msgbox RocketHideout_B4F_Text_Grunt1PostBattle
	addobject LOCALID_LIFT_KEY
	clearflag FLAG_HIDE_LIFT_KEY
	release
	end

RocketHideout_B4F_EventScript_LiftKey::
	lock
	faceplayer
	setflag FLAG_CAN_USE_ROCKET_HIDEOUT_LIFT
	removeobject LOCALID_LIFT_KEY
	giveitem ITEM_LIFT_KEY
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	release
	end

RocketHideout_B4F_EventScript_Grunt2::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_16, RocketHideout_B4F_Text_Grunt2Intro, RocketHideout_B4F_Text_Grunt2Defeat, RocketHideout_B4F_EventScript_DefeatedGrunt2
	msgbox RocketHideout_B4F_Text_Grunt2PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B4F_EventScript_DefeatedGrunt2::
	setvar NUM_DOOR_GRUNTS_DEFEATED, 0
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_16, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_17, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_eq NUM_DOOR_GRUNTS_DEFEATED, 2, RocketHideout_B4F_EventScript_RemoveBarrier
	call_if_eq NUM_DOOR_GRUNTS_DEFEATED, 2, RocketHideout_B4F_EventScript_DrawMapForBarrierRemoval
	release
	end

RocketHideout_B4F_EventScript_Grunt3::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_17, RocketHideout_B4F_Text_Grunt3Intro, RocketHideout_B4F_Text_Grunt3Defeat, RocketHideout_B4F_EventScript_DefeatedGrunt3
	msgbox RocketHideout_B4F_Text_Grunt3PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B4F_EventScript_DefeatedGrunt3::
	setvar NUM_DOOR_GRUNTS_DEFEATED, 0
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_16, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_defeated TRAINER_TEAM_ROCKET_GRUNT_17, RocketHideout_B4F_EventScript_CountGruntDefeated
	call_if_eq NUM_DOOR_GRUNTS_DEFEATED, 2, RocketHideout_B4F_EventScript_RemoveBarrier
	call_if_eq NUM_DOOR_GRUNTS_DEFEATED, 2, RocketHideout_B4F_EventScript_DrawMapForBarrierRemoval
	release
	end

RocketHideout_B4F_EventScript_DrawMapForBarrierRemoval::
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	return

RocketHideout_B4F_EventScript_SetBarrier::
	setmetatile 17, 12, METATILE_SilphCo_HideoutBarrier_TopLeft_Floor, 1
	setmetatile 18, 12, METATILE_SilphCo_HideoutBarrier_TopRight_Floor, 1
	setmetatile 17, 13, METATILE_SilphCo_HideoutBarrier_BottomLeft, 1
	setmetatile 18, 13, METATILE_SilphCo_HideoutBarrier_BottomRight, 1
	setmetatile 17, 14, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 18, 14, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	return

RocketHideout_B4F_EventScript_RemoveBarrier::
	setmetatile 17, 12, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 18, 12, METATILE_SilphCo_HideoutFloor, 0
	setmetatile 17, 13, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 18, 13, METATILE_SilphCo_HideoutFloor, 0
	setmetatile 17, 14, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 18, 14, METATILE_SilphCo_HideoutFloor, 0
	return

RocketHideout_B4F_EventScript_JessieJamesTrigger0::
	lockall
	setvar VAR_TEMP_1, 0
	goto RocketHideout_B4F_EventScript_JessieJames
	end

RocketHideout_B4F_EventScript_JessieJamesTrigger1::
	lockall
	setvar VAR_TEMP_1, 1
	goto RocketHideout_B4F_EventScript_JessieJames
	end

@ Jessie & James ambush the player, as in Pokémon Yellow.
RocketHideout_B4F_EventScript_JessieJames::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playbgm MUS_ENCOUNTER_ROCKET, 0
	msgbox RocketHideout_B4F_Text_JessieJamesStop
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	call_if_eq VAR_TEMP_1, 0, RocketHideout_B4F_EventScript_JessieJamesAppear0
	call_if_eq VAR_TEMP_1, 1, RocketHideout_B4F_EventScript_JessieJamesAppear1
	goto_if_eq VAR_ROCKET_RETRY, 5, RocketHideout_B4F_EventScript_JessieJamesRetry
	msgbox RocketHideout_B4F_Text_JessieJamesIntro
	closemessage
RocketHideout_B4F_EventScript_JessieJamesBattle::
	setvar VAR_0x8004, 5
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_ROCKET_HIDEOUT_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_ROCKET_HIDEOUT, RocketHideout_B4F_Text_JessieJamesDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox RocketHideout_B4F_Text_JessieJamesBlastOff
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROCKET_HIDEOUT_JESSIE
	removeobject LOCALID_ROCKET_HIDEOUT_JAMES
	fadescreen FADE_FROM_BLACK
	setvar VAR_MAP_SCENE_ROCKET_HIDEOUT_B4F_JESSIE_JAMES, 1
	addmoney 720
	setvar VAR_0x8004, 720
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, RocketHideout_B4F_EventScript_RocketCoins
	addmoney 960
	setvar VAR_0x8004, 1680
RocketHideout_B4F_EventScript_RocketCoins::
	call EventScript_RocketMeowthCoins
	@ v0.9.0: a THUNDER STONE they drop, which OAK's PIKACHU wants nothing to do
	@ with (it never evolves, party_menu.c). Another PIKACHU or EEVEE can use it.
	msgbox RocketHideout_B4F_Text_SomethingClattered
	giveitem ITEM_THUNDER_STONE
	setvar VAR_0x8004, ROCKET_BONUS_THUNDER_STONE
	call EventScript_RocketRewardResult
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	goto_if_eq VAR_RESULT, PARTY_SIZE, RocketHideout_B4F_EventScript_JessieJamesDone
	playmoncry SPECIES_PIKACHU, CRY_MODE_NORMAL
	waitmoncry
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox RocketHideout_B4F_Text_PikachuRefusesStone
RocketHideout_B4F_EventScript_JessieJamesDone::
	releaseall
	end

RocketHideout_B4F_EventScript_JessieJamesRetry::
	call EventScript_RocketTrioRetry
	goto RocketHideout_B4F_EventScript_JessieJamesBattle

RocketHideout_B4F_EventScript_JessieJamesAppear0::
	setobjectxyperm LOCALID_ROCKET_HIDEOUT_JESSIE, 14, 24
	setobjectxyperm LOCALID_ROCKET_HIDEOUT_JAMES, 14, 25
	addobject LOCALID_ROCKET_HIDEOUT_JESSIE
	addobject LOCALID_ROCKET_HIDEOUT_JAMES
	applymovement LOCALID_ROCKET_HIDEOUT_JESSIE, RocketHideout_B4F_EventScript_JessieJamesMovement0
	applymovement LOCALID_ROCKET_HIDEOUT_JAMES, RocketHideout_B4F_EventScript_JessieJamesMovement0
	waitmovement 0
	return

RocketHideout_B4F_EventScript_JessieJamesMovement0:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

RocketHideout_B4F_EventScript_JessieJamesAppear1::
	setobjectxyperm LOCALID_ROCKET_HIDEOUT_JESSIE, 14, 24
	setobjectxyperm LOCALID_ROCKET_HIDEOUT_JAMES, 14, 25
	addobject LOCALID_ROCKET_HIDEOUT_JESSIE
	addobject LOCALID_ROCKET_HIDEOUT_JAMES
	applymovement LOCALID_ROCKET_HIDEOUT_JESSIE, RocketHideout_B4F_EventScript_JessieJamesMovement1
	applymovement LOCALID_ROCKET_HIDEOUT_JAMES, RocketHideout_B4F_EventScript_JessieJamesMovement1
	waitmovement 0
	return

RocketHideout_B4F_EventScript_JessieJamesMovement1:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

RocketHideout_B4F_EventScript_HideJessieJames::
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B4F_JESSIE_JAMES
	return
