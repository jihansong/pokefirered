@ People react to a player who looks like a POKéMON after BILL's teleporter.
EventScript_ReactToPlayerMonForm::
	lock
	faceplayer
	special BufferPlayerMonFormName
	random 4
	switch VAR_RESULT
	case 0, EventScript_PlayerMonFormReaction0
	case 1, EventScript_PlayerMonFormReaction1
	case 2, EventScript_PlayerMonFormReaction2
	msgbox Text_PlayerMonFormReaction3
	release
	end

EventScript_PlayerMonFormReaction0::
	msgbox Text_PlayerMonFormReaction0
	release
	end

EventScript_PlayerMonFormReaction1::
	msgbox Text_PlayerMonFormReaction1
	release
	end

EventScript_PlayerMonFormReaction2::
	msgbox Text_PlayerMonFormReaction2
	release
	end

Text_PlayerMonFormReaction0::
    .string "Oh? A wild {STR_VAR_1}…\p"
    .string "It's staring at me like it wants\n"
    .string "to say something!$"

Text_PlayerMonFormReaction1::
    .string "Whoa! Where did this {STR_VAR_1}\n"
    .string "come from? Shoo, shoo!$"

Text_PlayerMonFormReaction2::
    .string "What a cute {STR_VAR_1}!\p"
    .string "…Hang on. Is that {STR_VAR_1}\n"
    .string "wearing sneakers?$"

Text_PlayerMonFormReaction3::
    .string "A {STR_VAR_1} walking around like\n"
    .string "a person?\p"
    .string "That reminds me of a rumor about\n"
    .string "BILL. He got stuck as a POKéMON\l"
    .string "once, too!$"
