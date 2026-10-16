VermilionCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VermilionCity_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, VermilionCity_OnFrame
	map_script MAP_SCRIPT_ON_RESUME, VermilionCity_OnResume
	.byte 0

@ Planes cross the sky over the airport every 30 seconds (src/airport_flyover.c).
VermilionCity_OnResume::
	special StartAirportFlyover
	end

VermilionCity_OnFrame::
	map_script_2 VAR_MAP_SCENE_VERMILION_CITY, 2, VermilionCity_EventScript_ExitSSAnne
	.2byte 0

VermilionCity_EventScript_ExitSSAnne::
	lockall
	applymovement LOCALID_PLAYER, VermilionCity_Movement_ExitSSAnne
	waitmovement 0
	setvar VAR_MAP_SCENE_VERMILION_CITY, 3
	releaseall
	end

VermilionCity_Movement_ExitSSAnne::
	walk_up
	walk_up
	step_end

VermilionCity_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_VERMILION_CITY
	call_if_set FLAG_TALKED_TO_OAKS_AIDE_IN_VERMILION, VermilionCity_EventScript_HideOaksAide
	setflag FLAG_HIDE_VERMILION_CITY_MEW
	call_if_eq VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_SOUTH, VermilionCity_EventScript_TruckPushedSouth
	call_if_eq VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_NORTH, VermilionCity_EventScript_TruckPushedNorth
	call_if_eq VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_WEST, VermilionCity_EventScript_TruckPushedWest
	call_if_eq VAR_VERMILION_CITY_TRUCK_PUSHED, DIR_EAST, VermilionCity_EventScript_TruckPushedEast
	setflag FLAG_TEMP_2
	call_if_ge VAR_MAP_SCENE_VERMILION_CITY, 3, VermilionCity_EventScript_ReadyRocketHarbor
	end

@ v0.9.0 (#4'): if the S.S. ANNE sailed before the player stopped TEAM ROCKET on
@ board (a save from before v0.5.0, or a loss on board and no second try),
@ the trio wait at the harbor, having missed the boat. Same trainer, party and
@ flag as on the ship, so only one of the two can happen.
VermilionCity_EventScript_ReadyRocketHarbor::
	goto_if_set FLAG_ROCKET_SS_ANNE, EventScript_Return
	clearflag FLAG_TEMP_2
	setvar VAR_TEMP_2, 1
	return

VermilionCity_EventScript_RocketHarbor::
	lockall
	setvar VAR_TEMP_2, 0
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterDown
	waitmovement 0
	playbgm MUS_ENCOUNTER_ROCKET, 0
	goto_if_eq VAR_ROCKET_RETRY, 4, VermilionCity_EventScript_RocketHarborRetry
	textcolor NPC_TEXT_COLOR_MALE
	msgbox VermilionCity_Text_MeowthMissedBoat
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox VermilionCity_Text_JessieBlamesJames
	textcolor NPC_TEXT_COLOR_MALE
	msgbox VermilionCity_Text_JamesGoldenEggs
	closemessage
	applymovement LOCALID_VERMILION_HARBOR_MEOWTH, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox VermilionCity_Text_MeowthSpotsPikachu
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox VermilionCity_Text_RocketHarborIntro
	closemessage
VermilionCity_EventScript_RocketHarborBattle::
	setvar VAR_0x8004, 4
	call EventScript_RocketTrioBeforeBattle
	setvar VAR_LAST_TALKED, LOCALID_VERMILION_HARBOR_JESSIE
	trainerbattle_no_intro TRAINER_JESSIE_JAMES_SS_ANNE, VermilionCity_Text_RocketHarborDefeat
	setvar VAR_ROCKET_RETRY, ROCKET_RETRY_NONE
	setvar VAR_0x8008, LOCALID_VERMILION_HARBOR_JESSIE
	setvar VAR_0x8009, LOCALID_VERMILION_HARBOR_JAMES
	setvar VAR_0x800A, LOCALID_VERMILION_HARBOR_MEOWTH
	call EventScript_RocketTrioBlastOff
	removeobject LOCALID_VERMILION_HARBOR_JESSIE
	removeobject LOCALID_VERMILION_HARBOR_MEOWTH
	removeobject LOCALID_VERMILION_HARBOR_JAMES
	setflag FLAG_ROCKET_SS_ANNE
	fadedefaultbgm
	setvar VAR_0x8004, 576
	goto_if_eq VAR_ROCKET_DOUBLES, PLAYER_HAS_TWO_USABLE_MONS, VermilionCity_EventScript_RocketHarborCoins
	setvar VAR_0x8004, 1344
VermilionCity_EventScript_RocketHarborCoins::
	call EventScript_RocketMeowthCoins
	msgbox VermilionCity_Text_JamesDroppedPouch
	giveitem ITEM_NUGGET
	setvar VAR_0x8004, ROCKET_HELD_NUGGET
	call EventScript_RocketRewardResult
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox VermilionCity_Text_MagikarpFood
	giveitem ITEM_RARE_CANDY
	setvar VAR_0x8004, ROCKET_BONUS_SS_ANNE_CANDY
	call EventScript_RocketRewardResult
	releaseall
	end

VermilionCity_EventScript_RocketHarborRetry::
	call EventScript_RocketTrioRetry
	goto VermilionCity_EventScript_RocketHarborBattle

VermilionCity_EventScript_HideOaksAide::
	setflag FLAG_HIDE_VERMILION_CITY_OAKS_AIDE
	return

VermilionCity_EventScript_Woman::
	msgbox VermilionCity_Text_GrimerMultipliesInSludge, MSGBOX_NPC
	end

VermilionCity_EventScript_OldMan1::
	lock
	faceplayer
	goto_if_eq VAR_MAP_SCENE_VERMILION_CITY, 3, VermilionCity_EventScript_OldMan1SSAnneLeft
	msgbox VermilionCity_Text_DidYouSeeSSAnneInHarbor
	release
	end

VermilionCity_EventScript_OldMan1SSAnneLeft::
	msgbox VermilionCity_Text_SSAnneHasDepartedForYear
	release
	end

VermilionCity_EventScript_FerrySailor::
	lock
	faceplayer
	goto_if_eq VAR_MAP_SCENE_VERMILION_CITY, 3, VermilionCity_EventScript_CheckSeagallopPresent
	msgbox VermilionCity_Text_WelcomeToTheSSAnne
	release
	end

VermilionCity_EventScript_CheckHasMysticTicket::
	goto_if_unset FLAG_ENABLE_SHIP_NAVEL_ROCK, EventScript_SetResultFalse
	checkitem ITEM_MYSTIC_TICKET
	goto_if_eq VAR_RESULT, FALSE, EventScript_SetResultFalse
	goto EventScript_SetResultTrue
	end

VermilionCity_EventScript_CheckHasAuroraTicket::
	goto_if_unset FLAG_ENABLE_SHIP_BIRTH_ISLAND, EventScript_SetResultFalse
	checkitem ITEM_AURORA_TICKET
	goto_if_eq VAR_RESULT, FALSE, EventScript_SetResultFalse
	goto EventScript_SetResultTrue
	end

VermilionCity_EventScript_CheckSeagallopPresent::
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	goto_if_ge VAR_MAP_SCENE_ONE_ISLAND_POKEMON_CENTER_1F, 5, VermilionCity_EventScript_ChooseSeagallopDestRainbowPass
	goto_if_ge VAR_MAP_SCENE_ONE_ISLAND_POKEMON_CENTER_1F, 1, VermilionCity_EventScript_ChooseSeagallopDestTriPass
	msgbox VermilionCity_Text_TheShipSetSail
	release
	end

VermilionCity_EventScript_ChooseSeagallopDestRainbowPass::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	call VermilionCity_EventScript_CheckHasMysticTicket
	goto_if_eq VAR_RESULT, TRUE, VermilionCity_EventScript_HasMysticTicket
	call VermilionCity_EventScript_CheckHasAuroraTicket
	goto_if_eq VAR_RESULT, TRUE, VermilionCity_EventScript_HasAuroraTicket
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	message VermilionCity_Text_BoardSeagallopRainbowPass
	waitmessage
	goto EventScript_SeviiDestinationsPage1
	end

VermilionCity_EventScript_HasMysticTicket::
	call VermilionCity_EventScript_CheckHasAuroraTicket
	goto_if_eq VAR_RESULT, TRUE, VermilionCity_EventScript_HasMysticAndAuroraTickets
	call_if_unset FLAG_SHOWN_MYSTIC_TICKET, VermilionCity_EventScript_ShowMysticTicket
	message VermilionCity_Text_BoardSeagallopFerry
	waitmessage
	multichoice 17, 6, MULTICHOICE_SEVII_NAVEL, FALSE
	switch VAR_RESULT
	case 0, EventScript_SeviiDestinationsPage1
	case 1, EventScript_SailToNavelRock
	case 2, EventScript_CancelSail
	case 127, EventScript_CancelSail
	end

VermilionCity_EventScript_ShowMysticTicket::
	setflag FLAG_SHOWN_MYSTIC_TICKET
	msgbox VermilionCity_Text_OhMysticTicketTakeYouToNavelRock
	return

VermilionCity_EventScript_HasAuroraTicket::
	call_if_unset FLAG_SHOWN_AURORA_TICKET, VermilionCity_EventScript_ShowAuroraTicket
	message VermilionCity_Text_BoardSeagallopFerry
	waitmessage
	multichoice 13, 6, MULTICHOICE_SEVII_BIRTH, FALSE
	switch VAR_RESULT
	case 0, EventScript_SeviiDestinationsPage1
	case 1, EventScript_SailToBirthIsland
	case 2, EventScript_CancelSail
	case 127, EventScript_CancelSail
	end

VermilionCity_EventScript_ShowAuroraTicket::
	setflag FLAG_SHOWN_AURORA_TICKET
	msgbox VermilionCity_Text_OhAuroraTicketTakeYouToBirthIsland
	return

VermilionCity_EventScript_HasMysticAndAuroraTickets::
	call_if_unset FLAG_SHOWN_MYSTIC_TICKET, VermilionCity_EventScript_ShowMysticTicket
	call_if_unset FLAG_SHOWN_AURORA_TICKET, VermilionCity_EventScript_ShowAuroraTicket
	message VermilionCity_Text_BoardSeagallopFerry
	waitmessage
	multichoice 13, 5, MULTICHOICE_SEVII_NAVEL_BIRTH, FALSE
	switch VAR_RESULT
	case 0, EventScript_SeviiDestinationsPage1
	case 1, EventScript_SailToNavelRock
	case 2, EventScript_SailToBirthIsland
	case 3, EventScript_CancelSail
	case 127, EventScript_CancelSail
	end

EventScript_SailToNavelRock::
	msgbox VermilionCity_Text_Seagallop10Departing
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	setvar VAR_0x8006, SEAGALLOP_NAVEL_ROCK
	goto EventScript_SetSail
	end

EventScript_SailToBirthIsland::
	msgbox VermilionCity_Text_Seagallop12Departing
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	setvar VAR_0x8006, SEAGALLOP_BIRTH_ISLAND
	goto EventScript_SetSail
	end

VermilionCity_EventScript_ChooseSeagallopDestTriPass::
	message VermilionCity_Text_BoardSeagallopTriPass
	waitmessage
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	multichoice 19, 5, MULTICHOICE_SEAGALLOP_123, FALSE
	switch VAR_RESULT
	case 0, EventScript_SailToOneIsland2
	case 1, EventScript_SailToTwoIsland2
	case 2, EventScript_SailToThreeIsland2
	case 3, EventScript_CancelSail
	case 127, EventScript_CancelSail
	end

@ Unreachable
Vermilion_EventScript_Unused::
	release
	end

VermilionCity_EventScript_CheckTicketLeft::
	lockall
	goto VermilionCity_EventScript_CheckTicket
	end

VermilionCity_EventScript_CheckTicketRight::
	lockall
	goto VermilionCity_EventScript_CheckTicket
	end

VermilionCity_EventScript_ExitedTicketCheck::
	lockall
	setvar VAR_VERMILION_CITY_TICKET_CHECK_TRIGGER, 0
	releaseall
	end

VermilionCity_EventScript_CheckTicket::
	textcolor NPC_TEXT_COLOR_MALE
	applymovement LOCALID_VERMILION_FERRY_SAILOR, Common_Movement_WalkInPlaceFasterLeft
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterRight
	waitmovement 0
	goto_if_eq VAR_MAP_SCENE_VERMILION_CITY, 3, VermilionCity_EventScript_CheckSeagallopPresentTrigger
	msgbox VermilionCity_Text_DoYouHaveATicket
	goto_if_unset FLAG_GOT_SS_TICKET, VermilionCity_EventScript_DontHaveSSTicket
	msgbox VermilionCity_Text_FlashedSSTicket
	setvar VAR_VERMILION_CITY_TICKET_CHECK_TRIGGER, 1
	releaseall
	end

VermilionCity_EventScript_DontHaveSSTicket::
	msgbox VermilionCity_Text_DontHaveNeededSSTicket
	closemessage
	goto VermilionCity_EventScript_WalkUpPier
	end

VermilionCity_EventScript_CheckSeagallopPresentTrigger::
	setvar VAR_0x8004, SEAGALLOP_VERMILION_CITY
	goto_if_ge VAR_MAP_SCENE_ONE_ISLAND_POKEMON_CENTER_1F, 5, VermilionCity_EventScript_ChooseSeagallopDestRainbowPass
	goto_if_ge VAR_MAP_SCENE_ONE_ISLAND_POKEMON_CENTER_1F, 1, VermilionCity_EventScript_ChooseSeagallopDestTriPass
	msgbox VermilionCity_Text_ShipSetSailDockStillOpen
	goto VermilionCity_EventScript_LetPlayerOntoPier
	end

@ After the S.S. ANNE has sailed, the dock stays open to look around
VermilionCity_EventScript_LetPlayerOntoPier::
	closemessage
	applymovement LOCALID_VERMILION_FERRY_SAILOR, Common_Movement_FaceOriginalDirection
	waitmovement 0
	setvar VAR_VERMILION_CITY_TICKET_CHECK_TRIGGER, 1
	releaseall
	end

VermilionCity_EventScript_Sailor::
	lock
	faceplayer
	goto_if_set FLAG_ROCKET_NEW_ISLAND, VermilionCity_EventScript_SailorFogLifted
	goto_if_set FLAG_FOUGHT_MEWTWO, VermilionCity_EventScript_SailorNewIsland
	msgbox VermilionCity_Text_SSAnneVisitsOnceAYear
	release
	end

@ v0.5.0 TEAM ROCKET event 11: the way to NEW ISLAND (foggy nights only).
VermilionCity_EventScript_SailorNewIsland::
	special BufferGameClock
	goto_if_ne VAR_RESULT, TIME_NIGHT, VermilionCity_EventScript_SailorComeAtNight
	msgbox VermilionCity_Text_SailorIslandInFog, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VermilionCity_EventScript_SailorMaybeLater
	msgbox VermilionCity_Text_SailorLetsGo
	closemessage
	fadescreen FADE_TO_BLACK
	playse SE_EXIT
	warp MAP_NEW_ISLAND, 6, 12
	waitstate
	release
	end

VermilionCity_EventScript_SailorComeAtNight::
	msgbox VermilionCity_Text_SailorComeAtNight
	release
	end

VermilionCity_EventScript_SailorMaybeLater::
	msgbox VermilionCity_Text_SailorMaybeLater
	release
	end

VermilionCity_EventScript_SailorFogLifted::
	msgbox VermilionCity_Text_SailorFogLifted
	release
	end

VermilionCity_EventScript_OaksAide::
	lock
	faceplayer
	setflag FLAG_TALKED_TO_OAKS_AIDE_IN_VERMILION
	msgbox VermilionCity_Text_Route2AideHasPackageForYou
	release
	end

VermilionCity_EventScript_OldMan2::
	msgbox VermilionCity_Text_BuildingOnThisLand, MSGBOX_NPC
	end

VermilionCity_EventScript_Machop::
	lock
	faceplayer
	waitse
	playmoncry SPECIES_MACHOP, CRY_MODE_NORMAL
	msgbox VermilionCity_Text_Machop
	waitmoncry
	msgbox VermilionCity_Text_MachopStompingLandFlat
	release
	end

VermilionCity_EventScript_CitySign::
	msgbox VermilionCity_Text_CitySign, MSGBOX_SIGN
	end

VermilionCity_EventScript_SnorlaxNotice::
	msgbox VermilionCity_Text_SnorlaxBlockingRoute12, MSGBOX_SIGN
	end

VermilionCity_EventScript_PokemonFanClubSign::
	msgbox VermilionCity_Text_PokemonFanClubSign, MSGBOX_SIGN
	end

VermilionCity_EventScript_GymSign::
	lockall
	famechecker FAMECHECKER_LTSURGE, 0
	msgbox VermilionCity_Text_GymSign
	releaseall
	end

VermilionCity_EventScript_HarborSign::
	msgbox VermilionCity_Text_VermilionHarbor, MSGBOX_SIGN
	end

@ Yellow's Officer Jenny. She hands over SQUIRTLE once the player has the THUNDERBADGE.
VermilionCity_EventScript_Officer::
	lock
	faceplayer
	goto_if_set FLAG_GOT_SQUIRTLE_FROM_OFFICER, VermilionCity_EventScript_OfficerAlreadyGaveSquirtle
	goto_if_set FLAG_BADGE03_GET, VermilionCity_EventScript_OfficerOfferSquirtle
	msgbox VermilionCity_Text_SquirtleNeedsGoodTrainer
	release
	end

VermilionCity_EventScript_OfficerOfferSquirtle::
	msgbox VermilionCity_Text_YouHaveThunderBadge, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VermilionCity_EventScript_OfficerDeclined
	goto VermilionCity_EventScript_GiveSquirtle
	end

VermilionCity_EventScript_OfficerDeclined::
	msgbox VermilionCity_Text_WhatAmIToDoNow
	release
	end

VermilionCity_EventScript_OfficerAlreadyGaveSquirtle::
	msgbox VermilionCity_Text_HowIsSquirtleDoing
	release
	end

VermilionCity_EventScript_GiveSquirtle::
	setvar VAR_TEMP_1, SPECIES_SQUIRTLE
	givemon SPECIES_SQUIRTLE, 10
	goto_if_eq VAR_RESULT, 0, VermilionCity_EventScript_ReceiveSquirtleParty
	goto_if_eq VAR_RESULT, 1, VermilionCity_EventScript_ReceiveSquirtlePC
	goto_if_eq VAR_RESULT, 2, EventScript_NoMoreRoomForPokemon
	release
	end

VermilionCity_EventScript_ReceiveSquirtleParty::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message VermilionCity_Text_ReceivedSquirtle
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_SQUIRTLE
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VermilionCity_EventScript_EndReceiveSquirtle
	call EventScript_GetGiftMonPartySlot
	call EventScript_ChangePokemonNickname
	goto VermilionCity_EventScript_EndReceiveSquirtle
	end

VermilionCity_EventScript_ReceiveSquirtlePC::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_LEVEL_UP
	message VermilionCity_Text_ReceivedSquirtle
	waitmessage
	waitfanfare
	bufferspeciesname STR_VAR_1, SPECIES_SQUIRTLE
	msgbox Text_GiveNicknameToThisMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VermilionCity_EventScript_SquirtleTransferredToPC
	call EventScript_NameReceivedBoxMon
	goto VermilionCity_EventScript_SquirtleTransferredToPC
	end

VermilionCity_EventScript_SquirtleTransferredToPC::
	call EventScript_TransferredToPC
	goto VermilionCity_EventScript_EndReceiveSquirtle
	end

VermilionCity_EventScript_EndReceiveSquirtle::
	textcolor NPC_TEXT_COLOR_MALE
	msgbox VermilionCity_Text_PleaseTreatSquirtleRight
	setflag FLAG_GOT_SQUIRTLE_FROM_OFFICER
	release
	end

VermilionCity_EventScript_TruckPushedSouth::
	setobjectxyperm LOCALID_VERMILION_TRUCK, 27, 30
	return

VermilionCity_EventScript_TruckPushedNorth::
	setobjectxyperm LOCALID_VERMILION_TRUCK, 27, 28
	return

VermilionCity_EventScript_TruckPushedWest::
	setobjectxyperm LOCALID_VERMILION_TRUCK, 26, 29
	return

VermilionCity_EventScript_TruckPushedEast::
	setobjectxyperm LOCALID_VERMILION_TRUCK, 28, 29
	return

@ Pokémon Yellow's truck, parked on the quay east of the harbor, with Mew hiding under it.
@ Once the ship has sailed, a Pokémon that knows STRENGTH can push the truck
@ aside and Mew jumps out of the spot it covered.
VermilionCity_EventScript_Truck::
	goto_if_questlog EventScript_ReleaseEnd
	lockall
	goto_if_set FLAG_GOT_MEW_EGG, VermilionCity_EventScript_TruckMewGone
	goto_if_set FLAG_FOUGHT_MEW, VermilionCity_EventScript_TruckWontBudge
	goto_if_lt VAR_MAP_SCENE_VERMILION_CITY, 3, VermilionCity_EventScript_TruckWontBudge
	checkpartymove MOVE_STRENGTH
	goto_if_eq VAR_RESULT, PARTY_SIZE, VermilionCity_EventScript_TruckWontBudge
	setfieldeffectargument 0, VAR_RESULT
	setvar VAR_0x8004, LOCALID_VERMILION_TRUCK
	setvar VAR_0x8005, 0
	setvar VAR_0x8009, 0
	specialvar VAR_RESULT, CanPushTruck
	goto_if_eq VAR_RESULT, FALSE, VermilionCity_EventScript_TruckWontBudge
	msgbox VermilionCity_Text_TruckLooksHeavy, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, VermilionCity_EventScript_DontPushTruck
	closemessage
	special QuestLog_CutRecording
	dofieldeffect FLDEFF_USE_STRENGTH
	waitstate
	special PushTruck
	waitstate
	delay 16
	setobjectxyperm LOCALID_VERMILION_MEW, VAR_0x8006, VAR_0x8007
	addobject LOCALID_VERMILION_MEW
	specialvar VAR_RESULT, GetPlayerFacingDirection
	copyvar VAR_0x8008, VAR_RESULT
	call_if_eq VAR_RESULT, DIR_SOUTH, VermilionCity_EventScript_MewJumpsOutUp
	call_if_eq VAR_RESULT, DIR_NORTH, VermilionCity_EventScript_MewJumpsOutDown
	call_if_eq VAR_RESULT, DIR_WEST, VermilionCity_EventScript_MewJumpsOutRight
	call_if_eq VAR_RESULT, DIR_EAST, VermilionCity_EventScript_MewJumpsOutLeft
	applymovement LOCALID_VERMILION_MEW, Common_Movement_ExclamationMark
	waitmovement 0
	waitse
	playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 20
	setwildbattle SPECIES_MEW, 30
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	setflag FLAG_FOUGHT_MEW
	copyvar VAR_VERMILION_CITY_TRUCK_PUSHED, VAR_0x8008
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, VermilionCity_EventScript_MewFledAway
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, VermilionCity_EventScript_MewFledAway
	goto_if_eq VAR_RESULT, B_OUTCOME_MON_FLED, VermilionCity_EventScript_MewFledAway
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_VERMILION_MEW
	fadescreen FADE_FROM_BLACK
	releaseall
	end

VermilionCity_EventScript_MewFledAway::
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_VERMILION_MEW
	fadescreen FADE_FROM_BLACK
	bufferspeciesname STR_VAR_1, SPECIES_MEW
	msgbox Text_MonFlewAway
	releaseall
	end

VermilionCity_EventScript_MewJumpsOutUp::
	applymovement LOCALID_VERMILION_MEW, VermilionCity_Movement_MewJumpOutUp
	waitmovement 0
	return

VermilionCity_EventScript_MewJumpsOutDown::
	applymovement LOCALID_VERMILION_MEW, VermilionCity_Movement_MewJumpOutDown
	waitmovement 0
	return

VermilionCity_EventScript_MewJumpsOutRight::
	applymovement LOCALID_VERMILION_MEW, VermilionCity_Movement_MewJumpOutRight
	waitmovement 0
	return

VermilionCity_EventScript_MewJumpsOutLeft::
	applymovement LOCALID_VERMILION_MEW, VermilionCity_Movement_MewJumpOutLeft
	waitmovement 0
	return

@ v0.9.0: the player took the MEW EGG from the NEW ISLAND lab.
VermilionCity_EventScript_TruckMewGone::
	msgbox VermilionCity_Text_TruckPinkHair
	releaseall
	end

VermilionCity_EventScript_TruckWontBudge::
	msgbox VermilionCity_Text_TruckWontBudge
	releaseall
	end

VermilionCity_EventScript_DontPushTruck::
	closemessage
	releaseall
	end

VermilionCity_Movement_MewJumpOutUp::
	jump_in_place_up
	step_end

VermilionCity_Movement_MewJumpOutDown::
	jump_in_place_down
	step_end

VermilionCity_Movement_MewJumpOutRight::
	jump_in_place_right
	step_end

VermilionCity_Movement_MewJumpOutLeft::
	jump_in_place_left
	step_end

VermilionCity_EventScript_AirportSign::
	msgbox VermilionCity_Text_AirportSign, MSGBOX_SIGN
	end
