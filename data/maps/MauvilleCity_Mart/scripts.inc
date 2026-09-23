MauvilleCity_Mart_MapScripts::
	.byte 0

MauvilleCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart MauvilleCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
MauvilleCity_Mart_EventScript_H0_Items::
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_GUARD_SPEC
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_X_ACCURACY
	release
	end

MauvilleCity_Mart_EventScript_H1::
	msgbox MauvilleCity_Mart_Text_H1, MSGBOX_NPC
	end

MauvilleCity_Mart_EventScript_H2::
	msgbox MauvilleCity_Mart_Text_H2, MSGBOX_NPC
	end
