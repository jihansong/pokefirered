@ v0.11.0 E3 (docs/v0.11.0-plan.md 4.3): BIRCH's child, of the other gender
@ to the player (one object; HoennZ3_SetupObjects picks the picture), shown
@ while VAR_HOENN_SCENE_BIRCH = 2. After the battle they go back to the LAB
@ (user decision 2026-09-27). Losing whites out with the var still 2, so the
@ battle is there again.
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
	msgbox Route103_Text_MayIntro
	call_if_ne VAR_0x8008, PARTY_SIZE, Route103_EventScript_MayPikachu
	trainerbattle_single TRAINER_HOENN_MAY_ROUTE_103_TORCHIC, Route103_Text_MayBattleIntro, Route103_Text_MayDefeat, Route103_EventScript_MayDefeated
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
	msgbox Route103_Text_BrendanIntro
	call_if_ne VAR_0x8008, PARTY_SIZE, Route103_EventScript_BrendanPikachu
	trainerbattle_single TRAINER_HOENN_BRENDAN_ROUTE_103_TORCHIC, Route103_Text_BrendanBattleIntro, Route103_Text_BrendanDefeat, Route103_EventScript_BrendanDefeated
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
	release
	end
