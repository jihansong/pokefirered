@ MAUVILLE's GAME CORNER, made playable: the twelve machines run FR/LG's own
@ slot game and pay into the COIN CASE from KANTO, and the counter takes coins
@ back for prizes. The room came across with its people; the machines did not.

MauvilleCity_GameCorner_EventScript_SlotMachine0::
	lockall
	setvar VAR_0x8004, 0
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine1::
	lockall
	setvar VAR_0x8004, 1
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine2::
	lockall
	setvar VAR_0x8004, 2
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine3::
	lockall
	setvar VAR_0x8004, 3
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine4::
	lockall
	setvar VAR_0x8004, 4
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine5::
	lockall
	setvar VAR_0x8004, 5
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine6::
	lockall
	setvar VAR_0x8004, 6
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine7::
	lockall
	setvar VAR_0x8004, 7
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine8::
	lockall
	setvar VAR_0x8004, 8
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine9::
	lockall
	setvar VAR_0x8004, 9
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine10::
	lockall
	setvar VAR_0x8004, 10
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine11::
	lockall
	setvar VAR_0x8004, 11
	goto MauvilleCity_GameCorner_EventScript_SlotMachine
	end

MauvilleCity_GameCorner_EventScript_SlotMachine::
	goto_if_unset FLAG_GOT_COIN_CASE, MauvilleCity_GameCorner_EventScript_NoCoinCase
	msgbox MauvilleCity_GameCorner_Text_PlayThisMachine, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MauvilleCity_GameCorner_EventScript_DontPlay
	specialvar VAR_RESULT, GetRandomSlotMachineId
	playslotmachine VAR_RESULT
	releaseall
	end

MauvilleCity_GameCorner_EventScript_DontPlay::
	releaseall
	end

MauvilleCity_GameCorner_EventScript_NoCoinCase::
	msgbox MauvilleCity_GameCorner_Text_NoCoinCase
	releaseall
	end

@ The clerk sells coins, the same ones the KANTO case already holds
MauvilleCity_GameCorner_EventScript_CoinsClerk::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_COIN_CASE, MauvilleCity_GameCorner_EventScript_ClerkNoCase
	showcoinsbox 0, 0
	msgbox MauvilleCity_GameCorner_Text_BuyCoins, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MauvilleCity_GameCorner_EventScript_ClerkDone
	checkcoins VAR_TEMP_1
	goto_if_ge VAR_TEMP_1, (MAX_COINS + 1) - 50, MauvilleCity_GameCorner_EventScript_ClerkCaseFull
	checkmoney 1000, 0
	goto_if_eq VAR_RESULT, FALSE, MauvilleCity_GameCorner_EventScript_ClerkNoMoney
	removemoney 1000, 0
	addcoins 50
	updatecoinsbox 0, 0
	updatemoneybox
	msgbox MauvilleCity_GameCorner_Text_Bought50
MauvilleCity_GameCorner_EventScript_ClerkDone::
	hidecoinsbox 0, 0
	release
	end

MauvilleCity_GameCorner_EventScript_ClerkNoMoney::
	msgbox MauvilleCity_GameCorner_Text_NotEnoughMoney
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end

MauvilleCity_GameCorner_EventScript_ClerkCaseFull::
	msgbox MauvilleCity_GameCorner_Text_CaseFull
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end

MauvilleCity_GameCorner_EventScript_ClerkNoCase::
	msgbox MauvilleCity_GameCorner_Text_NoCoinCase
	release
	end

@ The counter takes coins back for three prizes
MauvilleCity_GameCorner_EventScript_PrizeClerk::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_COIN_CASE, MauvilleCity_GameCorner_EventScript_ClerkNoCase
	showcoinsbox 0, 0
	message MauvilleCity_GameCorner_Text_WhichPrize
	waitmessage
	multichoice 11, 0, MULTICHOICE_MAUVILLE_PRIZES, FALSE
	switch VAR_RESULT
	case 0, MauvilleCity_GameCorner_EventScript_PrizeNugget
	case 1, MauvilleCity_GameCorner_EventScript_PrizePPUp
	case 2, MauvilleCity_GameCorner_EventScript_PrizeRareCandy
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end

MauvilleCity_GameCorner_EventScript_PrizeNugget::
	setvar VAR_TEMP_2, 1000
	setvar VAR_TEMP_3, ITEM_NUGGET
	goto MauvilleCity_GameCorner_EventScript_BuyPrize
	end

MauvilleCity_GameCorner_EventScript_PrizePPUp::
	setvar VAR_TEMP_2, 1500
	setvar VAR_TEMP_3, ITEM_PP_UP
	goto MauvilleCity_GameCorner_EventScript_BuyPrize
	end

MauvilleCity_GameCorner_EventScript_PrizeRareCandy::
	setvar VAR_TEMP_2, 2000
	setvar VAR_TEMP_3, ITEM_RARE_CANDY
	goto MauvilleCity_GameCorner_EventScript_BuyPrize
	end

MauvilleCity_GameCorner_EventScript_BuyPrize::
	checkcoins VAR_TEMP_1
	goto_if_lt VAR_TEMP_1, VAR_TEMP_2, MauvilleCity_GameCorner_EventScript_NotEnoughCoins
	checkitemspace VAR_TEMP_3, 1
	goto_if_eq VAR_RESULT, FALSE, MauvilleCity_GameCorner_EventScript_PrizeNoRoom
	removecoins VAR_TEMP_2
	updatecoinsbox 0, 0
	additem VAR_TEMP_3, 1
	msgbox MauvilleCity_GameCorner_Text_HereYouGo
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end

MauvilleCity_GameCorner_EventScript_NotEnoughCoins::
	msgbox MauvilleCity_GameCorner_Text_NotEnoughCoins
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end

MauvilleCity_GameCorner_EventScript_PrizeNoRoom::
	msgbox MauvilleCity_GameCorner_Text_PrizeNoRoom
	goto MauvilleCity_GameCorner_EventScript_ClerkDone
	end
