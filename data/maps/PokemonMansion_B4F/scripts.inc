PokemonMansion_B4F_MapScripts::
	.byte 0

@ The researcher who stayed to the end of the MEWTWO project fills in what the
@ diaries left out, then hands over his FINAL NOTES, TM29 and a TWISTEDSPOON.
PokemonMansion_B4F_EventScript_Researcher::
	lock
	faceplayer
	goto_if_set FLAG_GOT_MANSION_RESEARCHER_NOTES, PokemonMansion_B4F_EventScript_ResearcherAfter
	msgbox PokemonMansion_B4F_Text_YouReadThemAll
	msgbox PokemonMansion_B4F_Text_HowMewCame
	msgbox PokemonMansion_B4F_Text_DayMewtwoEscaped
	msgbox PokemonMansion_B4F_Text_TakeTheseNotes
	checkitemspace ITEM_TWISTED_SPOON
	goto_if_eq VAR_RESULT, FALSE, PokemonMansion_B4F_EventScript_NoRoom
	giveitem ITEM_FINAL_NOTES
	giveitem ITEM_TM29
	giveitem ITEM_TWISTED_SPOON
	setflag FLAG_GOT_MANSION_RESEARCHER_NOTES
	msgbox PokemonMansion_B4F_Text_ResearcherAfter
	release
	end

PokemonMansion_B4F_EventScript_NoRoom::
	msgbox PokemonMansion_B4F_Text_BagIsFull
	release
	end

PokemonMansion_B4F_EventScript_ResearcherAfter::
	msgbox PokemonMansion_B4F_Text_ResearcherAfter
	release
	end
