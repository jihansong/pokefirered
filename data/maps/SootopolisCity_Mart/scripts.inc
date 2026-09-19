SootopolisCity_Mart_MapScripts::
	.byte 0

SootopolisCity_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart SootopolisCity_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
SootopolisCity_Mart_EventScript_H0_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_POTION
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_SHADOW_MAIL
	release
	end

SootopolisCity_Mart_EventScript_H1::
	msgbox SootopolisCity_Mart_Text_H1, MSGBOX_NPC
	end

SootopolisCity_Mart_EventScript_H2::
	msgbox SootopolisCity_Mart_Text_H2, MSGBOX_NPC
	end

