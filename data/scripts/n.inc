@ Thunder Yellow v0.6.0: N, the young man who hears POKéMON (an homage). He
@ battles the player three times during the story (PEWTER MUSEUM, POKéMON
@ TOWER, SILPH CO.) and once more at his cabin on SIX ISLAND's WATER PATH.
@ Each time he tells the player what their PIKACHU is saying, from how close it is.

EventScript_NHearsPikachu::
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	goto_if_eq VAR_RESULT, PARTY_SIZE, EventScript_NNoPikachu
	specialvar VAR_RESULT, GetStarterPikachuFriendship
	goto_if_ge VAR_RESULT, 200, EventScript_NPikachuDevoted
	goto_if_ge VAR_RESULT, 100, EventScript_NPikachuFond
	msgbox Text_NPikachuUnsure
	return

EventScript_NPikachuFond::
	msgbox Text_NPikachuFond
	return

EventScript_NPikachuDevoted::
	msgbox Text_NPikachuDevoted
	return

EventScript_NNoPikachu::
	msgbox Text_NNoPikachu
	return

@ After each story battle he leaves.
EventScript_NLeaves::
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject VAR_LAST_TALKED
	fadescreen FADE_FROM_BLACK
	release
	end
