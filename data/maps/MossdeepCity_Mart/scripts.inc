MossdeepCity_Mart_MapScripts::
	.byte 0

MossdeepCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart MossdeepCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
MossdeepCity_Mart_EventScript_H0_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_NET_BALL
	.2byte ITEM_DIVE_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	release
	end

MossdeepCity_Mart_EventScript_H1::
	msgbox MossdeepCity_Mart_Text_H1, MSGBOX_NPC
	end

MossdeepCity_Mart_EventScript_H2::
	msgbox MossdeepCity_Mart_Text_H2, MSGBOX_NPC
	end

MossdeepCity_Mart_EventScript_H3::
	msgbox MossdeepCity_Mart_Text_H3, MSGBOX_NPC
	end

