MtPyre_2F_MapScripts::
	.byte 0

MtPyre_2F_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_MARK, MtPyre_2F_Text_H0_0, MtPyre_2F_Text_H0_1
	msgbox MtPyre_2F_Text_H0_2, MSGBOX_AUTOCLOSE
	end

MtPyre_2F_EventScript_HItem101::
	finditem ITEM_ULTRA_BALL
	end

MtPyre_2F_EventScript_H1::
	msgbox MtPyre_2F_Text_H1, MSGBOX_NPC
	end

MtPyre_2F_EventScript_H2::
	msgbox MtPyre_2F_Text_H2, MSGBOX_NPC
	end

MtPyre_2F_EventScript_H3::
	trainerbattle_double TRAINER_HOENN_DEZ_AND_LUKE, MtPyre_2F_Text_H3_0, MtPyre_2F_Text_H3_1, MtPyre_2F_Text_H3_1
	msgbox MtPyre_2F_Text_H3_2, MSGBOX_AUTOCLOSE
	end

MtPyre_2F_EventScript_H4::
	trainerbattle_double TRAINER_HOENN_DEZ_AND_LUKE, MtPyre_2F_Text_H4_0, MtPyre_2F_Text_H4_1, MtPyre_2F_Text_H4_1
	msgbox MtPyre_2F_Text_H4_2, MSGBOX_AUTOCLOSE
	end

MtPyre_2F_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_ZANDER, MtPyre_2F_Text_H5_0, MtPyre_2F_Text_H5_1
	msgbox MtPyre_2F_Text_H5_2, MSGBOX_AUTOCLOSE
	end

MtPyre_2F_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_LEAH, MtPyre_2F_Text_H6_0, MtPyre_2F_Text_H6_1
	msgbox MtPyre_2F_Text_H6_2, MSGBOX_AUTOCLOSE
	end

