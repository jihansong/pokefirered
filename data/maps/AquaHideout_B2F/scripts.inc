AquaHideout_B2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, AquaHideout_B2F_VS_OnTransition
	.byte 0

AquaHideout_B2F_EventScript_HItem111::
	finditem ITEM_NEST_BALL
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
AquaHideout_B2F_VS_Notice::
	lockall
	setvar VAR_TEMP_8, 1
	goto_if_set FLAG_HIDE_HOENN_AQUA_HIDEOUT_RAID, AquaHideout_B2F_VS_End
	playse SE_PIN
	applymovement 2, AquaHideout_B2F_VS_Movement_Notice
	waitmovement 0
AquaHideout_B2F_VS_End::
	releaseall
	end
AquaHideout_B2F_VS_Matt::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_AQUA_HIDEOUT_CLEARED, AquaHideout_B2F_VS_MattAfter
	trainerbattle_single TRAINER_HOENN_MATT, AquaHideout_B2F_VS_Text_MattIntro, AquaHideout_B2F_VS_Text_MattDefeat, AquaHideout_B2F_VS_Escape
	goto AquaHideout_B2F_VS_Escape
AquaHideout_B2F_VS_Escape::
	goto_if_set FLAG_HOENN_AQUA_HIDEOUT_CLEARED, AquaHideout_B2F_VS_MattAfter
	msgbox AquaHideout_B2F_VS_Text_MattEscape
	closemessage
	playse SE_SHIP
	applymovement 2, AquaHideout_B2F_VS_Movement_WatchSub
	applymovement 3, AquaHideout_B2F_VS_Movement_SubExit
	waitmovement 0
	playse SE_M_DIVE
	delay 32
	setflag FLAG_HOENN_AQUA_HIDEOUT_CLEARED
	setflag FLAG_HIDE_HOENN_AQUA_HIDEOUT_SUBMARINE
	removeobject 3
AquaHideout_B2F_VS_MattAfter::
	msgbox AquaHideout_B2F_VS_Text_MattAfter
	release
	end
AquaHideout_B2F_VS_Submarine::
	end

AquaHideout_B2F_VS_Movement_Notice:
	emote_exclamation_mark
	delay_16
	step_end

AquaHideout_B2F_VS_Movement_WatchSub:
	face_left
	step_end

AquaHideout_B2F_VS_Movement_SubExit:
	disable_anim
	walk_left
	walk_left
	walk_left
	delay_16
	delay_16
	step_end

AquaHideout_B2F_VS_Grunt4::
	trainerbattle_single TRAINER_HOENN_GRUNT_AQUA_HIDEOUT_4, AquaHideout_B2F_VS_Text_Grunt4Intro, AquaHideout_B2F_VS_Text_Grunt4Defeat, AquaHideout_B2F_VS_Grunt4After
	goto AquaHideout_B2F_VS_Grunt4After
AquaHideout_B2F_VS_Grunt4After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox AquaHideout_B2F_VS_Text_Grunt4After
	release
	end

AquaHideout_B2F_VS_Grunt6::
	trainerbattle_single TRAINER_HOENN_GRUNT_AQUA_HIDEOUT_6, AquaHideout_B2F_VS_Text_Grunt6Intro, AquaHideout_B2F_VS_Text_Grunt6Defeat, AquaHideout_B2F_VS_Grunt6After
	goto AquaHideout_B2F_VS_Grunt6After
AquaHideout_B2F_VS_Grunt6After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox AquaHideout_B2F_VS_Text_Grunt6After
	release
	end

AquaHideout_B2F_VS_Grunt8::
	trainerbattle_single TRAINER_HOENN_GRUNT_AQUA_HIDEOUT_8, AquaHideout_B2F_VS_Text_Grunt8Intro, AquaHideout_B2F_VS_Text_Grunt8Defeat, AquaHideout_B2F_VS_Grunt8After
	goto AquaHideout_B2F_VS_Grunt8After
AquaHideout_B2F_VS_Grunt8After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox AquaHideout_B2F_VS_Text_Grunt8After
	release
	end

AquaHideout_B2F_VS_OnTransition::
	special HoennVillain_SetupObjects
	end
@ END PATCH
