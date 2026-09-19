TrainerHill_Entrance_MapScripts::
	.byte 0

TrainerHill_Entrance_EventScript_H0::
	msgbox TrainerHill_Entrance_Text_H0, MSGBOX_NPC
	end

TrainerHill_Entrance_EventScript_H1::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart TrainerHill_Entrance_EventScript_H1_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
TrainerHill_Entrance_EventScript_H1_Items::
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_SPECIAL
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_GUARD_SPEC
	.2byte ITEM_X_ACCURACY
	release
	end

TrainerHill_Entrance_EventScript_H2::
	msgbox TrainerHill_Entrance_Text_H2, MSGBOX_NPC
	end

TrainerHill_Entrance_EventScript_H3::
	msgbox TrainerHill_Entrance_Text_H3, MSGBOX_NPC
	end

