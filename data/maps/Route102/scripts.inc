Route102_MapScripts::
	.byte 0

Route102_EventScript_H0::
	msgbox Route102_Text_H0, MSGBOX_NPC
	end

Route102_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_CALVIN_1, Route102_Text_H1_0, Route102_Text_H1_1
	msgbox Route102_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_RICK, Route102_Text_H2_0, Route102_Text_H2_1
	msgbox Route102_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_TIANA, Route102_Text_H3_0, Route102_Text_H3_1
	msgbox Route102_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H4::
	msgbox Route102_Text_H4, MSGBOX_NPC
	end

Route102_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_ALLEN, Route102_Text_H5_0, Route102_Text_H5_1
	msgbox Route102_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route102_EventScript_H6::
	msgbox Route102_Text_H6, MSGBOX_SIGN
	end

Route102_EventScript_H7::
	msgbox Route102_Text_H7, MSGBOX_SIGN
	end

