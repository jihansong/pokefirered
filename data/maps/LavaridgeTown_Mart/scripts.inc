LavaridgeTown_Mart_MapScripts::
	.byte 0

LavaridgeTown_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LavaridgeTown_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LavaridgeTown_Mart_EventScript_H0_Items::
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_X_SPEED
	release
	end

LavaridgeTown_Mart_EventScript_H1::
	msgbox LavaridgeTown_Mart_Text_H1, MSGBOX_NPC
	end

LavaridgeTown_Mart_EventScript_H2::
	msgbox LavaridgeTown_Mart_Text_H2, MSGBOX_NPC
	end

