Route117_MapScripts::
	.byte 0

Route117_EventScript_H0::
	msgbox Route117_Text_H0, MSGBOX_NPC
	end

Route117_EventScript_H1::
	msgbox Route117_Text_H1, MSGBOX_NPC
	end

Route117_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_DYLAN_1, Route117_Text_H2_0, Route117_Text_H2_1
	msgbox Route117_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_LYDIA_1, Route117_Text_H3_0, Route117_Text_H3_1
	msgbox Route117_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_ISAAC_1, Route117_Text_H4_0, Route117_Text_H4_1
	msgbox Route117_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_HItem43::
	finditem ITEM_GREAT_BALL
	end

Route117_EventScript_HItem44::
	finditem ITEM_REVIVE
	end

Route117_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_MARIA_1, Route117_Text_H5_0, Route117_Text_H5_1
	msgbox Route117_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_DEREK, Route117_Text_H6_0, Route117_Text_H6_1
	msgbox Route117_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H7::
	trainerbattle_double TRAINER_HOENN_ANNA_AND_MEG_1, Route117_Text_H7_0, Route117_Text_H7_1, Route117_Text_H7_1
	msgbox Route117_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H8::
	trainerbattle_double TRAINER_HOENN_ANNA_AND_MEG_1, Route117_Text_H8_0, Route117_Text_H8_1, Route117_Text_H8_1
	msgbox Route117_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H9::
	msgbox Route117_Text_H9, MSGBOX_NPC
	end

Route117_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_BRANDI, Route117_Text_H10_0, Route117_Text_H10_1
	msgbox Route117_Text_H10_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H11::
	trainerbattle_single TRAINER_HOENN_AISHA, Route117_Text_H11_0, Route117_Text_H11_1
	msgbox Route117_Text_H11_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H12::
	trainerbattle_single TRAINER_HOENN_MELINA, Route117_Text_H12_0, Route117_Text_H12_1
	msgbox Route117_Text_H12_2, MSGBOX_AUTOCLOSE
	end

Route117_EventScript_H13::
	msgbox Route117_Text_H13, MSGBOX_SIGN
	end

Route117_EventScript_H14::
	msgbox Route117_Text_H14, MSGBOX_SIGN
	end

Route117_EventScript_H15::
	msgbox Route117_Text_H15, MSGBOX_SIGN
	end

