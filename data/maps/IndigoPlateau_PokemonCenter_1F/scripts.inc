IndigoPlateau_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IndigoPlateau_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

IndigoPlateau_PokemonCenter_1F_OnTransition::
	setrespawn HEAL_LOCATION_INDIGO_PLATEAU
	specialvar VAR_RESULT, IsNationalPokedexEnabled
	call_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_CheckBlockDoor
	call IndigoPlateau_PokemonCenter_1F_EventScript_CheckTorchStolen
	goto_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_BlockDoor
	end

@ v0.9.0: TEAM ROCKET run off with the INDIGO TORCH when the player first comes
@ with eight badges (IndigoPlateau_Exterior). Until the player wins it back
@ outside, no challenge starts: the guard stands in the doorway.
IndigoPlateau_PokemonCenter_1F_EventScript_CheckTorchStolen::
	setvar VAR_RESULT, FALSE
	goto_if_unset FLAG_BADGE08_GET, EventScript_Return
	goto_if_set FLAG_ROCKET_INDIGO_TORCH, EventScript_Return
	setvar VAR_RESULT, TRUE
	return

IndigoPlateau_PokemonCenter_1F_EventScript_BlockDoor::
	setobjectxyperm LOCALID_LEAGUE_DOOR_GUARD, 4, 2
	end

IndigoPlateau_PokemonCenter_1F_EventScript_CheckBlockDoor::
	goto_if_set FLAG_SYS_CAN_LINK_WITH_RS, EventScript_Return
	setobjectxyperm LOCALID_LEAGUE_DOOR_GUARD, 4, 2
	return

IndigoPlateau_PokemonCenter_1F_EventScript_DoorGuard::
	lock
	faceplayer
	call IndigoPlateau_PokemonCenter_1F_EventScript_CheckTorchStolen
	goto_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_TorchStolen
	specialvar VAR_RESULT, IsNationalPokedexEnabled
	goto_if_eq VAR_RESULT, TRUE, IndigoPlateau_PokemonCenter_1F_EventScript_CheckSeviiIslandComplete
	msgbox IndigoPlateau_PokemonCenter_1F_Text_FaceEliteFourGoodLuck
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_TorchStolen::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_TorchStolen
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_CheckSeviiIslandComplete::
	goto_if_set FLAG_SYS_CAN_LINK_WITH_RS, IndigoPlateau_PokemonCenter_1F_EventScript_SeviiIslandComplete
	msgbox IndigoPlateau_PokemonCenter_1F_Text_LoreleiIsAbsentClosedForTimeBeing
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_SeviiIslandComplete::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_FaceEliteFourGoodLuck
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_GymGuy::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_GymGuyAdvice, MSGBOX_NPC
	end

IndigoPlateau_PokemonCenter_1F_EventScript_Clerk::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart IndigoPlateau_PokemonCenter_1F_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
IndigoPlateau_PokemonCenter_1F_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_FULL_RESTORE
	.2byte ITEM_MAX_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_NONE
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_Nurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse
	release
	end

@ v0.6.0: the way into the CHAMPION TOURNAMENT next door.
IndigoPlateau_PokemonCenter_1F_EventScript_TourneyReceptionist::
	lock
	faceplayer
	goto_if_unset FLAG_SYS_GAME_CLEAR, IndigoPlateau_PokemonCenter_1F_EventScript_TourneyClosed
	goto_if_unset FLAG_RECOVERED_SAPPHIRE, IndigoPlateau_PokemonCenter_1F_EventScript_TourneyClosed
	msgbox IndigoPlateau_PokemonCenter_1F_Text_TourneyWelcome, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, IndigoPlateau_PokemonCenter_1F_EventScript_TourneyLater
	closemessage
	warp MAP_TOURNAMENT_HALL, 8, 16
	waitstate
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_TourneyLater::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_TourneyLater
	release
	end

IndigoPlateau_PokemonCenter_1F_EventScript_TourneyClosed::
	msgbox IndigoPlateau_PokemonCenter_1F_Text_TourneyClosed
	release
	end
