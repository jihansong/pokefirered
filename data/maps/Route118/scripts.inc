Route118_MapScripts::
	.byte 0

Route118_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_PERRY, Route118_Text_H0_0, Route118_Text_H0_1
	msgbox Route118_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H1::
	msgbox Route118_Text_H1, MSGBOX_NPC
	end

Route118_EventScript_H2::
	msgbox Route118_Text_H2, MSGBOX_NPC
	end

Route118_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_ROSE_1, Route118_Text_H3_0, Route118_Text_H3_1
	msgbox Route118_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_WADE, Route118_Text_H4_0, Route118_Text_H4_1
	msgbox Route118_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_CHESTER, Route118_Text_H5_0, Route118_Text_H5_1
	msgbox Route118_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_BARNY, Route118_Text_H6_0, Route118_Text_H6_1
	msgbox Route118_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_DALTON_1, Route118_Text_H7_0, Route118_Text_H7_1
	msgbox Route118_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_HItem45::
	finditem ITEM_HYPER_POTION
	end

Route118_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_DEANDRE, Route118_Text_H8_0, Route118_Text_H8_1
	msgbox Route118_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route118_EventScript_H9::
	msgbox Route118_Text_H9, MSGBOX_SIGN
	end

Route118_EventScript_H10::
	msgbox Route118_Text_H10, MSGBOX_SIGN
	end
