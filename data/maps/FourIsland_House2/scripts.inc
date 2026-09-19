FourIsland_House2_MapScripts::
	.byte 0

@ A weather researcher studying FOUR ISLAND's snow gives the player a CASTFORM
@ once, like the WEATHER INSTITUTE in R/S/E.
FourIsland_House2_EventScript_WeatherResearcher::
	lock
	faceplayer
	goto_if_set FLAG_GOT_CASTFORM, FourIsland_House2_EventScript_ResearcherAfterCastform
	msgbox FourIsland_House2_Text_ResearcherStudyingWeather, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, FourIsland_House2_EventScript_ResearcherDeclined
	setvar VAR_TEMP_1, SPECIES_CASTFORM
	call EventScript_GiveGiftMonLv25
	goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
	setflag FLAG_GOT_CASTFORM
	textcolor NPC_TEXT_COLOR_MALE
	msgbox FourIsland_House2_Text_ResearcherAfterCastform
	release
	end

FourIsland_House2_EventScript_ResearcherDeclined::
	msgbox FourIsland_House2_Text_ResearcherDeclined
	release
	end

FourIsland_House2_EventScript_ResearcherAfterCastform::
	msgbox FourIsland_House2_Text_ResearcherAfterCastform
	release
	end

FourIsland_House2_Text_ResearcherStudyingWeather::
    .string "I came from HOENN's WEATHER\n"
    .string "INSTITUTE to study the snow here.\p"
    .string "This CASTFORM changes its form with\n"
    .string "the weather, but it gets so bored\l"
    .string "while I take notes.\p"
    .string "Would you take it traveling with\n"
    .string "you?$"

FourIsland_House2_Text_ResearcherDeclined::
    .string "Oh… If you change your mind,\n"
    .string "I'll be right here.$"

FourIsland_House2_Text_ResearcherAfterCastform::
    .string "Try taking CASTFORM into battle\n"
    .string "when it's raining or sunny!$"
