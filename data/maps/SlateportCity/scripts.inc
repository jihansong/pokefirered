SlateportCity_MapScripts::
	.byte 0

SlateportCity_EventScript_H0::
	msgbox SlateportCity_Text_H0, MSGBOX_NPC
	end

SlateportCity_EventScript_H1::
	msgbox SlateportCity_Text_H1, MSGBOX_NPC
	end

SlateportCity_EventScript_H2::
	msgbox SlateportCity_Text_H2, MSGBOX_NPC
	end

SlateportCity_EventScript_H3::
	msgbox SlateportCity_Text_H3, MSGBOX_NPC
	end

SlateportCity_EventScript_H4::
	msgbox SlateportCity_Text_H4, MSGBOX_NPC
	end

SlateportCity_EventScript_H5::
	msgbox SlateportCity_Text_H5, MSGBOX_NPC
	end

SlateportCity_EventScript_H6::
	msgbox SlateportCity_Text_H6, MSGBOX_NPC
	end

SlateportCity_EventScript_H7::
	msgbox SlateportCity_Text_H7, MSGBOX_NPC
	end

SlateportCity_EventScript_H8::
	msgbox SlateportCity_Text_H8, MSGBOX_NPC
	end

SlateportCity_EventScript_H9::
	msgbox SlateportCity_Text_H9, MSGBOX_NPC
	end

SlateportCity_EventScript_H10::
	msgbox SlateportCity_Text_H10, MSGBOX_NPC
	end

SlateportCity_EventScript_H11::
	msgbox SlateportCity_Text_H11, MSGBOX_NPC
	end

SlateportCity_EventScript_H12::
	msgbox SlateportCity_Text_H12, MSGBOX_NPC
	end

SlateportCity_EventScript_H13::
	msgbox SlateportCity_Text_H13, MSGBOX_NPC
	end

SlateportCity_EventScript_H14::
	msgbox SlateportCity_Text_H14, MSGBOX_NPC
	end

SlateportCity_EventScript_H15::
	msgbox SlateportCity_Text_H15, MSGBOX_NPC
	end

SlateportCity_EventScript_H16::
	msgbox SlateportCity_Text_H16, MSGBOX_NPC
	end

SlateportCity_EventScript_H17::
	lock
	faceplayer
	message Text_MayIHelpYou
	waitmessage
	pokemart SlateportCity_EventScript_H17_Items
	msgbox Text_PleaseComeAgain
	release
	end

	.align 2
SlateportCity_EventScript_H17_Items::
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CARBOS
	.2byte ITEM_ZINC
	.2byte ITEM_CALCIUM
	.2byte ITEM_HP_UP
	release
	end

SlateportCity_EventScript_H18::
	msgbox SlateportCity_Text_H18, MSGBOX_NPC
	end

SlateportCity_EventScript_H19::
	msgbox SlateportCity_Text_H19, MSGBOX_SIGN
	end

SlateportCity_EventScript_H20::
	msgbox SlateportCity_Text_H20, MSGBOX_SIGN
	end

SlateportCity_EventScript_H21::
	msgbox SlateportCity_Text_H21, MSGBOX_SIGN
	end

SlateportCity_EventScript_H22::
	msgbox SlateportCity_Text_H22, MSGBOX_SIGN
	end

SlateportCity_EventScript_H23::
	msgbox SlateportCity_Text_H23, MSGBOX_SIGN
	end

SlateportCity_EventScript_H24::
	msgbox SlateportCity_Text_H24, MSGBOX_SIGN
	end

SlateportCity_EventScript_H25::
	msgbox SlateportCity_Text_H25, MSGBOX_SIGN
	end

SlateportCity_EventScript_H26::
	msgbox SlateportCity_Text_H26, MSGBOX_SIGN
	end

