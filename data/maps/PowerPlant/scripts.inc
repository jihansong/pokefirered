PowerPlant_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, PowerPlant_OnResume
	map_script MAP_SCRIPT_ON_TRANSITION, PowerPlant_OnTransition
	.byte 0

PowerPlant_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, PowerPlant_EventScript_TryRemoveStaticMon
	end

PowerPlant_EventScript_TryRemoveStaticMon::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, EventScript_Return
	removeobject VAR_LAST_TALKED
	return

PowerPlant_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_POWER_PLANT
	call_if_unset FLAG_FOUGHT_ZAPDOS, PowerPlant_EventScript_ShowZapdos
	call_if_unset FLAG_FOUGHT_POWER_PLANT_ELECTRODE_1, PowerPlant_EventScript_ShowElectrode1
	call_if_unset FLAG_FOUGHT_POWER_PLANT_ELECTRODE_2, PowerPlant_EventScript_ShowElectrode2
	end

PowerPlant_EventScript_ShowZapdos::
	clearflag FLAG_HIDE_ZAPDOS
	return

PowerPlant_EventScript_ShowElectrode1::
	clearflag FLAG_HIDE_POWER_PLANT_ELECTRODE_1
	return

PowerPlant_EventScript_ShowElectrode2::
	clearflag FLAG_HIDE_POWER_PLANT_ELECTRODE_2
	return

PowerPlant_EventScript_Zapdos::
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	lock
	faceplayer
	setwildbattle SPECIES_ZAPDOS, 50
	waitse
	playmoncry SPECIES_ZAPDOS, CRY_MODE_ENCOUNTER
	message Text_Gyaoo
	waitmessage
	waitmoncry
	delay 10
	playbgm MUS_ENCOUNTER_GYM_LEADER, 0
	waitbuttonpress
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, PowerPlant_EventScript_DefeatedZapdos
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, PowerPlant_EventScript_RanFromZapdos
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, PowerPlant_EventScript_RanFromZapdos
	setflag FLAG_FOUGHT_ZAPDOS
	release
	end

PowerPlant_EventScript_DefeatedZapdos::
	setflag FLAG_FOUGHT_ZAPDOS
	goto EventScript_RemoveStaticMon
	end

PowerPlant_EventScript_RanFromZapdos::
	setvar VAR_0x8004, SPECIES_ZAPDOS
	goto EventScript_MonFlewAway
	end

PowerPlant_EventScript_Electrode1::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	setwildbattle SPECIES_ELECTRODE, 34
	waitse
	playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	dowildbattle
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special QuestLog_CutRecording
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, PowerPlant_EventScript_FoughtElectrode1
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, PowerPlant_EventScript_FoughtElectrode1
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, PowerPlant_EventScript_FoughtElectrode1
	setflag FLAG_FOUGHT_POWER_PLANT_ELECTRODE_1
	release
	end

PowerPlant_EventScript_FoughtElectrode1::
	setflag FLAG_FOUGHT_POWER_PLANT_ELECTRODE_1
	goto EventScript_RemoveStaticMon
	end

PowerPlant_EventScript_Electrode2::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	setwildbattle SPECIES_ELECTRODE, 34
	waitse
	playmoncry SPECIES_ELECTRODE, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	dowildbattle
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special QuestLog_CutRecording
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, PowerPlant_EventScript_FoughtElectrode2
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, PowerPlant_EventScript_FoughtElectrode2
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, PowerPlant_EventScript_FoughtElectrode2
	setflag FLAG_FOUGHT_POWER_PLANT_ELECTRODE_2
	release
	end

PowerPlant_EventScript_FoughtElectrode2::
	setflag FLAG_FOUGHT_POWER_PLANT_ELECTRODE_2
	goto EventScript_RemoveStaticMon
	end

@ Roadmap 2, event 13: where ZAPDOS stood, electricity still crackles. A lead
@ starter PIKACHU with maximum friendship at Lv40 or higher takes it in and
@ learns VOLT TACKLE.
PowerPlant_EventScript_LingeringElectricity::
	lockall
	goto_if_unset FLAG_FOUGHT_ZAPDOS, EventScript_ReleaseEnd
	msgbox PowerPlant_Text_SparksCrackling
	specialvar VAR_RESULT, CheckVoltTackleConditions
	switch VAR_RESULT
	case VOLT_TACKLE_READY, PowerPlant_EventScript_PikachuAbsorbs
	case VOLT_TACKLE_LOW_FRIENDSHIP, PowerPlant_EventScript_PikachuHesitates
	case VOLT_TACKLE_LOW_LEVEL, PowerPlant_EventScript_PikachuTooWeak
	case VOLT_TACKLE_ALREADY_KNOWN, PowerPlant_EventScript_PikachuAlreadyKnows
	releaseall
	end

PowerPlant_EventScript_PikachuHesitates::
	msgbox PowerPlant_Text_PikachuHesitates
	releaseall
	end

PowerPlant_EventScript_PikachuTooWeak::
	msgbox PowerPlant_Text_PikachuTooWeak
	releaseall
	end

PowerPlant_EventScript_PikachuAlreadyKnows::
	msgbox PowerPlant_Text_PikachuAlreadyKnows
	releaseall
	end

PowerPlant_EventScript_PikachuAbsorbs::
	closemessage
	playmoncry SPECIES_PIKACHU, CRY_MODE_NORMAL
	waitmoncry
	playse SE_THUNDER
	fadescreen FADE_TO_WHITE
	fadescreen FADE_FROM_WHITE
	setvar VAR_0x8004, 0
	setvar VAR_0x8005, 3
	setvar VAR_0x8006, 10
	setvar VAR_0x8007, 3
	special ShakeScreen
	playse SE_M_THUNDERBOLT
	fadescreen FADE_TO_WHITE
	fadescreen FADE_FROM_WHITE
	waitse
	playse SE_THUNDER
	fadescreen FADE_TO_WHITE
	delay 20
	fadescreen FADE_FROM_WHITE
	waitse
	msgbox PowerPlant_Text_PikachuAbsorbed
	setvar VAR_0x8005, MOVETUTOR_PIKACHU_VOLT_TACKLE
	closemessage
	fadescreen FADE_TO_BLACK
	specialvar VAR_0x8007, GetStarterPikachuPartySlotForScript
	call EventScript_ChooseMoveTutorMon
	releaseall
	end

PowerPlant_Text_SparksCrackling::
    .string "Faint sparks are still crackling\n"
    .string "where ZAPDOS once stood…$"

PowerPlant_Text_PikachuHesitates::
    .string "PIKACHU looks at the sparks, then\n"
    .string "back at {PLAYER}…\p"
    .string "It doesn't seem ready to trust the\n"
    .string "power yet.$"

PowerPlant_Text_PikachuTooWeak::
    .string "PIKACHU reached for the sparks,\n"
    .string "but jumped back with a squeak!\p"
    .string "It looks like PIKACHU needs to\n"
    .string "grow stronger first.$"

PowerPlant_Text_PikachuAlreadyKnows::
    .string "PIKACHU's cheeks crackle happily.$"

PowerPlant_Text_PikachuAbsorbed::
    .string "PIKACHU soaked up all the leftover\n"
    .string "electricity!\p"
    .string "Its whole body is crackling with\n"
    .string "power!$"

