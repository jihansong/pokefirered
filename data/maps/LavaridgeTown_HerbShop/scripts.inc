LavaridgeTown_HerbShop_MapScripts::
	.byte 0

LavaridgeTown_HerbShop_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LavaridgeTown_HerbShop_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LavaridgeTown_HerbShop_EventScript_H0_Items::
	.2byte ITEM_ENERGY_POWDER
	.2byte ITEM_ENERGY_ROOT
	.2byte ITEM_HEAL_POWDER
	.2byte ITEM_REVIVAL_HERB
	release
	end

LavaridgeTown_HerbShop_EventScript_H1::
	msgbox LavaridgeTown_HerbShop_Text_H1, MSGBOX_NPC
	end

LavaridgeTown_HerbShop_EventScript_H2::
	msgbox LavaridgeTown_HerbShop_Text_H2, MSGBOX_NPC
	end

