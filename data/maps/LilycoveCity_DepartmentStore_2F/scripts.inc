LilycoveCity_DepartmentStore_2F_MapScripts::
	.byte 0

LilycoveCity_DepartmentStore_2F_EventScript_H0::
	msgbox LilycoveCity_DepartmentStore_2F_Text_H0, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_2F_EventScript_H1::
	msgbox LilycoveCity_DepartmentStore_2F_Text_H1, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_2F_EventScript_H2::
	msgbox LilycoveCity_DepartmentStore_2F_Text_H2, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_2F_EventScript_H3::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_2F_EventScript_H3_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_2F_EventScript_H3_Items::
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_WAVE_MAIL
	.2byte ITEM_MECH_MAIL
	release
	end

LilycoveCity_DepartmentStore_2F_EventScript_H4::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_2F_EventScript_H4_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_2F_EventScript_H4_Items::
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_FLUFFY_TAIL
	release
	end

