FallarborTown_Mart_MapScripts::
	.byte 0

FallarborTown_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart FallarborTown_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
FallarborTown_Mart_EventScript_H0_Items::
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_X_SPECIAL
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_GUARD_SPEC
	release
	end

FallarborTown_Mart_EventScript_H1::
	msgbox FallarborTown_Mart_Text_H1, MSGBOX_NPC
	end

FallarborTown_Mart_EventScript_H2::
	msgbox FallarborTown_Mart_Text_H2, MSGBOX_NPC
	end

FallarborTown_Mart_EventScript_H3::
	msgbox FallarborTown_Mart_Text_H3, MSGBOX_NPC
	end

FallarborTown_Mart_EventScript_H4::
	msgbox FallarborTown_Mart_Text_H4, MSGBOX_NPC
	end

