Route2_MapScripts::
	.byte 0

Route2_EventScript_RouteSign::
	msgbox Route2_Text_RouteSign, MSGBOX_SIGN
	end

Route2_EventScript_DiglettsCaveSign::
	msgbox Route2_Text_DiglettsCave, MSGBOX_SIGN
	end

@ HGSS's Randy and KENYA: a SPEAROW carrying MAIL to his friend on Route 22.
@ VAR_KENYA_DELIVERY: 1 = carrying KENYA, 2 = delivered, 3 = got the HP UP.
Route2_EventScript_Randy::
	lock
	faceplayer
	goto_if_eq VAR_KENYA_DELIVERY, 3, Route2_EventScript_RandyPalWasSnoozing
	goto_if_eq VAR_KENYA_DELIVERY, 2, Route2_EventScript_RandyQuestComplete
	goto_if_eq VAR_KENYA_DELIVERY, 1, Route2_EventScript_RandyDontLoseIt
	msgbox Route2_Text_RandyTakeThisMonToMyFriend, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route2_EventScript_RandyNeverMind
	msgbox Route2_Text_RandyThanks
	specialvar VAR_RESULT, GiveKenya
	goto_if_eq VAR_RESULT, FALSE, Route2_EventScript_RandyPartyFull
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_OBTAIN_KEY_ITEM
	message Route2_Text_ReceivedMonWithMail
	waitmessage
	waitfanfare
	call EventScript_RestorePrevTextColor
	setvar VAR_KENYA_DELIVERY, 1
Route2_EventScript_RandyDontLoseIt::
	msgbox Route2_Text_RandyDontLoseIt
	release
	end

Route2_EventScript_RandyPartyFull::
	msgbox Route2_Text_RandyCantCarryAnotherMon
	release
	end

Route2_EventScript_RandyNeverMind::
	msgbox Route2_Text_RandyNeverMind
	release
	end

Route2_EventScript_RandyQuestComplete::
	msgbox Route2_Text_RandySomethingForYourTrouble
	giveitem ITEM_HP_UP
	goto_if_eq VAR_RESULT, FALSE, EventScript_BagIsFull
	setvar VAR_KENYA_DELIVERY, 3
Route2_EventScript_RandyPalWasSnoozing::
	msgbox Route2_Text_RandyMyPalWasSnoozing
	release
	end
