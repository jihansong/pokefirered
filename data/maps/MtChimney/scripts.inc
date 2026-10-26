MtChimney_MapScripts::
map_script MAP_SCRIPT_ON_TRANSITION, MtChimney_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, MtChimney_MountainResume
	map_script MAP_SCRIPT_ON_RETURN_TO_FIELD, MtChimney_MountainReturn
	.byte 0

MtChimney_EventScript_H1::
	msgbox MtChimney_Text_H1, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
MtChimney_OnTransition::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MtChimney_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MtChimney_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end


MtChimney_Mountain_Tabitha::
	trainerbattle_single TRAINER_HOENN_TABITHA_MT_CHIMNEY, MtChimney_Mountain_TextTabithaIntro, MtChimney_Mountain_TextTabithaDefeat
	msgbox MtChimney_Mountain_TextTabithaPost, MSGBOX_AUTOCLOSE
	end

MtChimney_Mountain_Grunt1::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_CHIMNEY_1, MtChimney_Mountain_TextGrunt1Intro, MtChimney_Mountain_TextGrunt1Defeat
	msgbox MtChimney_Mountain_TextGrunt1Post, MSGBOX_AUTOCLOSE
	end

MtChimney_Mountain_Grunt2::
	trainerbattle_single TRAINER_HOENN_GRUNT_MT_CHIMNEY_2, MtChimney_Mountain_TextGrunt2Intro, MtChimney_Mountain_TextGrunt2Defeat
	msgbox MtChimney_Mountain_TextGrunt2Post, MSGBOX_AUTOCLOSE
	end

MtChimney_Mountain_Maxie::
	lockall
	goto_if_defeated TRAINER_HOENN_MAXIE_MT_CHIMNEY, MtChimney_Mountain_AfterMaxie
	goto_if_defeated TRAINER_HOENN_TABITHA_MT_CHIMNEY, MtChimney_Mountain_BattleMaxie
	msgbox MtChimney_Mountain_TextNeedTabitha
	releaseall
	end

MtChimney_Mountain_BattleMaxie::
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	applymovement 1, Common_Movement_FacePlayer
	waitmovement 0
	playse SE_PIN
	applymovement 1, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox MtChimney_Mountain_TextMaxieIntro
	trainerbattle_no_intro TRAINER_HOENN_MAXIE_MT_CHIMNEY, MtChimney_Mountain_TextMaxieDefeat
MtChimney_Mountain_AfterMaxie::
	msgbox MtChimney_Mountain_TextMaxieAfter
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject 1
	removeobject 2
	removeobject 3
	removeobject 4
	removeobject 6
	removeobject 8
	removeobject 9
	removeobject 10
	removeobject 5
	setobjectxyperm 5, 10, 12
	addobject 5
	fadescreen FADE_FROM_BLACK
	getplayerxy VAR_0x8004, VAR_0x8005
	call_if_eq VAR_0x8005, 7, MtChimney_Mountain_ArchieNorth
	call_if_eq VAR_0x8005, 6, MtChimney_Mountain_ArchieEast
	msgbox MtChimney_Mountain_TextArchieAfter
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	call_if_eq VAR_0x8005, 7, MtChimney_Mountain_LeaveNorth
	call_if_eq VAR_0x8005, 6, MtChimney_Mountain_LeaveEast
	fadescreen FADE_TO_BLACK
	setflag FLAG_HOENN_MT_CHIMNEY_CLEARED
	removeobject 5
	removeobject 7
	special HoennMountain_SetupObjects
	setvar VAR_TEMP_0, 2
	fadedefaultbgm
	fadescreen FADE_FROM_BLACK
	releaseall
	end

MtChimney_Mountain_ArchieNorth::
	applymovement 5, MtChimney_Mountain_ArchieApproachNorth
	waitmovement 0
	return

MtChimney_Mountain_ArchieEast::
	applymovement 5, MtChimney_Mountain_ArchieApproachEast
	waitmovement 0
	return

MtChimney_Mountain_LeaveNorth::
	applymovement 5, MtChimney_Mountain_ArchieLeaveNorth
	waitmovement 0
	return

MtChimney_Mountain_LeaveEast::
	applymovement 5, MtChimney_Mountain_ArchieLeaveEast
	waitmovement 0
	return

MtChimney_EventScript_H0::
	lockall
	special HoennMountain_GetPhase
	goto_if_lt VAR_RESULT, 2, MtChimney_Mountain_Blocked
	goto_if_set FLAG_HOENN_METEORITE_RECOVERED, MtChimney_Mountain_Empty
	goto_if_set FLAG_HOENN_METEORITE_RETURNED, MtChimney_Mountain_Empty
	checkitem ITEM_METEORITE
	goto_if_eq VAR_RESULT, TRUE, MtChimney_Mountain_AlreadyHeld
	checkpcitem ITEM_METEORITE
	goto_if_eq VAR_RESULT, TRUE, MtChimney_Mountain_AlreadyStored
	msgbox MtChimney_Mountain_TextMachineAsk, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MtChimney_Mountain_Done
	giveitem ITEM_METEORITE
	goto_if_eq VAR_RESULT, FALSE, MtChimney_Mountain_Full
MtChimney_Mountain_AlreadyHeld::
	setflag FLAG_HOENN_METEORITE_RECOVERED
	msgbox MtChimney_Mountain_TextRecovered
	goto MtChimney_Mountain_Done
MtChimney_Mountain_AlreadyStored::
	setflag FLAG_HOENN_METEORITE_RECOVERED
	msgbox MtChimney_Mountain_TextStored
	goto MtChimney_Mountain_Done
MtChimney_Mountain_Blocked::
	msgbox MtChimney_Mountain_TextMachineBlocked
	goto MtChimney_Mountain_Done
MtChimney_Mountain_Empty::
	msgbox MtChimney_Mountain_TextMachineEmpty
	goto MtChimney_Mountain_Done
MtChimney_Mountain_Full::
	msgbox MtChimney_Mountain_TextFull
MtChimney_Mountain_Done::
	releaseall
	end
MtChimney_Mountain_ArchieApproachNorth::
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	face_up
	step_end
MtChimney_Mountain_ArchieApproachEast::
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_up
	walk_right
	face_right
	step_end
MtChimney_Mountain_ArchieLeaveNorth::
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

MtChimney_Mountain_ArchieLeaveEast::
	walk_left
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

MtChimney_Mountain_Archie::
	msgbox MtChimney_Mountain_TextArchieBusy, MSGBOX_NPC
	end

MtChimney_Mountain_BusyMagma::
	msgbox MtChimney_Mountain_TextBusy, MSGBOX_NPC
	end

MtChimney_Mountain_Dog1::
	msgbox MtChimney_Mountain_TextBusy, MSGBOX_NPC
	end

MtChimney_Mountain_Dog2::
	msgbox MtChimney_Mountain_TextBusy, MSGBOX_NPC
	end

MtChimney_Mountain_Dog3::
	msgbox MtChimney_Mountain_TextBusy, MSGBOX_NPC
	end

MtChimney_Mountain_Dog4::
	msgbox MtChimney_Mountain_TextBusy, MSGBOX_NPC
	end
@ END PATCH
