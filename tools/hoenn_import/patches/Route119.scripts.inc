

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

