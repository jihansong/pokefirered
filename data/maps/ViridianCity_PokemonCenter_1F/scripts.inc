ViridianCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ViridianCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

ViridianCity_PokemonCenter_1F_OnTransition::
	setrespawn HEAL_LOCATION_VIRIDIAN_CITY
	setflag FLAG_TEMP_1
	call_if_unset FLAG_ROCKET_VIRIDIAN_PC, ViridianCity_PokemonCenter_1F_EventScript_ReadyRocketRaid
	end

ViridianCity_PokemonCenter_1F_EventScript_ReadyRocketRaid::
	goto_if_unset FLAG_RECEIVED_STARTER_PIKACHU, EventScript_Return
	setvar VAR_TEMP_1, 1
	return

@ Thunder Yellow v0.5.0, TEAM ROCKET event 1: the first time the player walks into
@ the VIRIDIAN POKéMON CENTER with PIKACHU, JESSIE, JAMES and MEOWTH raid it, and the
@ PIKACHU there drive them off with a THUNDERBOLT. MEOWTH notices the player's
@ PIKACHU is no ordinary one, which is why the trio keep turning up after it.
ViridianCity_PokemonCenter_1F_EventScript_RocketRaid::
	lockall
	setvar VAR_TEMP_1, 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
	waitmovement 0
	fadescreen FADE_TO_BLACK
	playse SE_M_EXPLOSION
	clearflag FLAG_TEMP_1
	addobject LOCALID_VIRIDIAN_PC_JESSIE
	addobject LOCALID_VIRIDIAN_PC_JAMES
	addobject LOCALID_VIRIDIAN_PC_MEOWTH
	delay 30
	fadescreen FADE_FROM_BLACK
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	call EventScript_RocketTrioMotto
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox ViridianCity_PokemonCenter_1F_Text_JessieWantAllMons
	msgbox ViridianCity_PokemonCenter_1F_Text_NurseOhNo
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox ViridianCity_PokemonCenter_1F_Text_PikachuSparks
	closemessage
	playmoncry SPECIES_PIKACHU, CRY_MODE_ENCOUNTER
	waitmoncry
	playse SE_M_THUNDERBOLT
	fadescreenspeed FADE_TO_WHITE, 0
	fadescreenspeed FADE_FROM_WHITE, 0
	fadescreenspeed FADE_TO_WHITE, 0
	fadescreenspeed FADE_FROM_WHITE, 0
	waitse
	msgbox ViridianCity_PokemonCenter_1F_Text_CenterPikachuJoinIn
	textcolor NPC_TEXT_COLOR_MALE
	msgbox ViridianCity_PokemonCenter_1F_Text_MeowthNoticesPikachu
	setvar VAR_0x8008, LOCALID_VIRIDIAN_PC_JESSIE
	setvar VAR_0x8009, LOCALID_VIRIDIAN_PC_JAMES
	setvar VAR_0x800A, LOCALID_VIRIDIAN_PC_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_VIRIDIAN_PC_JESSIE
	removeobject LOCALID_VIRIDIAN_PC_JAMES
	removeobject LOCALID_VIRIDIAN_PC_MEOWTH
	setflag FLAG_ROCKET_VIRIDIAN_PC
	fadedefaultbgm
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox ViridianCity_PokemonCenter_1F_Text_NurseThankYou
	closemessage
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox ViridianCity_PokemonCenter_1F_Text_NurseRested
	releaseall
	end

ViridianCity_PokemonCenter_1F_EventScript_Nurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse
	release
	end

ViridianCity_PokemonCenter_1F_EventScript_Boy::
	msgbox ViridianCity_PokemonCenter_1F_Text_PokeCenterInEveryTown, MSGBOX_NPC
	end

ViridianCity_PokemonCenter_1F_EventScript_Gentleman::
	msgbox ViridianCity_PokemonCenter_1F_Text_FeelFreeToUsePC, MSGBOX_NPC
	end

ViridianCity_PokemonCenter_1F_EventScript_Youngster::
	msgbox ViridianCity_PokemonCenter_1F_Text_PokeCentersHealMons, MSGBOX_NPC
	end
