Route110_MapScripts::
	.byte 0

Route110_EventScript_H0::
	msgbox Route110_Text_H0, MSGBOX_NPC
	end

Route110_EventScript_H1::
	msgbox Route110_Text_H1, MSGBOX_NPC
	end

Route110_EventScript_H2::
	msgbox Route110_Text_H2, MSGBOX_NPC
	end

Route110_EventScript_H3::
	msgbox Route110_Text_H3, MSGBOX_NPC
	end

Route110_EventScript_H4::
	msgbox Route110_Text_H4, MSGBOX_NPC
	end

Route110_EventScript_H5::
	msgbox Route110_Text_H5, MSGBOX_NPC
	end

Route110_EventScript_H6::
	msgbox Route110_Text_H6, MSGBOX_NPC
	end

Route110_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_JASMINE, Route110_Text_H7_0, Route110_Text_H7_1
	msgbox Route110_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_ANTHONY, Route110_Text_H8_0, Route110_Text_H8_1
	msgbox Route110_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_ABIGAIL_1, Route110_Text_H9_0, Route110_Text_H9_1
	msgbox Route110_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_BENJAMIN_1, Route110_Text_H10_0, Route110_Text_H10_1
	msgbox Route110_Text_H10_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H11::
	trainerbattle_single TRAINER_HOENN_EDWARD, Route110_Text_H11_0, Route110_Text_H11_1
	msgbox Route110_Text_H11_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H12::
	trainerbattle_single TRAINER_HOENN_JACLYN, Route110_Text_H12_0, Route110_Text_H12_1
	msgbox Route110_Text_H12_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H13::
	trainerbattle_single TRAINER_HOENN_EDWIN_1, Route110_Text_H13_0, Route110_Text_H13_1
	msgbox Route110_Text_H13_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H14::
	trainerbattle_single TRAINER_HOENN_DALE, Route110_Text_H14_0, Route110_Text_H14_1
	msgbox Route110_Text_H14_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_HItem18::
	finditem ITEM_DIRE_HIT
	end

Route110_EventScript_HItem19::
	finditem ITEM_RARE_CANDY
	end

Route110_EventScript_H15::
	msgbox Route110_Text_H15, MSGBOX_NPC
	end

Route110_EventScript_H16::
	trainerbattle_single TRAINER_HOENN_JACOB, Route110_Text_H16_0, Route110_Text_H16_1
	msgbox Route110_Text_H16_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H17::
	trainerbattle_single TRAINER_HOENN_TIMMY, Route110_Text_H17_0, Route110_Text_H17_1
	msgbox Route110_Text_H17_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H18::
	trainerbattle_single TRAINER_HOENN_ISABEL_1, Route110_Text_H18_0, Route110_Text_H18_1
	msgbox Route110_Text_H18_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H19::
	trainerbattle_single TRAINER_HOENN_KALEB, Route110_Text_H19_0, Route110_Text_H19_1
	msgbox Route110_Text_H19_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H20::
	trainerbattle_single TRAINER_HOENN_ALYSSA, Route110_Text_H20_0, Route110_Text_H20_1
	msgbox Route110_Text_H20_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_H21::
	trainerbattle_single TRAINER_HOENN_JOSEPH, Route110_Text_H21_0, Route110_Text_H21_1
	msgbox Route110_Text_H21_2, MSGBOX_AUTOCLOSE
	end

Route110_EventScript_HItem20::
	finditem ITEM_ELIXIR
	end

Route110_EventScript_H22::
	msgbox Route110_Text_H22, MSGBOX_SIGN
	end

Route110_EventScript_H23::
	msgbox Route110_Text_H23, MSGBOX_SIGN
	end

Route110_EventScript_H24::
	msgbox Route110_Text_H24, MSGBOX_SIGN
	end

Route110_EventScript_H25::
	msgbox Route110_Text_H25, MSGBOX_SIGN
	end

Route110_EventScript_H26::
	msgbox Route110_Text_H26, MSGBOX_SIGN
	end

Route110_EventScript_H27::
	msgbox Route110_Text_H27, MSGBOX_SIGN
	end

Route110_EventScript_H28::
	msgbox Route110_Text_H28, MSGBOX_SIGN
	end

Route110_EventScript_H29::
	msgbox Route110_Text_H29, MSGBOX_SIGN
	end

Route110_EventScript_H30::
	msgbox Route110_Text_H30, MSGBOX_SIGN
	end

Route110_EventScript_H31::
	msgbox Route110_Text_H31, MSGBOX_SIGN
	end

Route110_EventScript_H32::
	msgbox Route110_Text_H32, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ The roadside board shows the run the south gate keeps (event 1).
Route110_EventScript_Board::
	special CyclingRoad_GetRecord
	goto_if_eq VAR_RESULT, 0, Route110_EventScript_BoardEmpty
	buffernumberstring STR_VAR_1, VAR_RESULT
	msgbox Route110_Text_BoardRecord, MSGBOX_SIGN
	end

Route110_EventScript_BoardEmpty::
	msgbox Route110_Text_BoardEmpty, MSGBOX_SIGN
	end
@ END PATCH
