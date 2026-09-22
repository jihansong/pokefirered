@ Thunder Yellow v0.5.0: TEAM ROCKET's JESSIE, JAMES and MEOWTH, shared scenes.

@ Their entrance: the ROCKET music and the motto, written for this game.
EventScript_RocketTrioMotto::
	playbgm MUS_ENCOUNTER_ROCKET, 0
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox Text_RocketTrioMotto1
	textcolor NPC_TEXT_COLOR_MALE
	msgbox Text_RocketTrioMotto2
	textcolor NPC_TEXT_COLOR_FEMALE
	msgbox Text_RocketTrioMotto3
	textcolor NPC_TEXT_COLOR_MALE
	msgbox Text_RocketTrioMotto4
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_RocketTrioMotto5
	return

@ Their exit. Set VAR_0x8008, VAR_0x8009 and VAR_0x800A to the local ids of JESSIE,
@ JAMES and MEOWTH (0 for one who isn't there) and removeobject them after this.
EventScript_RocketTrioBlastOff::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_RocketTrioBlastOff
	closemessage
	special RocketTrioBlastOff
	waitstate
	return
