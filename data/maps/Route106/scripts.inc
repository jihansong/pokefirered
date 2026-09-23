Route106_MapScripts::
	.byte 0

Route106_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_DOUGLAS, Route106_Text_H0_0, Route106_Text_H0_1
	msgbox Route106_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route106_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_KYLA, Route106_Text_H1_0, Route106_Text_H1_1
	msgbox Route106_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route106_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_ELLIOT_1, Route106_Text_H2_0, Route106_Text_H2_1
	msgbox Route106_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route106_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_NED, Route106_Text_H3_0, Route106_Text_H3_1
	msgbox Route106_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route106_EventScript_HItem14::
	finditem ITEM_PROTEIN
	end

Route106_EventScript_H4::
	msgbox Route106_Text_H4, MSGBOX_SIGN
	end
