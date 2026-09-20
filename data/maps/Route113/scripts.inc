Route113_MapScripts::
	.byte 0

Route113_EventScript_H0::
	msgbox Route113_Text_H0, MSGBOX_NPC
	end

Route113_EventScript_H1::
	msgbox Route113_Text_H1, MSGBOX_NPC
	end

Route113_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_JAYLEN, Route113_Text_H2_0, Route113_Text_H2_1
	msgbox Route113_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_DILLON, Route113_Text_H3_0, Route113_Text_H3_1
	msgbox Route113_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_MADELINE_1, Route113_Text_H4_0, Route113_Text_H4_1
	msgbox Route113_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_HItem26::
	finditem ITEM_MAX_ETHER
	end

Route113_EventScript_HItem27::
	finditem ITEM_SUPER_REPEL
	end

Route113_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_LAO_1, Route113_Text_H5_0, Route113_Text_H5_1
	msgbox Route113_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_LUNG, Route113_Text_H6_0, Route113_Text_H6_1
	msgbox Route113_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H7::
	trainerbattle_double TRAINER_HOENN_TORI_AND_TIA, Route113_Text_H7_0, Route113_Text_H7_1, Route113_Text_H7_1
	msgbox Route113_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H8::
	trainerbattle_double TRAINER_HOENN_TORI_AND_TIA, Route113_Text_H8_0, Route113_Text_H8_1, Route113_Text_H8_1
	msgbox Route113_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_HItem28::
	finditem ITEM_HYPER_POTION
	end

Route113_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_WYATT, Route113_Text_H9_0, Route113_Text_H9_1
	msgbox Route113_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_LAWRENCE, Route113_Text_H10_0, Route113_Text_H10_1
	msgbox Route113_Text_H10_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H11::
	trainerbattle_single TRAINER_HOENN_SOPHIE, Route113_Text_H11_0, Route113_Text_H11_1
	msgbox Route113_Text_H11_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H12::
	trainerbattle_single TRAINER_HOENN_COBY, Route113_Text_H12_0, Route113_Text_H12_1
	msgbox Route113_Text_H12_2, MSGBOX_AUTOCLOSE
	end

Route113_EventScript_H13::
	msgbox Route113_Text_H13, MSGBOX_SIGN
	end

Route113_EventScript_H14::
	msgbox Route113_Text_H14, MSGBOX_SIGN
	end

Route113_EventScript_H15::
	msgbox Route113_Text_H15, MSGBOX_SIGN
	end

Route113_EventScript_H16::
	msgbox Route113_Text_H16, MSGBOX_SIGN
	end

