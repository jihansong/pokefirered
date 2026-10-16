Route119_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route119_TYRival_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, Route119_TYRival_OnResume
	.byte 0

Route119_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_GREG, Route119_Text_H0_0, Route119_Text_H0_1
	msgbox Route119_Text_H0_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_TAYLOR, Route119_Text_H1_0, Route119_Text_H1_1
	msgbox Route119_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_DONALD, Route119_Text_H2_0, Route119_Text_H2_1
	msgbox Route119_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H3::
	trainerbattle_single TRAINER_HOENN_JACKSON_1, Route119_Text_H3_0, Route119_Text_H3_1
	msgbox Route119_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_BRENT, Route119_Text_H4_0, Route119_Text_H4_1
	msgbox Route119_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H5::
	trainerbattle_single TRAINER_HOENN_CATHERINE_1, Route119_Text_H5_0, Route119_Text_H5_1
	msgbox Route119_Text_H5_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_DOUG, Route119_Text_H6_0, Route119_Text_H6_1
	msgbox Route119_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_KENT, Route119_Text_H7_0, Route119_Text_H7_1
	msgbox Route119_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_YASU, Route119_Text_H8_0, Route119_Text_H8_1
	msgbox Route119_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_TAKASHI, Route119_Text_H9_0, Route119_Text_H9_1
	msgbox Route119_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_HUGH, Route119_Text_H10_0, Route119_Text_H10_1
	msgbox Route119_Text_H10_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H11::
	trainerbattle_single TRAINER_HOENN_PHIL, Route119_Text_H11_0, Route119_Text_H11_1
	msgbox Route119_Text_H11_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_HItem46::
	finditem ITEM_SUPER_REPEL
	end

Route119_EventScript_HItem47::
	finditem ITEM_ZINC
	end

Route119_EventScript_HItem48::
	finditem ITEM_ELIXIR
	end

Route119_EventScript_HItem49::
	finditem ITEM_LEAF_STONE
	end

Route119_EventScript_HItem50::
	finditem ITEM_RARE_CANDY
	end

Route119_EventScript_HItem51::
	finditem ITEM_HYPER_POTION
	end

Route119_EventScript_H12::
	msgbox Route119_Text_H12, MSGBOX_NPC
	end

Route119_EventScript_H13::
	msgbox Route119_Text_H13, MSGBOX_NPC
	end

Route119_EventScript_HItem52::
	finditem ITEM_HYPER_POTION
	end

Route119_EventScript_H14::
	msgbox Route119_Text_H14, MSGBOX_NPC
	end

Route119_EventScript_H15::
	trainerbattle_single TRAINER_HOENN_HIDEO, Route119_Text_H15_0, Route119_Text_H15_1
	msgbox Route119_Text_H15_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H16::
	trainerbattle_single TRAINER_HOENN_CHRIS, Route119_Text_H16_0, Route119_Text_H16_1
	msgbox Route119_Text_H16_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H17::
	trainerbattle_single TRAINER_HOENN_RACHEL, Route119_Text_H17_0, Route119_Text_H17_1
	msgbox Route119_Text_H17_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H18::
	trainerbattle_single TRAINER_HOENN_DAYTON, Route119_Text_H18_0, Route119_Text_H18_1
	msgbox Route119_Text_H18_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_H19::
	trainerbattle_single TRAINER_HOENN_FABIAN, Route119_Text_H19_0, Route119_Text_H19_1
	msgbox Route119_Text_H19_2, MSGBOX_AUTOCLOSE
	end

Route119_EventScript_HItem53::
	finditem ITEM_NUGGET
	end

Route119_EventScript_HItem54::
	finditem ITEM_ELIXIR
	end

Route119_EventScript_H20::
	msgbox Route119_Text_H20, MSGBOX_SIGN
	end

Route119_EventScript_H21::
	msgbox Route119_Text_H21, MSGBOX_SIGN
	end

Route119_EventScript_H22::
	msgbox Route119_Text_H22, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ TY_HOENN_RIVAL_110_119_V1
.equ LOCALID_ROUTE119_TY_RIVAL, 30

Route119_TYRival_OnTransition::
	special HoennZ3_SetupObjects
	end

Route119_TYRival_OnResume::
	special HoennZ3_SetupObjects
	end

Route119_TYRival_Trigger1::
	lockall
	setvar VAR_LAST_TALKED, LOCALID_ROUTE119_TY_RIVAL
	applymovement LOCALID_PLAYER, Route119_TYRival_FaceDown
	waitmovement 0
	goto Route119_TYRival_Start
	end

Route119_TYRival_Trigger2::
	lockall
	setvar VAR_LAST_TALKED, LOCALID_ROUTE119_TY_RIVAL
	applymovement LOCALID_PLAYER, Route119_TYRival_StepLeftFaceDown
	waitmovement 0
	goto Route119_TYRival_Start
	end

Route119_TYRival_Interact::
	lockall
	faceplayer
	goto Route119_TYRival_Start
	end

Route119_TYRival_Start::
	faceplayer
	goto_if_unset FLAG_HOENN_WEATHER_RESCUED, Route119_TYRival_Done
	goto_if_lt VAR_HOENN_SCENE_BIRCH, 3, Route119_TYRival_Done
	goto_if_set FLAG_HOENN_GOT_RIVAL_FLY_REWARD, Route119_TYRival_Done
	goto_if_unset FLAG_HOENN_GOT_RIVAL110_GIFT, Route119_TYRival_Done
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route119_TYRival_Brendan
	goto_if_not_defeated TRAINER_HOENN_MAY_ROUTE_110_TORCHIC, Route119_TYRival_Done
	goto_if_defeated TRAINER_HOENN_MAY_ROUTE_119_TORCHIC, Route119_TYRival_Reward
	playbgm MUS_ENCOUNTER_MAY, FALSE
	msgbox Route119_TYRival_MayIntro
	trainerbattle_single TRAINER_HOENN_MAY_ROUTE_119_TORCHIC, Route119_TYRival_MayBattleIntro, Route119_TYRival_MayDefeat, Route119_TYRival_Reward, NO_MUSIC
	goto Route119_TYRival_Reward
	end

Route119_TYRival_Brendan::
	goto_if_not_defeated TRAINER_HOENN_BRENDAN_ROUTE_110_TORCHIC, Route119_TYRival_Done
	goto_if_defeated TRAINER_HOENN_BRENDAN_ROUTE_119_TORCHIC, Route119_TYRival_Reward
	playbgm MUS_ENCOUNTER_BRENDAN, FALSE
	msgbox Route119_TYRival_BrendanIntro
	trainerbattle_single TRAINER_HOENN_BRENDAN_ROUTE_119_TORCHIC, Route119_TYRival_BrendanBattleIntro, Route119_TYRival_BrendanDefeat, Route119_TYRival_Reward, NO_MUSIC
	goto Route119_TYRival_Reward
	end

Route119_TYRival_Reward::
	goto_if_set FLAG_HOENN_GOT_RIVAL_FLY_REWARD, Route119_TYRival_Done
	goto_if_set FLAG_GOT_HM02, Route119_TYRival_Known
	checkitem ITEM_HM02
	goto_if_eq VAR_RESULT, TRUE, Route119_TYRival_Known
	checkpcitem ITEM_HM02
	goto_if_eq VAR_RESULT, TRUE, Route119_TYRival_Known
	msgbox Route119_TYRival_FreshText
	checkitemspace ITEM_HM02
	goto_if_eq VAR_RESULT, FALSE, Route119_TYRival_Full
	giveitem ITEM_HM02
	goto_if_eq VAR_RESULT, FALSE, Route119_TYRival_Full
	setflag FLAG_HOENN_GOT_RIVAL_FLY_REWARD
	msgbox Route119_TYRival_FreshThanks
	goto Route119_TYRival_Leave
	end

Route119_TYRival_Known::
	msgbox Route119_TYRival_KnownText
	checkitemspace ITEM_TM02
	goto_if_eq VAR_RESULT, FALSE, Route119_TYRival_Full
	giveitem ITEM_TM02
	goto_if_eq VAR_RESULT, FALSE, Route119_TYRival_Full
	setflag FLAG_HOENN_GOT_RIVAL_FLY_REWARD
	msgbox Route119_TYRival_TechniqueText
	goto Route119_TYRival_Leave
	end

Route119_TYRival_Full::
	msgbox Route119_TYRival_FullText
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

Route119_TYRival_Leave::
	closemessage
	setvar VAR_TEMP_0, 1
	setflag FLAG_TEMP_11
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE119_TY_RIVAL
	fadescreen FADE_FROM_BLACK
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

Route119_TYRival_Done::
	releaseall
	end

Route119_TYRival_FaceDown::
	walk_in_place_faster_down
	step_end

Route119_TYRival_StepLeftFaceDown::
	walk_left
	walk_in_place_faster_down
	step_end
@ TY_HOENN_WEATHER_BRIDGE_V1
Route119_TYWeather_BridgeGuard1::
	msgbox Route119_TYWeather_BlockadeText1, MSGBOX_NPC
	end

Route119_TYWeather_BridgeGuard2::
	msgbox Route119_TYWeather_BlockadeText2, MSGBOX_NPC
	end

@ END PATCH
