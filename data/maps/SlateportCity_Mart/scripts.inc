SlateportCity_Mart_MapScripts::
	.byte 0

SlateportCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart SlateportCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
SlateportCity_Mart_EventScript_H0_Items::
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_HARBOR_MAIL
	release
	end

SlateportCity_Mart_EventScript_H1::
	msgbox SlateportCity_Mart_Text_H1, MSGBOX_NPC
	end

SlateportCity_Mart_EventScript_H2::
	msgbox SlateportCity_Mart_Text_H2, MSGBOX_NPC
	end

