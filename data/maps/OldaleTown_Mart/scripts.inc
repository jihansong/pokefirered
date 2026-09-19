OldaleTown_Mart_MapScripts::
	.byte 0

OldaleTown_Mart_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart OldaleTown_Mart_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
OldaleTown_Mart_EventScript_H0_Items::
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	release
	end

OldaleTown_Mart_EventScript_H1::
	msgbox OldaleTown_Mart_Text_H1, MSGBOX_NPC
	end

OldaleTown_Mart_EventScript_H2::
	msgbox OldaleTown_Mart_Text_H2, MSGBOX_NPC
	end

