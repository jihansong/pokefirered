@ Event 7: the yard's generator, the second of the three PIKACHU branches.
SlateportCity_SternsShipyard_1F_EventScript_Generator::
	lock
	msgbox SlateportCity_SternsShipyard_1F_Text_Generator
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	goto_if_eq VAR_RESULT, PARTY_SIZE, EventScript_ReleaseEnd
	setflag FLAG_HOENN_PIKACHU_SHIPYARD_SEEN
	msgbox SlateportCity_SternsShipyard_1F_Text_GeneratorPikachu
	release
	end
