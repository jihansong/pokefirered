FortreeCity_Mart_MapScripts::
	.byte 0

FortreeCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart FortreeCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
FortreeCity_Mart_EventScript_H0_Items::
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REVIVE
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_WOOD_MAIL
	release
	end

FortreeCity_Mart_EventScript_H1::
	msgbox FortreeCity_Mart_Text_H1, MSGBOX_NPC
	end

FortreeCity_Mart_EventScript_H2::
	msgbox FortreeCity_Mart_Text_H2, MSGBOX_NPC
	end

FortreeCity_Mart_EventScript_H3::
	msgbox FortreeCity_Mart_Text_H3, MSGBOX_NPC
	end

