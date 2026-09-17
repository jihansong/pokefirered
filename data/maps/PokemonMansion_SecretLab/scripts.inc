PokemonMansion_SecretLab_MapScripts::
	.byte 0

@ The rumor that DITTO is a failed attempt at cloning MEW. After MEWTWO has
@ been battled, a hidden lab opens off POKéMON MANSION B1F. Once all three lab
@ logs are read, the pink mass in the culture capsule breaks out as a Lv40
@ DITTO that only knows TRANSFORM.
PokemonMansion_SecretLab_EventScript_HiddenDoor::
	lockall
	goto_if_unset FLAG_FOUGHT_MEWTWO, PokemonMansion_SecretLab_EventScript_DoorLocked
	msgbox PokemonMansion_SecretLab_Text_HiddenDoorOpen, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_ReleaseEnd
	closemessage
	playse SE_EXIT
	warp MAP_POKEMON_MANSION_SECRET_LAB, 0
	waitstate
	releaseall
	end

PokemonMansion_SecretLab_EventScript_DoorLocked::
	msgbox PokemonMansion_SecretLab_Text_WallFeelsHollow
	releaseall
	end

PokemonMansion_SecretLab_EventScript_Log1::
	lockall
	setflag FLAG_READ_MANSION_LAB_LOG_1
	msgbox PokemonMansion_SecretLab_Text_Log1
	releaseall
	end

PokemonMansion_SecretLab_EventScript_Log2::
	lockall
	setflag FLAG_READ_MANSION_LAB_LOG_2
	msgbox PokemonMansion_SecretLab_Text_Log2
	releaseall
	end

PokemonMansion_SecretLab_EventScript_Log3::
	lockall
	setflag FLAG_READ_MANSION_LAB_LOG_3
	msgbox PokemonMansion_SecretLab_Text_Log3
	releaseall
	end

PokemonMansion_SecretLab_EventScript_Capsule::
	lockall
	goto_if_set FLAG_HIDE_MANSION_LAB_DITTO, PokemonMansion_SecretLab_EventScript_CapsuleEmpty
	msgbox PokemonMansion_SecretLab_Text_PinkMassWriggling
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_1, EventScript_ReleaseEnd
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_2, EventScript_ReleaseEnd
	goto_if_unset FLAG_READ_MANSION_LAB_LOG_3, EventScript_ReleaseEnd
	msgbox PokemonMansion_SecretLab_Text_ItStaredAtYou
	closemessage
	playse SE_GLASS_FLUTE
	applymovement LOCALID_MANSION_LAB_DITTO, PokemonMansion_SecretLab_Movement_BreakOut
	waitmovement 0
	waitse
	playmoncry SPECIES_DITTO, CRY_MODE_ENCOUNTER
	waitmoncry
	setwildbattle SPECIES_DITTO, 40
	special SetScriptedWildMonTransformOnly
	dowildbattle
	setflag FLAG_HIDE_MANSION_LAB_DITTO
	removeobject LOCALID_MANSION_LAB_DITTO
	releaseall
	end

PokemonMansion_SecretLab_EventScript_CapsuleEmpty::
	msgbox PokemonMansion_SecretLab_Text_CapsuleEmpty
	releaseall
	end

PokemonMansion_SecretLab_Movement_BreakOut::
	jump_in_place_down
	jump_in_place_down
	jump_down
	step_end
