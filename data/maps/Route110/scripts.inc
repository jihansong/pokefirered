Route110_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route110_TYRival_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, Route110_TYRival_OnResume
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
@ TY_HOENN_RIVAL_110_119_V1
.equ LOCALID_ROUTE110_TY_RIVAL, 26

Route110_TYRival_OnTransition::
	special HoennZ3_SetupObjects
	end

Route110_TYRival_OnResume::
	special HoennZ3_SetupObjects
	end

Route110_TYRival_Trigger1::
	lockall
	setvar VAR_LAST_TALKED, LOCALID_ROUTE110_TY_RIVAL
	applymovement LOCALID_PLAYER, Route110_TYRival_CenterFromLeft
	waitmovement 0
	goto Route110_TYRival_Start
	end

Route110_TYRival_Trigger2::
	lockall
	setvar VAR_LAST_TALKED, LOCALID_ROUTE110_TY_RIVAL
	applymovement LOCALID_PLAYER, Route110_TYRival_Center
	waitmovement 0
	goto Route110_TYRival_Start
	end

Route110_TYRival_Trigger3::
	lockall
	setvar VAR_LAST_TALKED, LOCALID_ROUTE110_TY_RIVAL
	applymovement LOCALID_PLAYER, Route110_TYRival_CenterFromRight
	waitmovement 0
	goto Route110_TYRival_Start
	end

Route110_TYRival_Interact::
	lockall
	faceplayer
	goto Route110_TYRival_Start
	end

Route110_TYRival_Start::
	faceplayer
	goto_if_lt VAR_HOENN_SCENE_BIRCH, 3, Route110_TYRival_Done
	goto_if_set FLAG_HOENN_GOT_RIVAL110_GIFT, Route110_TYRival_Done
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route110_TYRival_Brendan
	goto_if_defeated TRAINER_HOENN_MAY_ROUTE_110_TORCHIC, Route110_TYRival_Reward
	playbgm MUS_ENCOUNTER_MAY, FALSE
	msgbox Route110_TYRival_MayIntro
	trainerbattle_single TRAINER_HOENN_MAY_ROUTE_110_TORCHIC, Route110_TYRival_MayBattleIntro, Route110_TYRival_MayDefeat, Route110_TYRival_Reward, NO_MUSIC
	goto Route110_TYRival_Reward
	end

Route110_TYRival_Brendan::
	goto_if_defeated TRAINER_HOENN_BRENDAN_ROUTE_110_TORCHIC, Route110_TYRival_Reward
	playbgm MUS_ENCOUNTER_BRENDAN, FALSE
	msgbox Route110_TYRival_BrendanIntro
	trainerbattle_single TRAINER_HOENN_BRENDAN_ROUTE_110_TORCHIC, Route110_TYRival_BrendanBattleIntro, Route110_TYRival_BrendanDefeat, Route110_TYRival_Reward, NO_MUSIC
	goto Route110_TYRival_Reward
	end

Route110_TYRival_Reward::
	goto_if_set FLAG_HOENN_GOT_RIVAL110_GIFT, Route110_TYRival_Done
	goto_if_set FLAG_GOT_ITEMFINDER, Route110_TYRival_Known
	checkitem ITEM_ITEMFINDER
	goto_if_eq VAR_RESULT, TRUE, Route110_TYRival_Known
	checkpcitem ITEM_ITEMFINDER
	goto_if_eq VAR_RESULT, TRUE, Route110_TYRival_Known
	msgbox Route110_TYRival_FreshText
	checkitemspace ITEM_ITEMFINDER
	goto_if_eq VAR_RESULT, FALSE, Route110_TYRival_Full
	giveitem ITEM_ITEMFINDER
	goto_if_eq VAR_RESULT, FALSE, Route110_TYRival_Full
	goto Route110_TYRival_Thanks
	end

Route110_TYRival_Known::
	msgbox Route110_TYRival_KnownText
	goto Route110_TYRival_Thanks
	end

Route110_TYRival_Thanks::
	setflag FLAG_HOENN_GOT_RIVAL110_GIFT
	msgbox Route110_TYRival_NextText
	closemessage
	setvar VAR_TEMP_0, 1
	setflag FLAG_TEMP_11
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE110_TY_RIVAL
	fadescreen FADE_FROM_BLACK
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

Route110_TYRival_Full::
	msgbox Route110_TYRival_FullText
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

Route110_TYRival_Done::
	releaseall
	end

Route110_TYRival_CenterFromLeft::
	walk_right
	walk_up
	step_end

Route110_TYRival_Center::
	walk_up
	step_end

Route110_TYRival_CenterFromRight::
	walk_left
	walk_up
	step_end
@ END PATCH
