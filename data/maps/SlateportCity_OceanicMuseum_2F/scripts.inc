SlateportCity_OceanicMuseum_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SlateportCity_OceanicMuseum_2F_OnTransition
	.byte 0

SlateportCity_OceanicMuseum_2F_EventScript_H0::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H0, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H1::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H1, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H2::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H2, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H3::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H3, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H4::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H4, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H5::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H5, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H6::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H6, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H7::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H7, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H8::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H8, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H9::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H9, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H10::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H10, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H11::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H11, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H12::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H12, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H13::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H13, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H14::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H14, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H15::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H15, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H16::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H16, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H17::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H17, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H18::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H18, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H19::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H19, MSGBOX_SIGN
	end

SlateportCity_OceanicMuseum_2F_EventScript_H20::
	msgbox SlateportCity_OceanicMuseum_2F_Text_H20, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Event 2: two AQUA men stand at STERN's sea floor survey. Beat both and ARCHIE
@ comes up the stairs to call them off, and to have a look at the champion.
.equ LOCALID_MUSEUM_GRUNT_1, 1
.equ LOCALID_MUSEUM_GRUNT_2, 2
.equ LOCALID_MUSEUM_ARCHIE, 3

SlateportCity_OceanicMuseum_2F_OnTransition::
	setflag FLAG_HIDE_HOENN_MUSEUM_ARCHIE
	end

SlateportCity_OceanicMuseum_2F_EventScript_Grunt1::
	trainerbattle_single TRAINER_HOENN_GRUNT_MUSEUM_1, SlateportCity_OceanicMuseum_2F_Text_Grunt1Intro, SlateportCity_OceanicMuseum_2F_Text_Grunt1Defeat, SlateportCity_OceanicMuseum_2F_EventScript_AfterGrunt
	msgbox SlateportCity_OceanicMuseum_2F_Text_Grunt1Post, MSGBOX_AUTOCLOSE
	end

SlateportCity_OceanicMuseum_2F_EventScript_Grunt2::
	trainerbattle_single TRAINER_HOENN_GRUNT_MUSEUM_2, SlateportCity_OceanicMuseum_2F_Text_Grunt2Intro, SlateportCity_OceanicMuseum_2F_Text_Grunt2Defeat, SlateportCity_OceanicMuseum_2F_EventScript_AfterGrunt
	msgbox SlateportCity_OceanicMuseum_2F_Text_Grunt2Post, MSGBOX_AUTOCLOSE
	end

SlateportCity_OceanicMuseum_2F_EventScript_AfterGrunt::
	addvar VAR_HOENN_SCENE_MUSEUM, 1
	goto_if_lt VAR_HOENN_SCENE_MUSEUM, 2, EventScript_ReleaseEnd
	goto SlateportCity_OceanicMuseum_2F_EventScript_ArchieScene
	end

SlateportCity_OceanicMuseum_2F_EventScript_ArchieScene::
	clearflag FLAG_HIDE_HOENN_MUSEUM_ARCHIE
	addobject LOCALID_MUSEUM_ARCHIE
	playse SE_PIN
	applymovement LOCALID_MUSEUM_ARCHIE, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_MUSEUM_ARCHIE, SlateportCity_OceanicMuseum_2F_Movement_ArchieEnter
	waitmovement 0
	msgbox SlateportCity_OceanicMuseum_2F_Text_ArchieWarning
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_MUSEUM_ARCHIE
	removeobject LOCALID_MUSEUM_GRUNT_1
	removeobject LOCALID_MUSEUM_GRUNT_2
	setflag FLAG_HIDE_HOENN_MUSEUM_ARCHIE
	setflag FLAG_HIDE_HOENN_MUSEUM_GRUNTS
	setflag FLAG_HOENN_MUSEUM_DEFENDED
	setflag FLAG_HOENN_ARCHIE_WARNED
	setvar VAR_HOENN_SCENE_MUSEUM, 3
	setvar VAR_HOENN_STAGE1_PROGRESS, 2
	fadescreen FADE_FROM_BLACK
	msgbox SlateportCity_OceanicMuseum_2F_Text_MuseumQuiet
	release
	end

@ ARCHIE never battles here; he only wants a look at the survey and at you
SlateportCity_OceanicMuseum_2F_EventScript_Archie::
	lock
	faceplayer
	msgbox SlateportCity_OceanicMuseum_2F_Text_ArchieWarning
	release
	end

SlateportCity_OceanicMuseum_2F_Movement_ArchieEnter::
	walk_down
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	step_end
@ END PATCH
