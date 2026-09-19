@ REGIROCK, REGICE and REGISTEEL sleep behind the back walls of three TANOBY
@ chambers. As with HOENN's SEALED CHAMBER, they wake only for a TRAINER who
@ brings WAILORD and RELICANTH, and only after the Hall of Fame.

@ Sets VAR_RESULT to TRUE if the player can wake a REGI.
EventScript_SealedChamberCanWake::
	setvar VAR_RESULT, FALSE
	goto_if_unset FLAG_SYS_GAME_CLEAR, EventScript_Return
	setvar VAR_0x8004, SPECIES_WAILORD
	specialvar VAR_RESULT, PartyHasSpecies
	goto_if_eq VAR_RESULT, FALSE, EventScript_Return
	setvar VAR_0x8004, SPECIES_RELICANTH
	specialvar VAR_RESULT, PartyHasSpecies
	return

@ VAR_0x8008 is the REGI; setwildbattle must already be done.
@ Returns the battle outcome in VAR_RESULT.
EventScript_SealedChamberWake::
	msgbox Text_SealedChamberWallReacts
	closemessage
	playse SE_M_EARTHQUAKE
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 3
	setvar VAR_0x8006, 12
	setvar VAR_0x8007, 3
	special ShakeScreen
	delay 60
	waitse
	playmoncry VAR_0x8008, CRY_MODE_ENCOUNTER
	waitmoncry
	delay 10
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	return

EventScript_SealedChamberRegiLeft::
	bufferspeciesname STR_VAR_1, VAR_0x8008
	msgbox Text_SealedChamberRegiLeft
	return

Text_SealedChamberInscription::
    .string "Ancient writing is carved into\n"
    .string "the wall…\p"
    .string "“Bring the king of the sea and the\n"
    .string "fish unchanged since ancient days.\p"
    .string "Then shall the sleeping giant\n"
    .string "open its eyes.”$"

Text_SealedChamberWallReacts::
    .string "WAILORD and RELICANTH are reacting\n"
    .string "to the writing!\p"
    .string "Something stirs behind the wall!$"

Text_SealedChamberRegiLeft::
    .string "{STR_VAR_1} sank back into the\n"
    .string "wall and fell silent.$"

Text_SealedChamberSilent::
    .string "The wall is silent.$"
