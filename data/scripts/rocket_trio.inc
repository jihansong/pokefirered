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

@ v0.9.0: every trio appearance is a battle (#1..#14 in docs/v0.9.0-plan.md).
@ Call right before trainerbattle with VAR_0x8004 = the event number. Notes
@ whether the battle will be a double, for the coins after it, and remembers
@ the event in VAR_ROCKET_RETRY: losing leaves it set, so the next try can skip
@ the long lines. Set VAR_ROCKET_RETRY back to ROCKET_RETRY_NONE after a win.
EventScript_RocketTrioBeforeBattle::
	special HasEnoughMonsForDoubleBattle
	copyvar VAR_ROCKET_DOUBLES, VAR_RESULT
	copyvar VAR_ROCKET_RETRY, VAR_0x8004
	return

@ The short try after a loss: one box instead of the motto and the set-up.
@ The caller has the ROCKET music playing already.
EventScript_RocketTrioRetry::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_RocketTrioRetry
	closemessage
	return

@ MEOWTH's PAY DAY coins, picked up after the trio blast off: 8 x MEOWTH's
@ level for each POKéMON past the first, and when the player had only one
@ POKéMON to send out, the half of the prize a single battle loses as well.
@ VAR_0x8004 = the amount. The money box opens on the old amount and goes up
@ as the coins are picked up.
EventScript_RocketMeowthCoins::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	showmoneybox 0, 0
	msgbox Text_RocketMeowthCoinsScattered
	special AddRocketMeowthCoins
	updatemoneybox
	playse SE_SHOP
	@ after updatemoneybox, which prints the money through gStringVar1
	buffernumberstring STR_VAR_1, VAR_0x8004
	msgbox Text_RocketMeowthCoins
	hidemoneybox
	return

@ Right after the giveitem of a trio reward, with VAR_0x8004 = its bit
@ (constants/rocket_trio.h). A new reward that went into the bag is marked
@ given; an old one needs nothing. If the bag had no room the OFFICER at the
@ VIRIDIAN POKéMON CENTER keeps it: a new reward simply stays unmarked, an old
@ one is marked held. Neither stops the event.
EventScript_RocketRewardResult::
	goto_if_eq VAR_0x8007, FALSE, EventScript_RocketRewardHeld
	goto_if_ge VAR_0x8004, ROCKET_HELD_FIRST, EventScript_Return
	special SetRocketRewardBit
	return

EventScript_RocketRewardHeld::
	call_if_ge VAR_0x8004, ROCKET_HELD_FIRST, EventScript_RocketSetRewardBit
	textcolor NPC_TEXT_COLOR_NEUTRAL
	msgbox Text_TooBadBagFull
	msgbox Text_RocketBagFullOfficer
	return

EventScript_RocketSetRewardBit::
	special SetRocketRewardBit
	return

@ After giveegg (or the special GiveMewEgg): VAR_RESULT 0 = party, 1 = PC,
@ 2 = no room anywhere, in which case the OFFICER keeps it. Leaves VAR_RESULT
@ as it was, so the caller can mark the reward only when the EGG was given.
EventScript_RocketEggResult::
	textcolor NPC_TEXT_COLOR_NEUTRAL
	goto_if_eq VAR_RESULT, 2, EventScript_RocketEggNoRoom
	playfanfare MUS_OBTAIN_ITEM
	message Text_RocketEggReceived
	waitmessage
	waitfanfare
	call_if_eq VAR_RESULT, 1, EventScript_RocketEggSentToPC
	closemessage
	return

EventScript_RocketEggSentToPC::
	msgbox Text_RocketEggSentToPC
	return

EventScript_RocketEggNoRoom::
	msgbox Text_RocketEggNoRoom
	msgbox Text_RocketBagFullOfficer
	return

@ The MEW EGG went to the party or the PC. One MEW per game: MEW no longer
@ hides under the truck on the VERMILION quay (FLAG_FOUGHT_MEW), and the truck
@ tells what happened instead (FLAG_GOT_MEW_EGG).
EventScript_GotMewEgg::
	setflag FLAG_FOUGHT_MEW
	setflag FLAG_GOT_MEW_EGG
	setvar VAR_0x8004, ROCKET_BONUS_NEW_ISLAND
	special SetRocketRewardBit
	return
