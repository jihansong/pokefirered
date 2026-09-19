@ The Bug-Catching Contest in VIRIDIAN FOREST (see src/bug_contest.c)
BugContest_EventScript_Officer::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE01_GET, BugContest_EventScript_NeedBadge
	special CheckBugContestDay
	goto_if_eq VAR_RESULT, 0, BugContest_EventScript_NotContestDay
	goto_if_eq VAR_RESULT, 2, BugContest_EventScript_AlreadyEntered
	msgbox BugContest_Text_WouldYouLikeToEnter, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, BugContest_EventScript_Declined
	bufferpartymonnick STR_VAR_1, 0
	getpartysize
	goto_if_eq VAR_RESULT, 1, BugContest_EventScript_Enter
	msgbox BugContest_Text_WeWillHoldTheRest, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, BugContest_EventScript_Declined
BugContest_EventScript_Enter::
	special StartBugContest
	goto_if_eq VAR_RESULT, FALSE, BugContest_EventScript_NoRoomForBalls
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_OBTAIN_ITEM
	message BugContest_Text_ReceivedBalls
	waitmessage
	waitfanfare
	call EventScript_RestorePrevTextColor
	msgbox BugContest_Text_ContestRules
	closemessage
	warp MAP_VIRIDIAN_FOREST, 0
	waitstate
	release
	end

BugContest_EventScript_NeedBadge::
	msgbox BugContest_Text_NeedBadge
	release
	end

BugContest_EventScript_NotContestDay::
	msgbox BugContest_Text_NotContestDay
	release
	end

BugContest_EventScript_AlreadyEntered::
	msgbox BugContest_Text_AlreadyEntered
	release
	end

BugContest_EventScript_Declined::
	msgbox BugContest_Text_Declined
	release
	end

BugContest_EventScript_NoRoomForBalls::
	msgbox BugContest_Text_NoRoomForBalls
	release
	end

BugContest_EventScript_TimeUp::
	lockall
	playse SE_DING_DONG
	msgbox BugContest_Text_TimeUp
	closemessage
	setvar VAR_BUG_CONTEST_STATE, BUG_CONTEST_JUDGING
	warp MAP_ROUTE2_VIRIDIAN_FOREST_SOUTH_ENTRANCE, 7, 2
	waitstate
	releaseall
	end

BugContest_OnFrame_Forest::
	map_script_2 VAR_BUG_CONTEST_SWAP, 1, BugContest_EventScript_SwapCatch
	.2byte 0

BugContest_EventScript_SwapCatch::
	lockall
	special BufferBugContestSwapNames
	msgbox BugContest_Text_SwitchCatch, MSGBOX_YESNO
	setvar VAR_0x8004, FALSE
	call_if_eq VAR_RESULT, YES, BugContest_EventScript_KeepNew
	special ResolveBugContestSwap
	releaseall
	end

BugContest_EventScript_KeepNew::
	setvar VAR_0x8004, TRUE
	return

BugContest_OnFrame_NorthEntrance::
	map_script_2 VAR_BUG_CONTEST_STATE, BUG_CONTEST_ACTIVE, BugContest_EventScript_StayInForest
	.2byte 0

BugContest_EventScript_StayInForest::
	lockall
	msgbox BugContest_Text_StayInForest
	closemessage
	warp MAP_VIRIDIAN_FOREST, 2
	waitstate
	releaseall
	end

BugContest_OnFrame_SouthEntrance::
	map_script_2 VAR_BUG_CONTEST_STATE, BUG_CONTEST_ACTIVE, BugContest_EventScript_ReturnedEarly
	map_script_2 VAR_BUG_CONTEST_STATE, BUG_CONTEST_JUDGING, BugContest_EventScript_Judging
	.2byte 0

BugContest_EventScript_ReturnedEarly::
	lockall
	msgbox BugContest_Text_FinishEarly, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, BugContest_EventScript_StartJudging
	msgbox BugContest_Text_GoodLuck
	closemessage
	warp MAP_VIRIDIAN_FOREST, 0
	waitstate
	releaseall
	end

BugContest_EventScript_StartJudging::
	setvar VAR_BUG_CONTEST_STATE, BUG_CONTEST_JUDGING
BugContest_EventScript_Judging::
	lockall
	textcolor NPC_TEXT_COLOR_MALE
	msgbox BugContest_Text_JudgingBegins
	special JudgeBugContest
	copyvar VAR_0x8008, VAR_RESULT
	setvar VAR_0x8005, 3
	special BufferBugContestPlace
	playse SE_BALL_BOUNCE_1
	msgbox BugContest_Text_ThirdPlace
	setvar VAR_0x8005, 2
	special BufferBugContestPlace
	playse SE_BALL_BOUNCE_1
	msgbox BugContest_Text_SecondPlace
	setvar VAR_0x8005, 1
	special BufferBugContestPlace
	playfanfare MUS_LEVEL_UP
	msgbox BugContest_Text_FirstPlace
	waitfanfare
	special EndBugContest
	call_if_eq VAR_0x8008, 0, BugContest_EventScript_NoPrize
	call_if_eq VAR_0x8008, 1, BugContest_EventScript_FirstPrize
	call_if_eq VAR_0x8008, 2, BugContest_EventScript_SecondPrize
	call_if_eq VAR_0x8008, 3, BugContest_EventScript_ThirdPrize
	msgbox BugContest_Text_ReturnedYourMons
	releaseall
	end

BugContest_EventScript_NoPrize::
	msgbox BugContest_Text_BetterLuck
	return

BugContest_EventScript_FirstPrize::
	msgbox BugContest_Text_YouWonFirst
	giveitem ITEM_SUN_STONE
	return

BugContest_EventScript_SecondPrize::
	msgbox BugContest_Text_YouWonSecond
	giveitem ITEM_EVERSTONE
	return

BugContest_EventScript_ThirdPrize::
	msgbox BugContest_Text_YouWonThird
	giveitem ITEM_SITRUS_BERRY
	return

BugContest_Text_NeedBadge::
	.string "This is the entry desk for the\n"
	.string "Bug-Catching Contest.\p"
	.string "Come back once you've earned a\n"
	.string "GYM BADGE.$"

BugContest_Text_NotContestDay::
	.string "Today is {STR_VAR_1}.\p"
	.string "The Bug-Catching Contest is held on\n"
	.string "TUESDAY, THURSDAY and SATURDAY.\p"
	.string "(Check the day on your POKéWATCH.)$"

BugContest_Text_AlreadyEntered::
	.string "You've already entered today's\n"
	.string "contest. Come back another day!$"

BugContest_Text_WouldYouLikeToEnter::
	.string "Today is {STR_VAR_1}. That means\n"
	.string "the Bug-Catching Contest is on!\p"
	.string "Catch the best BUG POKéMON in the\n"
	.string "forest within 20 minutes.\p"
	.string "Would you like to enter?$"

BugContest_Text_WeWillHoldTheRest::
	.string "Only one POKéMON may enter:\n"
	.string "your {STR_VAR_1}.\p"
	.string "We'll look after your other\n"
	.string "POKéMON until the contest is over.\l"
	.string "Is that okay?$"

BugContest_Text_Declined::
	.string "Maybe next time, then.$"

BugContest_Text_NoRoomForBalls::
	.string "Oh, your BAG has no room for the\n"
	.string "contest BALLS.$"

BugContest_Text_ReceivedBalls::
	.string "{PLAYER} received 20 SAFARI BALLS\n"
	.string "for the contest!$"

BugContest_Text_ContestRules::
	.string "The one who catches the strongest\n"
	.string "BUG POKéMON wins.\p"
	.string "You can only keep one catch. You\n"
	.string "can't save during the contest.\p"
	.string "Come back here when you're done.\n"
	.string "Good luck!$"

BugContest_Text_TimeUp::
	.string "ANNOUNCER: Time's up!\n"
	.string "Please return to the gate!$"

BugContest_Text_SwitchCatch::
	.string "You already caught a {STR_VAR_1}.\p"
	.string "Switch it for the {STR_VAR_2}?$"

BugContest_Text_StayInForest::
	.string "The Bug-Catching Contest is still\n"
	.string "on! Please stay in the forest.$"

BugContest_Text_FinishEarly::
	.string "You still have time left.\n"
	.string "Do you want to finish now?$"

BugContest_Text_GoodLuck::
	.string "Good luck out there!$"

BugContest_Text_JudgingBegins::
	.string "The contest is over!\n"
	.string "Let's judge the POKéMON caught.$"

BugContest_Text_ThirdPlace::
	.string "Placing third was {STR_VAR_1},\n"
	.string "who caught a {STR_VAR_2}!\p"
	.string "The score was {STR_VAR_3} points!$"

BugContest_Text_SecondPlace::
	.string "Placing second was {STR_VAR_1},\n"
	.string "who caught a {STR_VAR_2}!\p"
	.string "The score was {STR_VAR_3} points!$"

BugContest_Text_FirstPlace::
	.string "This time's winner is {STR_VAR_1},\n"
	.string "who caught a {STR_VAR_2}!\p"
	.string "The winning score was {STR_VAR_3}\n"
	.string "points!$"

BugContest_Text_BetterLuck::
	.string "Too bad, {PLAYER}.\n"
	.string "Better luck next time!$"

BugContest_Text_YouWonFirst::
	.string "{PLAYER}, you took first place!\n"
	.string "Here's your prize!$"

BugContest_Text_YouWonSecond::
	.string "{PLAYER}, you took second place!\n"
	.string "Here's your prize!$"

BugContest_Text_YouWonThird::
	.string "{PLAYER}, you took third place!\n"
	.string "Here's your prize!$"

BugContest_Text_ReturnedYourMons::
	.string "Here are the POKéMON we were\n"
	.string "looking after. See you again!$"
