EverGrandeCity_PokemonLeague_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EverGrandeCity_PokemonLeague_1F_OnTransition
	.byte 0

@ HOENN's ELITE FOUR is not open yet: the rooms behind this door were imported
@ without their battles, and their doors are only opened by the battle scripts,
@ so a player who walked in could never walk out again. Emerald's own two door
@ guards stand in front of the stairs until the ELITE FOUR opens.
EverGrandeCity_PokemonLeague_1F_OnTransition::
	setobjectxyperm 3, 9, 2
	setobjectxyperm 4, 10, 2
	end

EverGrandeCity_PokemonLeague_1F_EventScript_H0::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart EverGrandeCity_PokemonLeague_1F_EventScript_H0_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
EverGrandeCity_PokemonLeague_1F_EventScript_H0_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_POTION
	.2byte ITEM_FULL_RESTORE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_MAX_REPEL
	release
	end

EverGrandeCity_PokemonLeague_1F_EventScript_H1::
	msgbox EverGrandeCity_PokemonLeague_1F_Text_H1, MSGBOX_NPC
	end

EverGrandeCity_PokemonLeague_1F_EventScript_H2::
	msgbox EverGrandeCity_PokemonLeague_1F_Text_H2, MSGBOX_NPC
	end

