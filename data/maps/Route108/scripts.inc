Route108_MapScripts::
	.byte 0

Route108_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_JEROME, Route108_Text_H0_0, Route108_Text_H0_1
	msgbox Route108_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_TARA, Route108_Text_H1_0, Route108_Text_H1_1
	msgbox Route108_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_MATTHEW, Route108_Text_H2_0, Route108_Text_H2_1
	msgbox Route108_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_MISSY, Route108_Text_H3_0, Route108_Text_H3_1
	msgbox Route108_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_CAROLINA, Route108_Text_H4_0, Route108_Text_H4_1
	msgbox Route108_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_CORY_1, Route108_Text_H5_0, Route108_Text_H5_1
	msgbox Route108_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route108_EventScript_HItem15::
	finditem ITEM_STAR_PIECE
	end
