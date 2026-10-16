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
