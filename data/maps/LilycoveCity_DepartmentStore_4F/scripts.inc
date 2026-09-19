LilycoveCity_DepartmentStore_4F_MapScripts::
	.byte 0

LilycoveCity_DepartmentStore_4F_EventScript_H0::
	msgbox LilycoveCity_DepartmentStore_4F_Text_H0, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_4F_EventScript_H1::
	msgbox LilycoveCity_DepartmentStore_4F_Text_H1, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_4F_EventScript_H2::
	msgbox LilycoveCity_DepartmentStore_4F_Text_H2, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_4F_EventScript_H3::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_4F_EventScript_H3_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_4F_EventScript_H3_Items::
	.2byte ITEM_TM38_FIRE_BLAST
	.2byte ITEM_TM25_THUNDER
	.2byte ITEM_TM14_BLIZZARD
	.2byte ITEM_TM15_HYPER_BEAM
	release
	end

LilycoveCity_DepartmentStore_4F_EventScript_H4::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_4F_EventScript_H4_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_4F_EventScript_H4_Items::
	.2byte ITEM_TM17_PROTECT
	.2byte ITEM_TM20_SAFEGUARD
	.2byte ITEM_TM33_REFLECT
	.2byte ITEM_TM16_LIGHT_SCREEN
	release
	end

