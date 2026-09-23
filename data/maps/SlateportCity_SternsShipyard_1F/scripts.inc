SlateportCity_SternsShipyard_1F_MapScripts::
	.byte 0

SlateportCity_SternsShipyard_1F_EventScript_H0::
	msgbox SlateportCity_SternsShipyard_1F_Text_H0, MSGBOX_NPC
	end

SlateportCity_SternsShipyard_1F_EventScript_H1::
	msgbox SlateportCity_SternsShipyard_1F_Text_H1, MSGBOX_NPC
	end

SlateportCity_SternsShipyard_1F_EventScript_H2::
	msgbox SlateportCity_SternsShipyard_1F_Text_H2, MSGBOX_NPC
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
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
@ END PATCH
