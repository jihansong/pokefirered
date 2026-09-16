RocketHideout_B2F_MapScripts::
	.byte 0

@ Crystal's Team Rocket Base traps: POKé BALLS on the floor that are really a
@ VOLTORB or ELECTRODE. The emergency generator runs them and the B1F cameras;
@ switching it off disarms whatever is left.
RocketHideout_B2F_EventScript_VoltorbTrap1::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	setvar VAR_0x800A, SPECIES_VOLTORB
	call RocketHideout_B2F_EventScript_BallTrapReveal
	setwildbattle SPECIES_VOLTORB, 23
	dowildbattle
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_1
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_1
	release
	end

RocketHideout_B2F_EventScript_VoltorbTrap2::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	setvar VAR_0x800A, SPECIES_VOLTORB
	call RocketHideout_B2F_EventScript_BallTrapReveal
	setwildbattle SPECIES_VOLTORB, 23
	dowildbattle
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_2
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_2
	release
	end

RocketHideout_B2F_EventScript_ElectrodeTrap::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	setvar VAR_0x800A, SPECIES_ELECTRODE
	call RocketHideout_B2F_EventScript_BallTrapReveal
	setwildbattle SPECIES_ELECTRODE, 23
	dowildbattle
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_ELECTRODE_TRAP
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_ELECTRODE_TRAP
	release
	end

@ The flash of white and cry from Crystal's exploding traps
RocketHideout_B2F_EventScript_BallTrapReveal::
	special QuestLog_CutRecording
	fadescreen FADE_TO_WHITE
	playmoncry VAR_0x800A, CRY_MODE_ENCOUNTER
	fadescreen FADE_FROM_WHITE
	waitmoncry
	bufferspeciesname STR_VAR_1, VAR_0x800A
	msgbox RocketHideout_B2F_Text_ItWasATrap
	return

RocketHideout_B2F_EventScript_Generator::
	lockall
	goto_if_eq VAR_ROCKET_HIDEOUT_SECURITY, 3, RocketHideout_B2F_EventScript_GeneratorOff
	msgbox RocketHideout_B2F_Text_EmergencyGenerator, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, RocketHideout_B2F_EventScript_GeneratorLeftOn
	playse SE_CLICK
	waitse
	setvar VAR_ROCKET_HIDEOUT_SECURITY, 3
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_1
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_2
	setflag FLAG_HIDE_ROCKET_HIDEOUT_B2F_ELECTRODE_TRAP
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_1
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_VOLTORB_TRAP_2
	removeobject LOCALID_ROCKET_HIDEOUT_B2F_ELECTRODE_TRAP
	msgbox RocketHideout_B2F_Text_GeneratorShutDown
	releaseall
	end

RocketHideout_B2F_EventScript_GeneratorLeftOn::
	releaseall
	end

RocketHideout_B2F_EventScript_GeneratorOff::
	msgbox RocketHideout_B2F_Text_GeneratorIsOff
	releaseall
	end

RocketHideout_B2F_EventScript_Grunt::
	trainerbattle_single TRAINER_TEAM_ROCKET_GRUNT_13, RocketHideout_B2F_Text_GruntIntro, RocketHideout_B2F_Text_GruntDefeat
	msgbox RocketHideout_B2F_Text_GruntPostBattle, MSGBOX_AUTOCLOSE
	end
