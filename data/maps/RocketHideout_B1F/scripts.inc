RocketHideout_B1F_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, RocketHideout_B1F_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, RocketHideout_B1F_OnTransition
	.byte 0

RocketHideout_B1F_OnLoad::
	call_if_not_defeated TRAINER_TEAM_ROCKET_GRUNT_12 RocketHideout_B1F_EventScript_SetBarrier
	end

RocketHideout_B1F_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_ROCKET_HIDEOUT_B1F
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B1F_CAMERA_GRUNT
	call_if_ge VAR_ROCKET_HIDEOUT_SECURITY, 2, RocketHideout_B1F_EventScript_DisarmCameras
	end

RocketHideout_B1F_EventScript_DisarmCameras::
	setvar VAR_TEMP_2, 1
	return

@ HGSS/Crystal's Team Rocket Base security: the PERSIAN statues are cameras. Walking
@ past them sounds the alarm and two GRUNTS come out one after the other (Crystal's
@ GRUNTM 20 and 21). Beating both, or shutting off the generator on B2F, disarms them.
RocketHideout_B1F_EventScript_SecurityCamera::
	lockall
	setvar VAR_TEMP_2, 1
	goto_if_eq VAR_ROCKET_HIDEOUT_SECURITY, 1, RocketHideout_B1F_EventScript_CameraGrunt2
	call RocketHideout_B1F_EventScript_Alarm
	msgbox RocketHideout_B1F_Text_CameraGrunt1Intro
	closemessage
	trainerbattle_no_intro TRAINER_ROCKET_HIDEOUT_CAMERA_GRUNT_1, RocketHideout_B1F_Text_CameraGrunt1Defeat
	call RocketHideout_B1F_EventScript_CameraGruntLeaves
	setvar VAR_ROCKET_HIDEOUT_SECURITY, 1
RocketHideout_B1F_EventScript_CameraGrunt2::
	call RocketHideout_B1F_EventScript_Alarm
	msgbox RocketHideout_B1F_Text_CameraGrunt2Intro
	closemessage
	trainerbattle_no_intro TRAINER_ROCKET_HIDEOUT_CAMERA_GRUNT_2, RocketHideout_B1F_Text_CameraGrunt2Defeat
	msgbox RocketHideout_B1F_Text_CameraGrunt2PostBattle
	closemessage
	call RocketHideout_B1F_EventScript_CameraGruntLeaves
	setvar VAR_ROCKET_HIDEOUT_SECURITY, 2
	fadedefaultbgm
	releaseall
	end

@ The alarm rings, the player is startled and a GRUNT steps out right above the player
RocketHideout_B1F_EventScript_Alarm::
	playse SE_M_LICK
	delay 10
	playse SE_M_LICK
	delay 10
	playse SE_M_LICK
	delay 10
	playse SE_M_LICK
	delay 10
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	getplayerxy VAR_0x8004, VAR_0x8005
	setobjectxyperm LOCALID_ROCKET_HIDEOUT_B1F_CAMERA_GRUNT, VAR_0x8004, 4
	addobject LOCALID_ROCKET_HIDEOUT_B1F_CAMERA_GRUNT
	applymovement LOCALID_ROCKET_HIDEOUT_B1F_CAMERA_GRUNT, RocketHideout_B1F_Movement_CameraGruntApproach
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	return

RocketHideout_B1F_EventScript_CameraGruntLeaves::
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROCKET_HIDEOUT_B1F_CAMERA_GRUNT
	fadescreen FADE_FROM_BLACK
	return

RocketHideout_B1F_EventScript_PersianStatue::
	lock
	goto_if_ge VAR_ROCKET_HIDEOUT_SECURITY, 2, RocketHideout_B1F_EventScript_PersianStatueOff
	msgbox RocketHideout_B1F_Text_PersianStatueCamera
	release
	end

RocketHideout_B1F_EventScript_PersianStatueOff::
	msgbox RocketHideout_B1F_Text_PersianStatueOff
	release
	end

RocketHideout_B1F_Movement_CameraGruntApproach::
	walk_down
	step_end

RocketHideout_B1F_EventScript_Grunt1::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_8, RocketHideout_B1F_Text_Grunt1Intro, RocketHideout_B1F_Text_Grunt1Defeat
	msgbox RocketHideout_B1F_Text_Grunt1PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B1F_EventScript_Grunt2::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_9, RocketHideout_B1F_Text_Grunt2Intro, RocketHideout_B1F_Text_Grunt2Defeat
	msgbox RocketHideout_B1F_Text_Grunt2PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B1F_EventScript_Grunt3::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_10, RocketHideout_B1F_Text_Grunt3Intro, RocketHideout_B1F_Text_Grunt3Defeat
	msgbox RocketHideout_B1F_Text_Grunt3PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B1F_EventScript_Grunt4::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_11, RocketHideout_B1F_Text_Grunt4Intro, RocketHideout_B1F_Text_Grunt4Defeat
	msgbox RocketHideout_B1F_Text_Grunt4PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B1F_EventScript_Grunt5::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_12, RocketHideout_B1F_Text_Grunt5Intro, RocketHideout_B1F_Text_Grunt5Defeat, RocketHideout_B1F_EventScript_DefeatedGrunt5
	msgbox RocketHideout_B1F_Text_Grunt5PostBattle, MSGBOX_AUTOCLOSE
	end

RocketHideout_B1F_EventScript_DefeatedGrunt5::
	call RocketHideout_B1F_EventScript_RemoveBarrier
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	release
	end

RocketHideout_B1F_EventScript_SetBarrier::
	setmetatile 20, 19, METATILE_SilphCo_HideoutBarrier_TopLeft_Floor, 1
	setmetatile 21, 19, METATILE_SilphCo_HideoutBarrier_TopRight_Floor, 1
	setmetatile 20, 20, METATILE_SilphCo_HideoutBarrier_BottomLeft, 1
	setmetatile 21, 20, METATILE_SilphCo_HideoutBarrier_BottomRight, 1
	setmetatile 20, 21, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 21, 21, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	return

RocketHideout_B1F_EventScript_RemoveBarrier::
	setmetatile 20, 19, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 21, 19, METATILE_SilphCo_HideoutFloor, 0
	setmetatile 20, 20, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 21, 20, METATILE_SilphCo_HideoutFloor, 0
	setmetatile 20, 21, METATILE_SilphCo_HideoutFloor_ShadeFull, 0
	setmetatile 21, 21, METATILE_SilphCo_HideoutFloor, 0
	return
