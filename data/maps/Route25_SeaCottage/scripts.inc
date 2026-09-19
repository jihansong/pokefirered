.equ BILL_IN_TELEPORTER,     FLAG_TEMP_2
.equ RETURN_AFTER_SS_TICKET, FLAG_TEMP_3

Route25_SeaCottage_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route25_SeaCottage_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Route25_SeaCottage_OnFrame
	.byte 0

Route25_SeaCottage_OnFrame::
	map_script_2 VAR_SEA_COTTAGE_TELEPORT, 1, Route25_SeaCottage_EventScript_TeleporterTransform
	map_script_2 VAR_SEA_COTTAGE_TELEPORT, 2, Route25_SeaCottage_EventScript_TeleporterChangeBack
	.2byte 0

Route25_SeaCottage_OnTransition::
	call_if_unset FLAG_HELPED_BILL_IN_SEA_COTTAGE, Route25_SeaCottage_EventScript_HideClefairyBill
	call_if_set FLAG_GOT_SS_TICKET, Route25_SeaCottage_EventScript_SetReturnedAfterSSTicket
	end

Route25_SeaCottage_EventScript_HideClefairyBill::
	clearflag FLAG_HIDE_BILL_CLEFAIRY
	setobjectxyperm LOCALID_BILL_HUMAN, 3, 3
	return

Route25_SeaCottage_EventScript_SetReturnedAfterSSTicket::
	setflag RETURN_AFTER_SS_TICKET
	return

Route25_SeaCottage_EventScript_Bill::
	lock
	faceplayer
	call_if_set FLAG_SYS_GAME_CLEAR, Route25_SeaCottage_EventScript_BillCheckEventTickets
	goto_if_unset FLAG_GOT_SS_TICKET, Route25_SeaCottage_EventScript_BillNoRedScale
	checkitem ITEM_RED_SCALE
	goto_if_eq VAR_RESULT, TRUE, Route25_SeaCottage_EventScript_BillRedScale
Route25_SeaCottage_EventScript_BillNoRedScale::
	goto_if_set RETURN_AFTER_SS_TICKET, BillsGarden_EventScript_BillCheckGarden
	goto_if_set FLAG_GOT_SS_TICKET, Route25_SeaCottage_EventScript_BillGoToSSAnne
	goto_if_set FLAG_HELPED_BILL_IN_SEA_COTTAGE, Route25_SeaCottage_EventScript_BillGiveSSTicket
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_BillAskForHelpMale
	goto_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_BillAskForHelpFemale
	end

Route25_SeaCottage_EventScript_BillAskForHelpMale::
	msgbox Route25_SeaCottage_Text_ImBillHelpMeOutPal, MSGBOX_YESNO
	goto Route25_SeaCottage_EventScript_BillAskForHelp
	end

Route25_SeaCottage_EventScript_BillAskForHelpFemale::
	msgbox Route25_SeaCottage_Text_ImBillHelpMeOutLady, MSGBOX_YESNO
	goto Route25_SeaCottage_EventScript_BillAskForHelp
	end

Route25_SeaCottage_EventScript_BillAskForHelp::
	call_if_eq VAR_RESULT, NO, Route25_SeaCottage_EventScript_DeclineHelpBill
	msgbox Route25_SeaCottage_Text_RunCellSeparationOnPC
	closemessage
	delay 10
	call_if_eq VAR_FACING, DIR_SOUTH, Route25_SeaCottage_EventScript_BillWalkToTeleporterSouth
	call_if_eq VAR_FACING, DIR_NORTH, Route25_SeaCottage_EventScript_BillWalkToTeleporter
	call_if_eq VAR_FACING, DIR_WEST, Route25_SeaCottage_EventScript_BillWalkToTeleporter
	call_if_eq VAR_FACING, DIR_EAST, Route25_SeaCottage_EventScript_BillWalkToTeleporter
	opendoor 10, 3
	waitdooranim
	applymovement LOCALID_BILL_CLEFAIRY, Route25_SeaCottage_Movement_BillEnterTeleporter
	waitmovement 0
	removeobject LOCALID_BILL_CLEFAIRY
	playse SE_CONTEST_CURTAIN_FALL
	closedoor 10, 3
	waitdooranim
	setflag BILL_IN_TELEPORTER
	release
	end

@ Just returns after message, execution continues as if player had said yes
Route25_SeaCottage_EventScript_DeclineHelpBill::
	checkplayergender
	call_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_DeclineHelpBillMale
	call_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_DeclineHelpBillFemale
	return

Route25_SeaCottage_EventScript_DeclineHelpBillMale::
	msgbox Route25_SeaCottage_Text_NoPleaseChief
	return

Route25_SeaCottage_EventScript_DeclineHelpBillFemale::
	msgbox Route25_SeaCottage_Text_NoPleaseBeautiful
	return

Route25_SeaCottage_EventScript_BillWalkToTeleporterSouth::
	applymovement LOCALID_BILL_CLEFAIRY, Route25_SeaCottage_Movement_BillWalkToTeleporterSouth
	waitmovement 0
	return

Route25_SeaCottage_EventScript_BillWalkToTeleporter::
	applymovement LOCALID_BILL_CLEFAIRY, Route25_SeaCottage_Movement_BillWalkToTeleporter
	waitmovement 0
	return

Route25_SeaCottage_EventScript_BillGoToSSAnne::
	msgbox Route25_SeaCottage_Text_SSAnnePartyYouGoInstead
	release
	end

Route25_SeaCottage_EventScript_BillGiveSSTicket::
	famechecker FAMECHECKER_BILL, FCPICKSTATE_COLORED, UpdatePickStateFromSpecialVar8005
	checkplayergender
	call_if_eq VAR_RESULT, MALE, Route25_SeaCottage_EventScript_BillThanksMale
	call_if_eq VAR_RESULT, FEMALE, Route25_SeaCottage_EventScript_BillThanksFemale
	checkitemspace ITEM_SS_TICKET
	goto_if_eq VAR_RESULT, FALSE, Route25_SeaCottage_EventScript_NoRoomForSSTicket
	giveitem_msg Route25_SeaCottage_Text_ReceivedSSTicketFromBill, ITEM_SS_TICKET, 1, MUS_OBTAIN_KEY_ITEM
	setflag FLAG_GOT_SS_TICKET_DUP
	setflag FLAG_HIDE_NUGGET_BRIDGE_ROCKET
	setflag FLAG_GOT_SS_TICKET
	setflag FLAG_SYS_NOT_SOMEONES_PC
	goto Route25_SeaCottage_EventScript_BillGoToSSAnne
	end

Route25_SeaCottage_EventScript_BillThanksMale::
	msgbox Route25_SeaCottage_Text_ThanksBudTakeThis
	return

Route25_SeaCottage_EventScript_BillThanksFemale::
	msgbox Route25_SeaCottage_Text_ThanksLadyTakeThis
	return

Route25_SeaCottage_EventScript_NoRoomForSSTicket::
	msgbox Route25_SeaCottage_Text_YouveGotTooMuchStuff
	release
	end

Route25_SeaCottage_EventScript_BillGoLookAtPC::
	msgbox Route25_SeaCottage_Text_CheckOutRareMonsOnPC
	release
	end

Route25_SeaCottage_Movement_BillWalkToTeleporter::
	walk_up
	walk_up
	step_end

Route25_SeaCottage_Movement_BillWalkToTeleporterSouth::
	walk_right
	walk_up
	walk_up
	walk_left
	walk_in_place_faster_up
	step_end

Route25_SeaCottage_Movement_BillEnterTeleporter::
	walk_up
	step_end

Route25_SeaCottage_EventScript_Computer::
	lockall
	goto_if_set RETURN_AFTER_SS_TICKET, Route25_SeaCottage_EventScript_OfferTeleporter
	goto_if_set BILL_IN_TELEPORTER, Route25_SeaCottage_EventScript_RunCellSeparator
	msgbox Route25_SeaCottage_Text_TeleporterIsDisplayed
	releaseall
	end

Route25_SeaCottage_EventScript_RunCellSeparator::
	fadeoutbgm 0
	msgbox Route25_SeaCottage_Text_InitiatedTeleportersCellSeparator
	closemessage
	clearflag BILL_IN_TELEPORTER
	setflag FLAG_HELPED_BILL_IN_SEA_COTTAGE
	special SpawnCameraObject
	applymovement LOCALID_CAMERA, Route25_SeaCottage_Movement_CameraPanToTeleporters
	waitmovement 0
	delay 35
	playse SE_PIN
	waitse
	setvar VAR_0x8004, 0
	special AnimateTeleporterHousing
	delay 10
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	setvar VAR_0x8004, 1
	special AnimateTeleporterHousing
	playse SE_WARP_IN
	special AnimateTeleporterCable
	waitse
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	opendoor 3, 3
	waitdooranim
	fadeinbgm 0
	addobject LOCALID_BILL_HUMAN
	clearflag FLAG_HIDE_BILL_HUMAN_SEA_COTTAGE
	delay 50
	playfanfare MUS_LEVEL_UP
	applymovement LOCALID_BILL_HUMAN, Route25_SeaCottage_Movement_BillExitTeleporter
	waitmovement 0
	waitfanfare
	applymovement LOCALID_CAMERA, Route25_SeaCottage_Movement_CameraPanBackFromTeleporters
	waitmovement 0
	playse SE_CONTEST_CURTAIN_FALL
	closedoor 3, 3
	waitdooranim
	applymovement LOCALID_BILL_HUMAN, Route25_SeaCottage_Movement_BillWalkToMiddleOfRoom
	waitmovement 0
	special RemoveCameraObject
	releaseall
	end

Route25_SeaCottage_EventScript_PlayTeleporterBeepSE::
	playse SE_BALL
	waitse
	delay 20
	return

Route25_SeaCottage_Movement_CameraPanToTeleporters::
	walk_up
	walk_up
	walk_right
	walk_right
	step_end

Route25_SeaCottage_Movement_CameraPanBackFromTeleporters::
	delay_16
	delay_16
	walk_down
	walk_down
	walk_left
	walk_left
	step_end

Route25_SeaCottage_EventScript_OpenBillsMonList::
	msgbox Route25_SeaCottage_Text_BillsFavoriteMonList
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_BillsMonList::
	message Route25_SeaCottage_Text_SeeWhichMon
	waitmessage
	multichoice 0, 0, MULTICHOICE_EEVEELUTIONS, FALSE
	switch VAR_RESULT
	case 0, Route25_SeaCottage_EventScript_ViewEevee
	case 1, Route25_SeaCottage_EventScript_ViewFlareon
	case 2, Route25_SeaCottage_EventScript_ViewJolteon
	case 3, Route25_SeaCottage_EventScript_ViewVaporeon
	case 4, Route25_SeaCottage_EventScript_ExitBillsMonList
	case 127, Route25_SeaCottage_EventScript_ExitBillsMonList
	end

Route25_SeaCottage_EventScript_ViewEevee::
	showmonpic SPECIES_EEVEE, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_EEVEE
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewFlareon::
	showmonpic SPECIES_FLAREON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_FLAREON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewJolteon::
	showmonpic SPECIES_JOLTEON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_JOLTEON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ViewVaporeon::
	showmonpic SPECIES_VAPOREON, 10, 3
	waitbuttonpress
	hidemonpic
	setvar VAR_0x8004, SPECIES_VAPOREON
	special SetSeenMon
	goto Route25_SeaCottage_EventScript_BillsMonList
	end

Route25_SeaCottage_EventScript_ExitBillsMonList::
	releaseall
	end

Route25_SeaCottage_Movement_BillWalkToMiddleOfRoom::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	step_end

Route25_SeaCottage_Movement_BillExitTeleporter::
	walk_down
	step_end

@ Mr. POKéMON's RED SCALE trade from HGSS
Route25_SeaCottage_EventScript_BillRedScale::
	msgbox Route25_SeaCottage_Text_BillThatScaleRedGyarados, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route25_SeaCottage_EventScript_BillRedScaleRefused
	giveitem ITEM_EXP_SHARE
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	removeitem ITEM_RED_SCALE
	msgbox Route25_SeaCottage_Text_CheckOutRareMonsOnPC
	release
	end

Route25_SeaCottage_EventScript_BillRedScaleRefused::
	msgbox Route25_SeaCottage_Text_BillThatsDisappointing
	release
	end

@ After the Hall of Fame, BILL hands over the MYSTIC and AURORA TICKETS, which
@ this revision of the game never gives out. They open the SEAGALLOP routes to
@ NAVEL ROCK (LUGIA, HO-OH) and BIRTH ISLAND (DEOXYS).
Route25_SeaCottage_EventScript_BillCheckEventTickets::
	goto_if_unset FLAG_GOT_EVENT_TICKETS_FROM_BILL, Route25_SeaCottage_EventScript_BillGiveEventTickets
	return

Route25_SeaCottage_EventScript_BillGiveEventTickets::
	msgbox Route25_SeaCottage_Text_BillOddTicketsArrived
	giveitem ITEM_MYSTIC_TICKET
	giveitem ITEM_AURORA_TICKET
	setflag FLAG_RECEIVED_MYSTIC_TICKET
	setflag FLAG_RECEIVED_AURORA_TICKET
	setflag FLAG_ENABLE_SHIP_NAVEL_ROCK
	setflag FLAG_ENABLE_SHIP_BIRTH_ISLAND
	setflag FLAG_GOT_EVENT_TICKETS_FROM_BILL
	msgbox Route25_SeaCottage_Text_BillShowTicketsAtVermilion
	release
	end

@ Roadmap 2, event 4: BILL's teleporter accident, a nod to the Gen 1 rumor of
@ BILL fused with a CLEFAIRY. After the S.S. TICKET, the PC can run the
@ TELEPORTER again. The player comes out of the pod looking like their lead
@ POKéMON (CLEFAIRY if it has no overworld sprite) and walks around like that
@ until they run it once more.
Route25_SeaCottage_EventScript_OfferTeleporter::
	goto_if_questlog Route25_SeaCottage_EventScript_OpenBillsMonList
	call_if_eq VAR_PLAYER_MON_FORM, SPECIES_NONE, Route25_SeaCottage_EventScript_AskRunTeleporter
	call_if_ne VAR_PLAYER_MON_FORM, SPECIES_NONE, Route25_SeaCottage_EventScript_AskChangeBack
	goto_if_eq VAR_RESULT, NO, Route25_SeaCottage_EventScript_OpenBillsMonList
	msgbox Route25_SeaCottage_Text_BillHopInThePod
	closemessage
	call_if_eq VAR_PLAYER_MON_FORM, SPECIES_NONE, Route25_SeaCottage_EventScript_SetTransformScene
	call_if_ne VAR_PLAYER_MON_FORM, SPECIES_NONE, Route25_SeaCottage_EventScript_SetChangeBackScene
	playse SE_CONTEST_CURTAIN_FALL
	fadescreen FADE_TO_BLACK
	warpsilent MAP_ROUTE25_SEA_COTTAGE, 3, 3
	waitstate
	releaseall
	end

Route25_SeaCottage_EventScript_AskRunTeleporter::
	msgbox Route25_SeaCottage_Text_RunTeleporterAgain, MSGBOX_YESNO
	return

Route25_SeaCottage_EventScript_AskChangeBack::
	msgbox Route25_SeaCottage_Text_RunTeleporterToChangeBack, MSGBOX_YESNO
	return

Route25_SeaCottage_EventScript_SetTransformScene::
	setvar VAR_SEA_COTTAGE_TELEPORT, 1
	return

Route25_SeaCottage_EventScript_SetChangeBackScene::
	setvar VAR_SEA_COTTAGE_TELEPORT, 2
	return

Route25_SeaCottage_EventScript_TeleporterTransform::
	lockall
	call Route25_SeaCottage_EventScript_RunTeleporterInPod
	setvar VAR_0x8004, TRUE
	special SetPlayerMonForm
	copyvar VAR_0x8005, VAR_RESULT
	call Route25_SeaCottage_EventScript_StepOutOfPod
	call_if_eq VAR_0x8005, TRUE, Route25_SeaCottage_EventScript_BillDataMixedUp
	msgbox Route25_SeaCottage_Text_BillYouLookLikeMon
	setvar VAR_SEA_COTTAGE_TELEPORT, 0
	releaseall
	end

Route25_SeaCottage_EventScript_TeleporterChangeBack::
	lockall
	call Route25_SeaCottage_EventScript_RunTeleporterInPod
	setvar VAR_0x8004, FALSE
	special SetPlayerMonForm
	call Route25_SeaCottage_EventScript_StepOutOfPod
	msgbox Route25_SeaCottage_Text_BillBackToNormal
	setvar VAR_SEA_COTTAGE_TELEPORT, 0
	releaseall
	end

@ The player waits hidden in the pod while the machine runs
Route25_SeaCottage_EventScript_RunTeleporterInPod::
	hideobjectat LOCALID_PLAYER, MAP_ROUTE25_SEA_COTTAGE
	delay 30
	setvar VAR_0x8004, 0
	special AnimateTeleporterHousing
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	setvar VAR_0x8004, 1
	special AnimateTeleporterHousing
	playse SE_WARP_IN
	special AnimateTeleporterCable
	waitse
	playse SE_M_EARTHQUAKE
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 10
	setvar VAR_0x8007, 3
	special ShakeScreen
	delay 20
	fadescreen FADE_TO_WHITE
	playse SE_M_REFLECT
	delay 20
	fadescreen FADE_FROM_WHITE
	fadescreen FADE_TO_WHITE
	fadescreen FADE_FROM_WHITE
	waitse
	call Route25_SeaCottage_EventScript_PlayTeleporterBeepSE
	return

Route25_SeaCottage_EventScript_StepOutOfPod::
	opendoor 3, 3
	waitdooranim
	showobjectat LOCALID_PLAYER, MAP_ROUTE25_SEA_COTTAGE
	applymovement LOCALID_PLAYER, Route25_SeaCottage_Movement_StepOutOfPod
	waitmovement 0
	closedoor 3, 3
	waitdooranim
	return

Route25_SeaCottage_Movement_StepOutOfPod::
	walk_down
	step_end

Route25_SeaCottage_EventScript_BillDataMixedUp::
	msgbox Route25_SeaCottage_Text_BillDataMixedUp
	return
