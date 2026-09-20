Route124_MapScripts::
	.byte 0

Route124_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_SPENCER, Route124_Text_H0_0, Route124_Text_H0_1
	msgbox Route124_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_ROLAND, Route124_Text_H1_0, Route124_Text_H1_1
	msgbox Route124_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_JENNY_1, Route124_Text_H2_0, Route124_Text_H2_1
	msgbox Route124_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_GRACE, Route124_Text_H3_0, Route124_Text_H3_1
	msgbox Route124_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_CHAD, Route124_Text_H4_0, Route124_Text_H4_1
	msgbox Route124_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_HItem68::
	finditem ITEM_RED_SHARD
	end

Route124_EventScript_HItem69::
	finditem ITEM_BLUE_SHARD
	end

Route124_EventScript_HItem70::
	finditem ITEM_YELLOW_SHARD
	end

Route124_EventScript_H5::
	trainerbattle_double TRAINER_HOENN_LILA_AND_ROY_1, Route124_Text_H5_0, Route124_Text_H5_1, Route124_Text_H5_1
	msgbox Route124_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H6::
	trainerbattle_double TRAINER_HOENN_LILA_AND_ROY_1, Route124_Text_H6_0, Route124_Text_H6_1, Route124_Text_H6_1
	msgbox Route124_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_DECLAN, Route124_Text_H7_0, Route124_Text_H7_1
	msgbox Route124_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_ISABELLA, Route124_Text_H8_0, Route124_Text_H8_1
	msgbox Route124_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route124_EventScript_H9::
	msgbox Route124_Text_H9, MSGBOX_SIGN
	end

