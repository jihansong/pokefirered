MauvilleCity_BikeShop_MapScripts::
	.byte 0

MauvilleCity_BikeShop_EventScript_H0::
	msgbox MauvilleCity_BikeShop_Text_H0, MSGBOX_NPC
	end

MauvilleCity_BikeShop_EventScript_H1::
	msgbox MauvilleCity_BikeShop_Text_H1, MSGBOX_NPC
	end

MauvilleCity_BikeShop_EventScript_H2::
	msgbox MauvilleCity_BikeShop_Text_H2, MSGBOX_SIGN
	end

MauvilleCity_BikeShop_EventScript_H3::
	msgbox MauvilleCity_BikeShop_Text_H3, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Root owns atomic item transaction/receipt/registration; this script never gives/removes items itself.
MauvilleCity_BikeShop_EventScript_Rydel::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	msgbox MauvilleCity_BikeShop_Text_H0, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Service

MauvilleCity_BikeShop_EventScript_Service::
	message MauvilleCity_BikeShop_Text_Service
	waitmessage
	multichoice 0, 0, MULTI_TY_RYDEL_SERVICE, FALSE
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_Exchange
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_Record
	goto_if_eq VAR_RESULT, 2, MauvilleCity_BikeShop_EventScript_Guide
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_Exchange::
	special GetRydelBikeState
	goto_if_eq VAR_RESULT, 3, MauvilleCity_BikeShop_EventScript_BothBikes
	goto_if_ne VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_AskExchange
	goto_if_set FLAG_HOENN_RYDEL_BIKE_RECEIVED, MauvilleCity_BikeShop_EventScript_BringBike
	msgbox MauvilleCity_BikeShop_Text_FirstOffer, MSGBOX_YESNO
	goto_if_ne VAR_RESULT, YES, MauvilleCity_BikeShop_EventScript_Bye
	goto MauvilleCity_BikeShop_EventScript_ChooseBike

MauvilleCity_BikeShop_EventScript_AskExchange::
	msgbox MauvilleCity_BikeShop_Text_AskExchange, MSGBOX_YESNO
	goto_if_ne VAR_RESULT, YES, MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_ChooseBike::
	message MauvilleCity_BikeShop_Text_ChooseBike
	waitmessage
	multichoice 0, 0, MULTI_TY_RYDEL_BIKE, FALSE
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_ChooseMach
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_ChooseAcro
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_ChooseMach::
	setvar VAR_0x8004, ITEM_MACH_BIKE
	goto MauvilleCity_BikeShop_EventScript_Commit

MauvilleCity_BikeShop_EventScript_ChooseAcro::
	setvar VAR_0x8004, ITEM_ACRO_BIKE

MauvilleCity_BikeShop_EventScript_Commit::
	bufferitemname STR_VAR_1, VAR_0x8004
	special CommitRydelBike
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_Received
	goto_if_eq VAR_RESULT, 2, MauvilleCity_BikeShop_EventScript_AlreadyOwned
	msgbox MauvilleCity_BikeShop_Text_NoRoom, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_Received::
	playfanfare MUS_OBTAIN_KEY_ITEM
	msgbox MauvilleCity_BikeShop_Text_Received, MSGBOX_DEFAULT
	waitfanfare
	msgbox MauvilleCity_BikeShop_Text_ComeBack, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_AlreadyOwned::
	msgbox MauvilleCity_BikeShop_Text_AlreadyOwned, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_BothBikes::
	msgbox MauvilleCity_BikeShop_Text_BothBikes, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Bye

MauvilleCity_BikeShop_EventScript_BringBike::
	msgbox MauvilleCity_BikeShop_Text_BringBike, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_Bye

@ Existing Cycling Road record service and its three dialogue strings are preserved.
MauvilleCity_BikeShop_EventScript_Record::
	special CyclingRoad_GetRecord
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_NoRecord
	buffernumberstring STR_VAR_1, VAR_RESULT
	goto_if_le VAR_RESULT, 60, MauvilleCity_BikeShop_EventScript_RecordGold
	msgbox MauvilleCity_BikeShop_Text_Record
	release
	end

MauvilleCity_BikeShop_EventScript_RecordGold::
	msgbox MauvilleCity_BikeShop_Text_RecordGold
	release
	end

MauvilleCity_BikeShop_EventScript_NoRecord::
	msgbox MauvilleCity_BikeShop_Text_NoRecord
	release
	end

MauvilleCity_BikeShop_EventScript_Guide::
	message MauvilleCity_BikeShop_Text_ChooseGuide
	waitmessage
	multichoice 0, 0, MULTI_TY_RYDEL_BIKE, FALSE
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_GuideMach
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_GuideAcro
	goto MauvilleCity_BikeShop_EventScript_Service

MauvilleCity_BikeShop_EventScript_GuideMach::
	call MauvilleCity_BikeShop_EventScript_MachPages
	goto MauvilleCity_BikeShop_EventScript_Service

MauvilleCity_BikeShop_EventScript_GuideAcro::
	call MauvilleCity_BikeShop_EventScript_AcroPages
	goto MauvilleCity_BikeShop_EventScript_Service

MauvilleCity_BikeShop_EventScript_Bye::
	release
	end

@ Existing two sign-event indices are retained; these are their new target labels.
MauvilleCity_BikeShop_EventScript_MachBikeHandbook::
	goto_if_questlog EventScript_ReleaseEnd
	lockall
	call MauvilleCity_BikeShop_EventScript_MachPages
	releaseall
	end

MauvilleCity_BikeShop_EventScript_AcroBikeHandbook::
	goto_if_questlog EventScript_ReleaseEnd
	lockall
	call MauvilleCity_BikeShop_EventScript_AcroPages
	releaseall
	end

MauvilleCity_BikeShop_EventScript_MachPages::
	message MauvilleCity_BikeShop_Text_MachHandbookWhichPage
	waitmessage
	multichoice 0, 0, MULTI_TY_MACH_INFO, FALSE
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_MachRide
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_MachTurn
	goto_if_eq VAR_RESULT, 2, MauvilleCity_BikeShop_EventScript_MachSlopes
	return

MauvilleCity_BikeShop_EventScript_MachRide::
	msgbox MauvilleCity_BikeShop_Text_HowToRideMachBike, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_MachPages

MauvilleCity_BikeShop_EventScript_MachTurn::
	msgbox MauvilleCity_BikeShop_Text_HowToTurnMachBike, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_MachPages

MauvilleCity_BikeShop_EventScript_MachSlopes::
	msgbox MauvilleCity_BikeShop_Text_SandySlopes, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_MachPages

MauvilleCity_BikeShop_EventScript_AcroPages::
	message MauvilleCity_BikeShop_Text_AcroHandbookWhichPage
	waitmessage
	multichoice 0, 0, MULTI_TY_ACRO_INFO, FALSE
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_AcroWheelies
	goto_if_eq VAR_RESULT, 1, MauvilleCity_BikeShop_EventScript_AcroHops
	goto_if_eq VAR_RESULT, 2, MauvilleCity_BikeShop_EventScript_AcroJumps
	return

MauvilleCity_BikeShop_EventScript_AcroWheelies::
	msgbox MauvilleCity_BikeShop_Text_Wheelies, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_AcroPages

MauvilleCity_BikeShop_EventScript_AcroHops::
	msgbox MauvilleCity_BikeShop_Text_BunnyHops, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_AcroPages

MauvilleCity_BikeShop_EventScript_AcroJumps::
	msgbox MauvilleCity_BikeShop_Text_Jumps, MSGBOX_DEFAULT
	goto MauvilleCity_BikeShop_EventScript_AcroPages
@ END PATCH
