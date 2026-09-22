FuchsiaCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FuchsiaCity_OnTransition
	.byte 0

FuchsiaCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_FUCHSIA_CITY
	call_if_set FLAG_GOT_DOME_FOSSIL, FuchsiaCity_EventScript_SetOmanyteGfx
	call_if_unset FLAG_GOT_DOME_FOSSIL, FuchsiaCity_EventScript_SetKabutoGfx
	setflag FLAG_TEMP_1
	call_if_set FLAG_GOT_HM03, FuchsiaCity_EventScript_ReadyRocketDratini
	end

FuchsiaCity_EventScript_ReadyRocketDratini::
	goto_if_set FLAG_ROCKET_SAFARI_DRATINI, EventScript_Return
	setvar VAR_TEMP_1, 1
	return

@ Thunder Yellow v0.5.0, TEAM ROCKET event 7: once the player has SURF from the
@ SAFARI ZONE, the trio come out of the SAFARI gate right behind them with a
@ poached DRATINI in a sack. A double battle, the DRATINI swims home, and the
@ SAFARI ZONE attendant gives the player a DRAGON FANG.
FuchsiaCity_EventScript_RocketDratini::
	lockall
	setvar VAR_TEMP_1, 0
	clearflag FLAG_TEMP_1
	addobject LOCALID_FUCHSIA_JESSIE
	addobject LOCALID_FUCHSIA_MEOWTH
	addobject LOCALID_FUCHSIA_JAMES
	textcolor NPC_TEXT_COLOR_MALE
	msgbox FuchsiaCity_Text_MeowthSackOfDratini
	closemessage
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	playmoncry SPECIES_DRATINI, CRY_MODE_WEAK
	waitmoncry
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox FuchsiaCity_Text_SomethingInSack
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox FuchsiaCity_Text_JessieRareDratini
	textcolor NPC_TEXT_COLOR_MALE
	msgbox FuchsiaCity_Text_JamesPoached
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox FuchsiaCity_Text_RocketDratiniIntro
	closemessage
	setvar VAR_LAST_TALKED, LOCALID_FUCHSIA_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_SAFARI, FuchsiaCity_Text_RocketDratiniDefeat
	playmoncry SPECIES_DRATINI, CRY_MODE_NORMAL
	waitmoncry
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox FuchsiaCity_Text_DratiniEscapes
	closemessage
	setvar VAR_0x8008, LOCALID_FUCHSIA_JESSIE
	setvar VAR_0x8009, LOCALID_FUCHSIA_JAMES
	setvar VAR_0x800A, LOCALID_FUCHSIA_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_FUCHSIA_JESSIE
	removeobject LOCALID_FUCHSIA_MEOWTH
	removeobject LOCALID_FUCHSIA_JAMES
	setflag FLAG_ROCKET_SAFARI_DRATINI
	fadedefaultbgm
	textcolor NPC_TEXT_COLOR_MALE
	msgbox FuchsiaCity_Text_AttendantThanks
	giveitem ITEM_DRAGON_FANG
	msgbox FuchsiaCity_Text_AttendantDragonFang
	releaseall
	end

FuchsiaCity_EventScript_SetOmanyteGfx::
	setvar VAR_OBJ_GFX_ID_0, OBJ_EVENT_GFX_OMANYTE
	return

FuchsiaCity_EventScript_SetKabutoGfx::
	setvar VAR_OBJ_GFX_ID_0, OBJ_EVENT_GFX_KABUTO
	return

FuchsiaCity_EventScript_LittleBoy::
	msgbox FuchsiaCity_Text_DidYouTrySafariGame, MSGBOX_NPC
	end

FuchsiaCity_EventScript_OldMan::
	msgbox FuchsiaCity_Text_SafariZoneZooInFront, MSGBOX_NPC
	end

FuchsiaCity_EventScript_Erik::
	msgbox FuchsiaCity_Text_WheresSara, MSGBOX_NPC
	end

FuchsiaCity_EventScript_Youngster::
	msgbox FuchsiaCity_Text_ItemBallInThere, MSGBOX_NPC
	end

FuchsiaCity_EventScript_Lass::
	lock
	faceplayer
	famechecker FAMECHECKER_KOGA, 3
	msgbox FuchsiaCity_Text_MyFatherIsGymLeader
	release
	end

FuchsiaCity_EventScript_CitySign::
	msgbox FuchsiaCity_Text_CitySign, MSGBOX_SIGN
	end

FuchsiaCity_EventScript_SafariZoneSign::
	msgbox FuchsiaCity_Text_SafariZoneSign, MSGBOX_SIGN
	end

FuchsiaCity_EventScript_SafariGameSign::
	msgbox FuchsiaCity_Text_SafariGameSign, MSGBOX_SIGN
	end

FuchsiaCity_EventScript_WardensHomeSign::
	msgbox FuchsiaCity_Text_WardensHomeSign, MSGBOX_SIGN
	end

@ Unused
FuchsiaCity_EventScript_SafariZoneOfficeSign::
	msgbox FuchsiaCity_Text_SafariZoneOfficeSign, MSGBOX_SIGN
	end

FuchsiaCity_EventScript_GymSign::
	lockall
	famechecker FAMECHECKER_KOGA, 0
	msgbox FuchsiaCity_Text_GymSign
	releaseall
	end

FuchsiaCity_EventScript_ChanseySign::
	lockall
	setvar VAR_0x8004, SPECIES_CHANSEY
	special SetSeenMon
	showmonpic SPECIES_CHANSEY, 10, 3
	msgbox FuchsiaCity_Text_ChanseySign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_VoltorbSign::
	lockall
	setvar VAR_0x8004, SPECIES_VOLTORB
	special SetSeenMon
	showmonpic SPECIES_VOLTORB, 10, 3
	msgbox FuchsiaCity_Text_VoltorbSign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_KangaskhanSign::
	lockall
	setvar VAR_0x8004, SPECIES_KANGASKHAN
	special SetSeenMon
	showmonpic SPECIES_KANGASKHAN, 10, 3
	msgbox FuchsiaCity_Text_KangaskhanSign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_SlowpokeSign::
	lockall
	setvar VAR_0x8004, SPECIES_SLOWPOKE
	special SetSeenMon
	showmonpic SPECIES_SLOWPOKE, 10, 3
	msgbox FuchsiaCity_Text_SlowpokeSign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_LaprasSign::
	lockall
	setvar VAR_0x8004, SPECIES_LAPRAS
	special SetSeenMon
	showmonpic SPECIES_LAPRAS, 10, 3
	msgbox FuchsiaCity_Text_LaprasSign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_FossilMonSign::
	lockall
	goto_if_set FLAG_GOT_DOME_FOSSIL, FuchsiaCity_EventScript_OmanyteSign
	setvar VAR_0x8004, SPECIES_KABUTO
	special SetSeenMon
	showmonpic SPECIES_KABUTO, 10, 3
	msgbox FuchsiaCity_Text_KabutoSign
	hidemonpic
	releaseall
	end

FuchsiaCity_EventScript_OmanyteSign::
	setvar VAR_0x8004, SPECIES_OMANYTE
	special SetSeenMon
	showmonpic SPECIES_OMANYTE, 10, 3
	msgbox FuchsiaCity_Text_OmanyteSign
	hidemonpic
	releaseall
	end
