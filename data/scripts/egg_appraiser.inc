@ Roadmap 2, event 8: the egg appraiser. He shows up at both day cares once
@ the player has had an egg. He reads the first egg in the party, and once
@ gives away a special egg that always hatches into a shiny JOHTO baby.
EventScript_EggAppraiser::
	lock
	faceplayer
	goto_if_unset FLAG_GOT_EGG_APPRAISER_EGG, EventScript_EggAppraiserOfferEgg
EventScript_EggAppraiserAppraise::
	specialvar VAR_RESULT, AppraisePartyEgg
	goto_if_eq VAR_RESULT, FALSE, EventScript_EggAppraiserNoEgg
	msgbox Text_EggAppraiserLetMeSee
	call_if_eq VAR_0x8005, 0, EventScript_EggAppraiserHatchSoon
	call_if_eq VAR_0x8005, 1, EventScript_EggAppraiserHatchWhile
	call_if_eq VAR_0x8005, 2, EventScript_EggAppraiserHatchLong
	call_if_eq VAR_0x8006, TRUE, EventScript_EggAppraiserShiny
	release
	end

EventScript_EggAppraiserHatchSoon::
	msgbox Text_EggAppraiserHatchSoon
	return

EventScript_EggAppraiserHatchWhile::
	msgbox Text_EggAppraiserHatchWhile
	return

EventScript_EggAppraiserHatchLong::
	msgbox Text_EggAppraiserHatchLong
	return

EventScript_EggAppraiserShiny::
	msgbox Text_EggAppraiserShiny
	return

EventScript_EggAppraiserNoEgg::
	msgbox Text_EggAppraiserNoEgg
	release
	end

EventScript_EggAppraiserOfferEgg::
	msgbox Text_EggAppraiserIntro
	specialvar VAR_RESULT, GiveEggAppraiserEgg
	goto_if_eq VAR_RESULT, 2, EventScript_EggAppraiserNoRoom
	setflag FLAG_GOT_EGG_APPRAISER_EGG
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_OBTAIN_ITEM
	message Text_EggAppraiserReceivedEgg
	waitmessage
	waitfanfare
	call_if_eq VAR_RESULT, 1, EventScript_EggAppraiserEggToPC
	textcolor NPC_TEXT_COLOR_MALE
	msgbox Text_EggAppraiserTakeCare
	release
	end

EventScript_EggAppraiserEggToPC::
	msgbox Text_EggAppraiserEggSentToPC
	return

EventScript_EggAppraiserNoRoom::
	msgbox Text_EggAppraiserNoRoom
	release
	end

Text_EggAppraiserIntro::
    .string "I'm an EGG appraiser. I can tell\n"
    .string "what's growing inside an EGG just\l"
    .string "by holding it.\p"
    .string "Ah, you've raised an EGG yourself!\n"
    .string "Then you're just the TRAINER I was\l"
    .string "hoping for.\p"
    .string "A friend in JOHTO left this EGG\n"
    .string "with me. It glitters in a way I've\l"
    .string "never seen. Please, hatch it for\l"
    .string "me!$"

Text_EggAppraiserReceivedEgg::
    .string "{PLAYER} received an EGG!$"

Text_EggAppraiserEggSentToPC::
    .string "There's no room in your party, so\n"
    .string "the EGG was sent to a PC BOX.$"

Text_EggAppraiserTakeCare::
    .string "Something from far-off JOHTO is\n"
    .string "inside. Come show me your EGGS any\l"
    .string "time!$"

Text_EggAppraiserNoRoom::
    .string "Oh dear, your party and BOXES are\n"
    .string "full. Make some room and come\l"
    .string "back.$"

Text_EggAppraiserNoEgg::
    .string "Bring an EGG in your party and\n"
    .string "I'll appraise it for you.$"

Text_EggAppraiserLetMeSee::
    .string "Let me see that EGG…\p"
    .string "Hmm… I sense a {STR_VAR_1}-type\n"
    .string "POKéMON inside.$"

Text_EggAppraiserHatchSoon::
    .string "It's moving around a lot. It'll\n"
    .string "hatch very soon!$"

Text_EggAppraiserHatchWhile::
    .string "It's growing nicely. It will hatch\n"
    .string "after a good long walk.$"

Text_EggAppraiserHatchLong::
    .string "It's fast asleep. It'll be a long\n"
    .string "while before it hatches.$"

Text_EggAppraiserShiny::
    .string "And… oh my! It glitters! This one\n"
    .string "will hatch in a special color!$"
