@ Original Emerald orb-theft staging, with the existing research chapter.

MtPyre_Summit_VS_Trigger0::
	lockall
	setvar VAR_0x8008, 0
	goto MtPyre_Summit_VS_Theft

MtPyre_Summit_VS_Trigger1::
	lockall
	setvar VAR_0x8008, 1
	goto MtPyre_Summit_VS_Theft

MtPyre_Summit_VS_Trigger2::
	lockall
	setvar VAR_0x8008, 2
	goto MtPyre_Summit_VS_Theft

MtPyre_Summit_VS_Archie::
	end

MtPyre_Summit_VS_Theft::
	goto_if_set FLAG_HIDE_HOENN_MT_PYRE_AQUA, MtPyre_Summit_VS_End
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	call_if_eq VAR_0x8008, 0, MtPyre_Summit_VS_FaceArchieLeft
	call_if_eq VAR_0x8008, 1, MtPyre_Summit_VS_FaceArchieMiddle
	call_if_eq VAR_0x8008, 2, MtPyre_Summit_VS_FaceArchieRight
	msgbox MtPyre_Summit_VS_Text_Archie
	closemessage
	fadescreen FADE_TO_BLACK
	setflag FLAG_HOENN_MT_PYRE_ORBS_STOLEN
	setflag FLAG_HIDE_HOENN_MT_PYRE_AQUA
	setvar VAR_TEMP_8, 1
	removeobject 3
	removeobject 4
	removeobject 5
	removeobject 6
	removeobject 7
	fadedefaultbgm
	fadescreen FADE_FROM_BLACK
	call_if_eq VAR_0x8008, 0, MtPyre_Summit_VS_ElderLeft
	call_if_eq VAR_0x8008, 1, MtPyre_Summit_VS_ElderMiddle
	call_if_eq VAR_0x8008, 2, MtPyre_Summit_VS_ElderRight
	msgbox MtPyre_Summit_VS_Text_ElderTheft
	goto MtPyre_Summit_VS_GiveEmblem

MtPyre_Summit_VS_ElderLeft::
	applymovement 2, MtPyre_Summit_VS_Movement_ElderLeft
	waitmovement 0
	return
MtPyre_Summit_VS_ElderMiddle::
	applymovement 2, MtPyre_Summit_VS_Movement_ElderMiddle
	waitmovement 0
	return
MtPyre_Summit_VS_ElderRight::
	applymovement 2, MtPyre_Summit_VS_Movement_ElderRight
	waitmovement 0
	return

MtPyre_Summit_EventScript_H1::
	lock
	faceplayer
	goto_if_unset FLAG_HOENN_MT_PYRE_ORBS_STOLEN, MtPyre_Summit_VS_ElderBefore
MtPyre_Summit_VS_GiveEmblem::
	goto_if_set FLAG_HOENN_GOT_MAGMA_EMBLEM, MtPyre_Summit_VS_ElderAfter
	checkitem ITEM_MAGMA_EMBLEM
	goto_if_eq VAR_RESULT, TRUE, MtPyre_Summit_VS_EmblemHeld
	checkpcitem ITEM_MAGMA_EMBLEM
	goto_if_eq VAR_RESULT, TRUE, MtPyre_Summit_VS_EmblemHeld
	msgbox MtPyre_Summit_VS_Text_EmblemOffer
	giveitem ITEM_MAGMA_EMBLEM
	goto_if_eq VAR_RESULT, FALSE, MtPyre_Summit_VS_EmblemFull
MtPyre_Summit_VS_EmblemHeld::
	setflag FLAG_HOENN_GOT_MAGMA_EMBLEM
MtPyre_Summit_VS_ElderAfter::
	msgbox MtPyre_Summit_VS_Text_EmblemDirections
	releaseall
	end
MtPyre_Summit_VS_EmblemFull::
	msgbox MtPyre_Summit_VS_Text_EmblemFull
	releaseall
	end
MtPyre_Summit_VS_ElderBefore::
	msgbox MtPyre_Summit_Text_H1
	release
	end
MtPyre_Summit_VS_End::
	releaseall
	end

MtPyre_Summit_VS_Movement_ElderLeft:
	walk_down
	walk_down
	face_left
	step_end

MtPyre_Summit_VS_Movement_ElderRight:
	walk_down
	walk_down
	face_right
	step_end

MtPyre_Summit_VS_Movement_ElderMiddle:
	walk_down
	step_end

MtPyre_Summit_VS_Grunt1::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_PYRE_1, MtPyre_Summit_VS_Text_Grunt1Intro, MtPyre_Summit_VS_Text_Grunt1Defeat, MtPyre_Summit_VS_Grunt1After
	goto MtPyre_Summit_VS_Grunt1After
MtPyre_Summit_VS_Grunt1After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MtPyre_Summit_VS_Text_Grunt1After
	release
	end

MtPyre_Summit_VS_Grunt2::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_PYRE_2, MtPyre_Summit_VS_Text_Grunt2Intro, MtPyre_Summit_VS_Text_Grunt2Defeat, MtPyre_Summit_VS_Grunt2After
	goto MtPyre_Summit_VS_Grunt2After
MtPyre_Summit_VS_Grunt2After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MtPyre_Summit_VS_Text_Grunt2After
	release
	end

MtPyre_Summit_VS_Grunt3::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_PYRE_3, MtPyre_Summit_VS_Text_Grunt3Intro, MtPyre_Summit_VS_Text_Grunt3Defeat, MtPyre_Summit_VS_Grunt3After
	goto MtPyre_Summit_VS_Grunt3After
MtPyre_Summit_VS_Grunt3After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MtPyre_Summit_VS_Text_Grunt3After
	release
	end

MtPyre_Summit_VS_Grunt4::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_PYRE_4, MtPyre_Summit_VS_Text_Grunt4Intro, MtPyre_Summit_VS_Text_Grunt4Defeat, MtPyre_Summit_VS_Grunt4After
	goto MtPyre_Summit_VS_Grunt4After
MtPyre_Summit_VS_Grunt4After::
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox MtPyre_Summit_VS_Text_Grunt4After
	release
	end


MtPyre_Summit_VS_FaceArchieLeft::
	applymovement 3, MtPyre_Summit_VS_Movement_ArchieLeft
	waitmovement 0
	return
MtPyre_Summit_VS_FaceArchieMiddle::
	turnobject 3, DIR_SOUTH
	return
MtPyre_Summit_VS_FaceArchieRight::
	applymovement 3, MtPyre_Summit_VS_Movement_ArchieRight
	waitmovement 0
	return
MtPyre_Summit_VS_Movement_ArchieLeft:
	walk_left
	face_down
	step_end
MtPyre_Summit_VS_Movement_ArchieRight:
	walk_right
	face_down
	step_end

MtPyre_Summit_VS_OnTransition::
	special HoennVillain_SetupObjects
	end
