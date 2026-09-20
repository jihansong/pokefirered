MtPyre_3F_MapScripts::
	.byte 0

MtPyre_3F_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_WILLIAM, MtPyre_3F_Text_H0_0, MtPyre_3F_Text_H0_1
	msgbox MtPyre_3F_Text_H0_2, MSGBOX_AUTOCLOSE
	end

MtPyre_3F_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_KAYLA, MtPyre_3F_Text_H1_0, MtPyre_3F_Text_H1_1
	msgbox MtPyre_3F_Text_H1_2, MSGBOX_AUTOCLOSE
	end

MtPyre_3F_EventScript_HItem102::
	finditem ITEM_SUPER_REPEL
	end

MtPyre_3F_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_GABRIELLE_1, MtPyre_3F_Text_H2_0, MtPyre_3F_Text_H2_1
	msgbox MtPyre_3F_Text_H2_2, MSGBOX_AUTOCLOSE
	end

