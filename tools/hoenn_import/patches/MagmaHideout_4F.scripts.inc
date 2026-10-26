@ Original hideout awakening and battle; shared native screen effects.
MagmaHideout_4F_VS_GroudonSleeping::
	end
MagmaHideout_4F_VS_GroudonAwake::
	end
MagmaHideout_4F_VS_Maxie::
	lockall
	goto_if_set FLAG_HIDE_HOENN_MAGMA_HIDEOUT_RAID, MagmaHideout_4F_VS_End
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	goto_if_defeated TRAINER_HOENN_MAXIE_MAGMA_HIDEOUT, MagmaHideout_4F_VS_Won
	goto_if_set FLAG_HOENN_MAGMA_GROUDON_AWAKENED, MagmaHideout_4F_VS_Battle
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	msgbox MagmaHideout_4F_VS_Text_Awaken
	closemessage
	playse SE_ORB
	delay 40
	fadescreen FADE_TO_WHITE
	setflag FLAG_HOENN_MAGMA_GROUDON_AWAKENED
	removeobject 2
	clearflag FLAG_HIDE_HOENN_MAGMA_GROUDON_AWAKE
	addobject 3
	fadescreen FADE_FROM_WHITE
	playmoncry SPECIES_GROUDON, 0
	waitmoncry
	applymovement 3, MagmaHideout_4F_VS_Movement_GroudonApproach
	waitmovement 0
	setvar VAR_0x8004, 1
	setvar VAR_0x8005, 1
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 5
	special ShakeScreen
	waitstate
	applymovement 3, MagmaHideout_4F_VS_Movement_GroudonExit
	waitmovement 0
	setflag FLAG_HIDE_HOENN_MAGMA_GROUDON_AWAKE
	removeobject 3
	applymovement 4, MagmaHideout_4F_VS_Movement_MaxieLook
	waitmovement 0
	msgbox MagmaHideout_4F_VS_Text_GroudonFled
	closemessage
MagmaHideout_4F_VS_Battle::
	msgbox MagmaHideout_4F_VS_Text_MaxieIntro
	trainerbattle_no_intro TRAINER_HOENN_MAXIE_MAGMA_HIDEOUT, MagmaHideout_4F_VS_Text_MaxieDefeat
MagmaHideout_4F_VS_Won::
	setflag FLAG_HOENN_MAGMA_HIDEOUT_CLEARED
	setflag FLAG_HIDE_HOENN_MAGMA_HIDEOUT_RAID
	msgbox MagmaHideout_4F_VS_Text_MaxieAfter
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject 4
	removeobject 5
	removeobject 6
	removeobject 7
	removeobject 8
	fadedefaultbgm
	fadescreen FADE_FROM_BLACK
	msgbox MagmaHideout_4F_VS_Text_SternLead
MagmaHideout_4F_VS_End::
	releaseall
	end

MagmaHideout_4F_VS_Movement_GroudonApproach:
	delay_16
	walk_slow_down
	delay_16
	walk_slow_down
	step_end

MagmaHideout_4F_VS_Movement_GroudonExit:
	slide_up
	slide_up
	step_end

MagmaHideout_4F_VS_Movement_MaxieLook:
	face_left
	delay_16
	face_right
	delay_16
	face_up
	step_end

MagmaHideout_4F_VS_Tabitha::
	trainerbattle_single TRAINER_HOENN_TABITHA_MAGMA_HIDEOUT, MagmaHideout_4F_VS_Text_TabithaIntro, MagmaHideout_4F_VS_Text_TabithaDefeat, MagmaHideout_4F_VS_TabithaAfter
	goto MagmaHideout_4F_VS_TabithaAfter
MagmaHideout_4F_VS_TabithaAfter::
	msgbox MagmaHideout_4F_VS_Text_TabithaAfter
	release
	end

MagmaHideout_4F_VS_Grunt11::
	trainerbattle_single TRAINER_HOENN_GRUNT_MAGMA_HIDEOUT_11, MagmaHideout_4F_VS_Text_Grunt11Intro, MagmaHideout_4F_VS_Text_Grunt11Defeat, MagmaHideout_4F_VS_Grunt11After
	goto MagmaHideout_4F_VS_Grunt11After
MagmaHideout_4F_VS_Grunt11After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MagmaHideout_4F_VS_Text_Grunt11After
	release
	end

MagmaHideout_4F_VS_Grunt12::
	trainerbattle_single TRAINER_HOENN_GRUNT_MAGMA_HIDEOUT_12, MagmaHideout_4F_VS_Text_Grunt12Intro, MagmaHideout_4F_VS_Text_Grunt12Defeat, MagmaHideout_4F_VS_Grunt12After
	goto MagmaHideout_4F_VS_Grunt12After
MagmaHideout_4F_VS_Grunt12After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MagmaHideout_4F_VS_Text_Grunt12After
	release
	end

MagmaHideout_4F_VS_Grunt13::
	trainerbattle_single TRAINER_HOENN_GRUNT_MAGMA_HIDEOUT_13, MagmaHideout_4F_VS_Text_Grunt13Intro, MagmaHideout_4F_VS_Text_Grunt13Defeat, MagmaHideout_4F_VS_Grunt13After
	goto MagmaHideout_4F_VS_Grunt13After
MagmaHideout_4F_VS_Grunt13After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MagmaHideout_4F_VS_Text_Grunt13After
	release
	end

MagmaHideout_4F_VS_OnTransition::
	special HoennVillain_SetupObjects
	end
