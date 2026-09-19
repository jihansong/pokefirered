BattleFrontier_Mart_MapScripts::
	.byte 0

BattleFrontier_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart BattleFrontier_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
BattleFrontier_Mart_EventScript_H0_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_POTION
	.2byte ITEM_FULL_RESTORE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_PROTEIN
	.2byte ITEM_CALCIUM
	.2byte ITEM_IRON
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_HP_UP
	release
	end

BattleFrontier_Mart_EventScript_H1::
	msgbox BattleFrontier_Mart_Text_H1, MSGBOX_NPC
	end

BattleFrontier_Mart_EventScript_H2::
	msgbox BattleFrontier_Mart_Text_H2, MSGBOX_NPC
	end

BattleFrontier_Mart_EventScript_H3::
	msgbox BattleFrontier_Mart_Text_H3, MSGBOX_NPC
	end

