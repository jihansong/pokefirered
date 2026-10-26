MeteorFalls_1F_1R_MapScripts::
map_script MAP_SCRIPT_ON_TRANSITION, MeteorFalls_1F_1R_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, MeteorFalls_1F_1R_MountainResume
	map_script MAP_SCRIPT_ON_RETURN_TO_FIELD, MeteorFalls_1F_1R_MountainReturn
	.byte 0

MeteorFalls_1F_1R_EventScript_HItem83::
	finditem ITEM_TM23_IRON_TAIL
	end

MeteorFalls_1F_1R_EventScript_HItem84::
	finditem ITEM_MOON_STONE
	end

MeteorFalls_1F_1R_EventScript_HItem85::
	finditem ITEM_FULL_HEAL
	end

MeteorFalls_1F_1R_EventScript_HItem86::
	finditem ITEM_PP_UP
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
MeteorFalls_1F_1R_OnTransition::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MeteorFalls_1F_1R_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MeteorFalls_1F_1R_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end


MeteorFalls_1F_1R_Mountain_Theft::
	lockall
	setflag FLAG_HOENN_MOUNTAIN_CHAPTER_STARTED
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	applymovement LOCALID_PLAYER, Common_Movement_FaceDown
	waitmovement 0
	delay 24
	msgbox MeteorFalls_1F_1R_Mountain_TextStolen
	closemessage
	applymovement 5, Common_Movement_ExclamationMark
	waitmovement 0
	playse SE_PIN
	msgbox MeteorFalls_1F_1R_Mountain_TextSpotted
	closemessage
	applymovement 5, MeteorFalls_1F_1R_Mountain_GruntApproach
	waitmovement 0
	msgbox MeteorFalls_1F_1R_Mountain_TextHalt
	closemessage
	clearflag FLAG_HIDE_HOENN_METEOR_AQUA
	addobject 7
	addobject 8
	addobject 9
	applymovement 7, MeteorFalls_1F_1R_Mountain_ArchieArrive
	applymovement 8, MeteorFalls_1F_1R_Mountain_AquaArrive1
	applymovement 9, MeteorFalls_1F_1R_Mountain_AquaArrive2
	waitmovement 0
	msgbox MeteorFalls_1F_1R_Mountain_TextEscape
	closemessage
	applymovement LOCALID_PLAYER, MeteorFalls_1F_1R_Mountain_PlayerAside
	waitmovement 0
	applymovement 5, MeteorFalls_1F_1R_Mountain_GruntExit1
	applymovement 6, MeteorFalls_1F_1R_Mountain_GruntExit2
	waitmovement 0
	removeobject 5
	removeobject 6
	applymovement 7, MeteorFalls_1F_1R_Mountain_ArchieApproach
	waitmovement 0
	msgbox MeteorFalls_1F_1R_Mountain_TextWarning
	closemessage
	applymovement 8, MeteorFalls_1F_1R_Mountain_AquaApproach1
	applymovement 9, MeteorFalls_1F_1R_Mountain_AquaApproach2
	waitmovement 0
	applymovement 7, MeteorFalls_1F_1R_Mountain_ArchieExit
	applymovement 8, MeteorFalls_1F_1R_Mountain_AquaExit1
	applymovement 9, MeteorFalls_1F_1R_Mountain_AquaExit2
	waitmovement 0
	fadescreen FADE_TO_BLACK
	removeobject 7
	removeobject 8
	removeobject 9
	setflag FLAG_HOENN_METEOR_FALLS_SCENE_DONE
	special HoennMountain_SetupObjects
	setvar VAR_TEMP_0, 1
	fadedefaultbgm
	fadescreen FADE_FROM_BLACK
	msgbox MeteorFalls_1F_1R_Mountain_TextCozmo
	releaseall
	end

MeteorFalls_1F_1R_Mountain_Magma1::
	msgbox MeteorFalls_1F_1R_Mountain_TextWait, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_Magma2::
	msgbox MeteorFalls_1F_1R_Mountain_TextWait, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_Archie::
	msgbox MeteorFalls_1F_1R_Mountain_TextWait, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_Aqua1::
	msgbox MeteorFalls_1F_1R_Mountain_TextWait, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_Aqua2::
	msgbox MeteorFalls_1F_1R_Mountain_TextWait, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_Cozmo::
	msgbox MeteorFalls_1F_1R_Mountain_TextQuiet, MSGBOX_NPC
	end

MeteorFalls_1F_1R_Mountain_GruntApproach::
	walk_right
	walk_right
	face_up
	step_end

MeteorFalls_1F_1R_Mountain_ArchieArrive::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

MeteorFalls_1F_1R_Mountain_AquaArrive1::
	delay_16
	delay_16
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

MeteorFalls_1F_1R_Mountain_AquaArrive2::
	delay_16
	delay_16
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

MeteorFalls_1F_1R_Mountain_PlayerAside::
	walk_left
	face_right
	step_end

MeteorFalls_1F_1R_Mountain_GruntExit1::
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

MeteorFalls_1F_1R_Mountain_GruntExit2::
	delay_16
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	walk_fast_right
	step_end

MeteorFalls_1F_1R_Mountain_ArchieApproach::
	walk_right
	walk_right
	walk_up
	walk_up
	face_left
	step_end

MeteorFalls_1F_1R_Mountain_AquaApproach1::
	walk_right
	walk_right
	walk_right
	face_up
	step_end

MeteorFalls_1F_1R_Mountain_AquaApproach2::
	walk_right
	walk_right
	walk_right
	face_up
	step_end

MeteorFalls_1F_1R_Mountain_ArchieExit::
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

MeteorFalls_1F_1R_Mountain_AquaExit1::
	delay_16
	walk_up
	walk_up
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

MeteorFalls_1F_1R_Mountain_AquaExit2::
	delay_16
	delay_16
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end
@ END PATCH
