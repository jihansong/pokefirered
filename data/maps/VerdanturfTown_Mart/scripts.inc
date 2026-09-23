VerdanturfTown_Mart_MapScripts::
	.byte 0

VerdanturfTown_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart VerdanturfTown_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
VerdanturfTown_Mart_EventScript_H0_Items::
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_NEST_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_X_SPECIAL
	.2byte ITEM_FLUFFY_TAIL
	release
	end

VerdanturfTown_Mart_EventScript_H1::
	msgbox VerdanturfTown_Mart_Text_H1, MSGBOX_NPC
	end

VerdanturfTown_Mart_EventScript_H2::
	msgbox VerdanturfTown_Mart_Text_H2, MSGBOX_NPC
	end

VerdanturfTown_Mart_EventScript_H3::
	msgbox VerdanturfTown_Mart_Text_H3, MSGBOX_NPC
	end
