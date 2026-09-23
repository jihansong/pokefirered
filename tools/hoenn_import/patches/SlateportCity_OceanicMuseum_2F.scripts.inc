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

@ Event 7: the current exhibit. The starter PIKACHU has an opinion about it.
SlateportCity_OceanicMuseum_2F_EventScript_CurrentExhibit::
	lock
	msgbox SlateportCity_OceanicMuseum_2F_Text_CurrentExhibit
	specialvar VAR_RESULT, GetStarterPikachuPartySlotForScript
	goto_if_eq VAR_RESULT, PARTY_SIZE, EventScript_ReleaseEnd
	setflag FLAG_HOENN_PIKACHU_MUSEUM_SEEN
	msgbox SlateportCity_OceanicMuseum_2F_Text_CurrentExhibitPikachu
	release
	end
