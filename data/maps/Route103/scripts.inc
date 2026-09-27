Route103_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route103_OnTransition
	.byte 0

Route103_EventScript_H0::
	msgbox Route103_Text_H0, MSGBOX_NPC
	end

Route103_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_DAISY, Route103_Text_H1_0, Route103_Text_H1_1
	msgbox Route103_Text_H1_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H2::
	trainerbattle_double TRAINER_HOENN_AMY_AND_LIV_1, Route103_Text_H2_0, Route103_Text_H2_1, Route103_Text_H2_1
	msgbox Route103_Text_H2_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H3::
	trainerbattle_double TRAINER_HOENN_AMY_AND_LIV_1, Route103_Text_H3_0, Route103_Text_H3_1, Route103_Text_H3_1
	msgbox Route103_Text_H3_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H4::
	trainerbattle_single TRAINER_HOENN_ANDREW, Route103_Text_H4_0, Route103_Text_H4_1
	msgbox Route103_Text_H4_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H5::
	msgbox Route103_Text_H5, MSGBOX_NPC
	end

Route103_EventScript_H6::
	trainerbattle_single TRAINER_HOENN_MIGUEL_1, Route103_Text_H6_0, Route103_Text_H6_1
	msgbox Route103_Text_H6_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_HItem7::
	finditem ITEM_GUARD_SPEC
	end

Route103_EventScript_H7::
	trainerbattle_single TRAINER_HOENN_RHETT, Route103_Text_H7_0, Route103_Text_H7_1
	msgbox Route103_Text_H7_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H8::
	trainerbattle_single TRAINER_HOENN_MARCOS, Route103_Text_H8_0, Route103_Text_H8_1
	msgbox Route103_Text_H8_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H9::
	trainerbattle_single TRAINER_HOENN_ISABELLE, Route103_Text_H9_0, Route103_Text_H9_1
	msgbox Route103_Text_H9_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_H10::
	trainerbattle_single TRAINER_HOENN_PETE, Route103_Text_H10_0, Route103_Text_H10_1
	msgbox Route103_Text_H10_2, MSGBOX_AUTOCLOSE
	end

Route103_EventScript_HItem8::
	finditem ITEM_PP_UP
	end

Route103_EventScript_H11::
	msgbox Route103_Text_H11, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ v0.11.0 E3 (docs/v0.11.0-plan.md 4.3): BIRCH's child, of the other gender
@ to the player (one object; HoennZ3_SetupObjects picks the picture), shown
@ while VAR_HOENN_SCENE_BIRCH = 2. After the battle they go back to the LAB
@ (user decision 2026-09-27). Losing whites out with the var still 2, so the
@ battle is there again. Emerald's encounter themes play from the first line;
@ the battle has MUS_VS_RIVAL (GetBattleBGM).
.equ LOCALID_ROUTE103_RIVAL, 14

Route103_OnTransition::
	special HoennZ3_SetupObjects
	end

Route103_EventScript_Rival::
	lock
	faceplayer
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	copyvar VAR_0x8008, VAR_RESULT
	checkplayergender
	goto_if_eq VAR_RESULT, FEMALE, Route103_EventScript_Brendan
	playbgm MUS_ENCOUNTER_MAY, FALSE
	msgbox Route103_Text_MayIntro
	call_if_ne VAR_0x8008, PARTY_SIZE, Route103_EventScript_MayPikachu
	trainerbattle_single TRAINER_HOENN_MAY_ROUTE_103_TORCHIC, Route103_Text_MayBattleIntro, Route103_Text_MayDefeat, Route103_EventScript_MayDefeated, NO_MUSIC
	goto Route103_EventScript_MayDefeated
	end

Route103_EventScript_MayPikachu::
	msgbox Route103_Text_MayPikachu
	return

Route103_EventScript_MayDefeated::
	msgbox Route103_Text_MayPostBattle
	goto Route103_EventScript_RivalGoesToLab
	end

Route103_EventScript_Brendan::
	playbgm MUS_ENCOUNTER_BRENDAN, FALSE
	msgbox Route103_Text_BrendanIntro
	call_if_ne VAR_0x8008, PARTY_SIZE, Route103_EventScript_BrendanPikachu
	trainerbattle_single TRAINER_HOENN_BRENDAN_ROUTE_103_TORCHIC, Route103_Text_BrendanBattleIntro, Route103_Text_BrendanDefeat, Route103_EventScript_BrendanDefeated, NO_MUSIC
	goto Route103_EventScript_BrendanDefeated
	end

Route103_EventScript_BrendanPikachu::
	msgbox Route103_Text_BrendanPikachu
	return

Route103_EventScript_BrendanDefeated::
	msgbox Route103_Text_BrendanPostBattle
	goto Route103_EventScript_RivalGoesToLab
	end

@ The player can stand on any side, so the rival leaves behind a fade
@ rather than walking through anyone
Route103_EventScript_RivalGoesToLab::
	closemessage
	setvar VAR_HOENN_SCENE_BIRCH, 3
	setflag FLAG_HIDE_HOENN_RIVAL_ROUTE103
	clearflag FLAG_HIDE_HOENN_RIVAL_LAB
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE103_RIVAL
	fadescreen FADE_FROM_BLACK
	savebgm MUS_DUMMY
	fadedefaultbgm
	release
	end
@ END PATCH
