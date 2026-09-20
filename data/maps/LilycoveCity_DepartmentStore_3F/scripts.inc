LilycoveCity_DepartmentStore_3F_MapScripts::
	.byte 0

LilycoveCity_DepartmentStore_3F_EventScript_H0::
	msgbox LilycoveCity_DepartmentStore_3F_Text_H0, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_3F_EventScript_H1::
	msgbox LilycoveCity_DepartmentStore_3F_Text_H1, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_3F_EventScript_H2::
	msgbox LilycoveCity_DepartmentStore_3F_Text_H2, MSGBOX_NPC
	end

LilycoveCity_DepartmentStore_3F_EventScript_H3::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_3F_EventScript_H3_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_3F_EventScript_H3_Items::
	.2byte ITEM_PROTEIN
	.2byte ITEM_CALCIUM
	.2byte ITEM_IRON
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_HP_UP
	release
	end

LilycoveCity_DepartmentStore_3F_EventScript_H4::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart LilycoveCity_DepartmentStore_3F_EventScript_H4_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
LilycoveCity_DepartmentStore_3F_EventScript_H4_Items::
	.2byte ITEM_X_SPEED
	.2byte ITEM_X_SPECIAL
	.2byte ITEM_X_ATTACK
	.2byte ITEM_X_DEFEND
	.2byte ITEM_DIRE_HIT
	.2byte ITEM_GUARD_SPEC
	.2byte ITEM_X_ACCURACY
	release
	end

