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
	setflag FLAG_TEMP_2
	goto_if_unset FLAG_RECEIVED_STARTER_PIKACHU, EventScript_Return
	setvar VAR_TEMP_1, 1
	return

@ Thunder Yellow v0.5.0, TEAM ROCKET event 1: the first time the player walks into
@ the VIRIDIAN POKéMON CENTER with PIKACHU, JESSIE, JAMES and MEOWTH raid it, and the
@ PIKACHU there drive them off with a THUNDERBOLT. MEOWTH notices the player's
@ PIKACHU is no ordinary one, which is why the trio keep turning up after it.
@ v0.9.0 (#1): MEOWTH first takes PIKACHU on alone. Like the rival's first
@ battles (trainerbattle_earlyrival) a loss doesn't white out: the party is
@ healed and the scene goes on either way.
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
	textcolor NPC_TEXT_COLOR_MALE
	msgbox ViridianCity_PokemonCenter_1F_Text_MeowthSizesUp
	closemessage
	setvar VAR_LAST_TALKED, LOCALID_VIRIDIAN_PC_MEOWTH
	trainerbattle_earlyrival TRAINER_JESSIE_JAMES_VIRIDIAN_PC, RIVAL_BATTLE_HEAL_AFTER, ViridianCity_PokemonCenter_1F_Text_MeowthDefeat, ViridianCity_PokemonCenter_1F_Text_MeowthVictory
	call_if_eq VAR_RESULT, FALSE, ViridianCity_PokemonCenter_1F_EventScript_MeowthLost
	call_if_eq VAR_RESULT, TRUE, ViridianCity_PokemonCenter_1F_EventScript_PikachuGetsUp
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

ViridianCity_PokemonCenter_1F_EventScript_MeowthLost::
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox ViridianCity_PokemonCenter_1F_Text_JessieMeowthLost
	return

ViridianCity_PokemonCenter_1F_EventScript_PikachuGetsUp::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox ViridianCity_PokemonCenter_1F_Text_PikachuGetsUp
	return

@ v0.9.0: the OFFICER on the TEAM ROCKET trio case. He hands over what the
@ trio left behind: rewards added in v0.9.0 for events a save had already
@ played (VAR_ROCKET_BONUS_GIVEN bit clear), and rewards the bag had no room
@ for at the time (VAR_ROCKET_REWARD_HELD bit set). He stops at the first one
@ that doesn't fit and keeps the rest. Here from the visit after the raid.
ViridianCity_PokemonCenter_1F_EventScript_Officer::
	lock
	faceplayer
	msgbox ViridianCity_PokemonCenter_1F_Text_OfficerIntro
	setvar VAR_TEMP_2, 0  @ things handed over
	setvar VAR_TEMP_3, 0  @ 1 = no room, stopped
	setvar VAR_TEMP_4, 0  @ 1 = has said "these belong to you"
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerWaterStone
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerSSAnneCandy
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerThunderStone
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerCleanseTag
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerLeafStone
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerUpGrade
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerDragonScale
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerCinnabarCandy
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGymCandy
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerEeveeEgg
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerFireStone
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerNewIsland
	setvar VAR_0x8004, ROCKET_HELD_MYSTIC_WATER
	setvar VAR_0x8005, ITEM_MYSTIC_WATER
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	setvar VAR_0x8004, ROCKET_HELD_NUGGET
	setvar VAR_0x8005, ITEM_NUGGET
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	setvar VAR_0x8004, ROCKET_HELD_MIRACLE_SEED
	setvar VAR_0x8005, ITEM_MIRACLE_SEED
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	setvar VAR_0x8004, ROCKET_HELD_DRAGON_FANG
	setvar VAR_0x8005, ITEM_DRAGON_FANG
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	setvar VAR_0x8004, ROCKET_HELD_FULL_RESTORE
	setvar VAR_0x8005, ITEM_FULL_RESTORE
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	setvar VAR_0x8004, ROCKET_HELD_CARGO_TAG
	setvar VAR_0x8005, ITEM_CARGO_TAG
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld
	textcolor NPC_TEXT_COLOR_MALE
	goto_if_eq VAR_TEMP_3, 1, ViridianCity_PokemonCenter_1F_EventScript_OfficerComeBack
	goto_if_eq VAR_TEMP_2, 0, ViridianCity_PokemonCenter_1F_EventScript_OfficerNothing
	release
	end

ViridianCity_PokemonCenter_1F_EventScript_OfficerComeBack::
	msgbox ViridianCity_PokemonCenter_1F_Text_OfficerComeBack
	release
	end

ViridianCity_PokemonCenter_1F_EventScript_OfficerNothing::
	msgbox ViridianCity_PokemonCenter_1F_Text_OfficerNothing
	release
	end

@ Each reward: the event it belongs to must be over (the same test the
@ event itself uses), then VAR_0x8004 = its bit, VAR_0x8005 = the item and
@ VAR_0x8006 = how many.
ViridianCity_PokemonCenter_1F_EventScript_OfficerWaterStone::
	goto_if_unset FLAG_ROCKET_CERULEAN_GYM, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_WATER_STONE
	setvar VAR_0x8005, ITEM_WATER_STONE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerSSAnneCandy::
	goto_if_unset FLAG_ROCKET_SS_ANNE, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_SS_ANNE_CANDY
	setvar VAR_0x8005, ITEM_RARE_CANDY
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerThunderStone::
	goto_if_not_defeated TRAINER_JESSIE_JAMES_ROCKET_HIDEOUT, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_THUNDER_STONE
	setvar VAR_0x8005, ITEM_THUNDER_STONE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerCleanseTag::
	goto_if_not_defeated TRAINER_JESSIE_JAMES_POKEMON_TOWER, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_CLEANSE_TAG
	setvar VAR_0x8005, ITEM_CLEANSE_TAG
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerLeafStone::
	goto_if_unset FLAG_ROCKET_CELADON_GYM, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_LEAF_STONE
	setvar VAR_0x8005, ITEM_LEAF_STONE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerUpGrade::
	goto_if_not_defeated TRAINER_JESSIE_JAMES_SILPH_CO, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_UP_GRADE
	setvar VAR_0x8005, ITEM_UP_GRADE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerDragonScale::
	goto_if_unset FLAG_ROCKET_SAFARI_DRATINI, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_DRAGON_SCALE
	setvar VAR_0x8005, ITEM_DRAGON_SCALE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerCinnabarCandy::
	goto_if_unset FLAG_ROCKET_CINNABAR, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_CINNABAR_CANDY
	setvar VAR_0x8005, ITEM_RARE_CANDY
	setvar VAR_0x8006, 2
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerGymCandy::
	goto_if_unset FLAG_ROCKET_VIRIDIAN_GYM, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_GYM_CANDY
	setvar VAR_0x8005, ITEM_RARE_CANDY
	setvar VAR_0x8006, 3
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerFireStone::
	goto_if_unset FLAG_ROCKET_INDIGO_TORCH, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_FIRE_STONE
	setvar VAR_0x8005, ITEM_FIRE_STONE
	setvar VAR_0x8006, 1
	goto ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus

ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus::
	goto_if_eq VAR_TEMP_3, 1, EventScript_Return
	special CheckRocketRewardBit
	goto_if_eq VAR_RESULT, TRUE, EventScript_Return
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerHandOver
	giveitem VAR_0x8005, VAR_0x8006
	goto_if_eq VAR_0x8007, FALSE, ViridianCity_PokemonCenter_1F_EventScript_OfficerNoRoom
	special SetRocketRewardBit
	addvar VAR_TEMP_2, 1
	return

@ An old reward the bag had no room for: VAR_0x8004 = its held bit,
@ VAR_0x8005 = the item.
ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveHeld::
	goto_if_eq VAR_TEMP_3, 1, EventScript_Return
	special CheckRocketRewardBit
	goto_if_eq VAR_RESULT, FALSE, EventScript_Return
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerHandOver
	giveitem VAR_0x8005
	goto_if_eq VAR_0x8007, FALSE, ViridianCity_PokemonCenter_1F_EventScript_OfficerNoRoom
	special ClearRocketRewardBit
	addvar VAR_TEMP_2, 1
	return

ViridianCity_PokemonCenter_1F_EventScript_OfficerEeveeEgg::
	goto_if_unset FLAG_ROCKET_VIRIDIAN_GYM, EventScript_Return
	goto_if_eq VAR_TEMP_3, 1, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_EEVEE_EGG
	special CheckRocketRewardBit
	goto_if_eq VAR_RESULT, TRUE, EventScript_Return
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerHandOver
	giveegg SPECIES_EEVEE
	goto_if_eq VAR_RESULT, 2, ViridianCity_PokemonCenter_1F_EventScript_OfficerNoRoom
	call EventScript_RocketEggResult
	setvar VAR_0x8004, ROCKET_BONUS_EEVEE_EGG
	special SetRocketRewardBit
	addvar VAR_TEMP_2, 1
	return

@ NEW ISLAND: the MEW EGG if MEW is still under the truck, or the RARE CANDY
@ left beside the empty shell.
ViridianCity_PokemonCenter_1F_EventScript_OfficerNewIsland::
	goto_if_unset FLAG_ROCKET_NEW_ISLAND, EventScript_Return
	setvar VAR_0x8004, ROCKET_BONUS_NEW_ISLAND
	setvar VAR_0x8005, ITEM_RARE_CANDY
	setvar VAR_0x8006, 3
	goto_if_set FLAG_FOUGHT_MEW, ViridianCity_PokemonCenter_1F_EventScript_OfficerGiveBonus
	goto_if_eq VAR_TEMP_3, 1, EventScript_Return
	special CheckRocketRewardBit
	goto_if_eq VAR_RESULT, TRUE, EventScript_Return
	call ViridianCity_PokemonCenter_1F_EventScript_OfficerHandOver
	textcolor NPC_TEXT_COLOR_MALE
	msgbox ViridianCity_PokemonCenter_1F_Text_OfficerMewEgg
	specialvar VAR_RESULT, GiveMewEgg
	goto_if_eq VAR_RESULT, 2, ViridianCity_PokemonCenter_1F_EventScript_OfficerNoRoom
	call EventScript_RocketEggResult
	call EventScript_GotMewEgg
	addvar VAR_TEMP_2, 1
	return

ViridianCity_PokemonCenter_1F_EventScript_OfficerHandOver::
	goto_if_eq VAR_TEMP_4, 1, EventScript_Return
	setvar VAR_TEMP_4, 1
	textcolor NPC_TEXT_COLOR_MALE
	msgbox ViridianCity_PokemonCenter_1F_Text_OfficerHandOver
	return

ViridianCity_PokemonCenter_1F_EventScript_OfficerNoRoom::
	setvar VAR_TEMP_3, 1
	return

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
