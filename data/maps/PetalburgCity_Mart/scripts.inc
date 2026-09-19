PetalburgCity_Mart_MapScripts::
	.byte 0

PetalburgCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart PetalburgCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
PetalburgCity_Mart_EventScript_H0_Items::
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_ORANGE_MAIL
	release
	end

PetalburgCity_Mart_EventScript_H1::
	msgbox PetalburgCity_Mart_Text_H1, MSGBOX_NPC
	end

PetalburgCity_Mart_EventScript_H2::
	msgbox PetalburgCity_Mart_Text_H2, MSGBOX_NPC
	end

PetalburgCity_Mart_EventScript_H3::
	msgbox PetalburgCity_Mart_Text_H3, MSGBOX_NPC
	end

