Route125_MapScripts::
	.byte 0

Route125_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_NOLEN, Route125_Text_H0_0, Route125_Text_H0_1
	msgbox Route125_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_STAN, Route125_Text_H1_0, Route125_Text_H1_1
	msgbox Route125_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_TANYA, Route125_Text_H2_0, Route125_Text_H2_1
	msgbox Route125_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_SHARON, Route125_Text_H3_0, Route125_Text_H3_1
	msgbox Route125_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_ERNEST_1, Route125_Text_H4_0, Route125_Text_H4_1
	msgbox Route125_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H5::
	trainerbattle_double TRAINER_HOENN_KIM_AND_IRIS, Route125_Text_H5_0, Route125_Text_H5_1, Route125_Text_H5_1
	msgbox Route125_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H6::
	trainerbattle_double TRAINER_HOENN_KIM_AND_IRIS, Route125_Text_H6_0, Route125_Text_H6_1, Route125_Text_H6_1
	msgbox Route125_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_PRESLEY, Route125_Text_H7_0, Route125_Text_H7_1
	msgbox Route125_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_AURON, Route125_Text_H8_0, Route125_Text_H8_1
	msgbox Route125_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route125_EventScript_HItem71::
	finditem ITEM_BIG_PEARL
	end

