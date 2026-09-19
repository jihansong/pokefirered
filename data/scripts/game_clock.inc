@ Roadmap 2, event 9: the game clock. Set once on the first step after the
@ player has a POKéMON, and again at any time from the clock in the player's room.
EventScript_SetGameClockPrompt::
	lockall
	msgbox Text_ClockNotSet
	call EventScript_SetGameClock
	releaseall
	end

EventScript_SetGameClock::
	closemessage
	special StartSetGameClock
	waitstate
	special BufferGameClock
	msgbox Text_ClockIsSet
	return

EventScript_WallClock::
	lockall
	special BufferGameClock
	msgbox Text_WallClockShows
EventScript_ClockTimeOfDay::
	call_if_eq VAR_RESULT, TIME_MORNING, EventScript_WallClockMorning
	call_if_eq VAR_RESULT, TIME_DAY, EventScript_WallClockDay
	call_if_eq VAR_RESULT, TIME_NIGHT, EventScript_WallClockNight
	msgbox Text_WallClockChange, MSGBOX_YESNO
	call_if_eq VAR_RESULT, YES, EventScript_SetGameClock
	releaseall
	end

EventScript_WallClockMorning::
	msgbox Text_WallClockMorning
	return

EventScript_WallClockDay::
	msgbox Text_WallClockDay
	return

EventScript_WallClockNight::
	msgbox Text_WallClockNight
	return

Text_ClockNotSet::
    .string "The clock hasn't been set yet.\p"
    .string "Please set the day of the week and\n"
    .string "the time.$"

Text_ClockIsSet::
    .string "The clock was set to {STR_VAR_1}.$"

Text_WallClockShows::
    .string "It's a clock. It reads\n"
    .string "{STR_VAR_1}.$"

Text_WallClockMorning::
    .string "It's morning. Some POKéMON are\n"
    .string "only out at this hour.$"

Text_WallClockDay::
    .string "It's daytime.$"

Text_WallClockNight::
    .string "It's night. Night owls and ghosts\n"
    .string "come out now.$"

Text_WallClockChange::
    .string "Change the time?$"

EventScript_UsePokeWatch::
	lockall
	special BufferGameClock
	msgbox Text_PokeWatchShows
	goto EventScript_ClockTimeOfDay
	end

Text_PokeWatchShows::
    .string "{PLAYER} checked the POKéWATCH.\p"
    .string "It's {STR_VAR_1}.$"
