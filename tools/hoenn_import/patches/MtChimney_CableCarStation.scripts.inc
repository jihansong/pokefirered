MtChimney_CableCarStation_OnTransition::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MtChimney_CableCarStation_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MtChimney_CableCarStation_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMountain_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

@ Return through the same existing attendant and lower station.
MtChimney_CableCarStation_EventScript_H0::
	goto_if_questlog EventScript_ReleaseEnd
	lock
	faceplayer
	msgbox MtChimney_CableCarStation_Text_H0, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MtChimney_CableCarStation_TY_Declined
	closemessage
	getplayerxy VAR_0x8005, VAR_0x8006
	goto_if_ne VAR_0x8005, 6, MtChimney_CableCarStation_TY_Declined
	goto_if_ne VAR_0x8006, 7, MtChimney_CableCarStation_TY_Declined
	applymovement 1, MtChimney_CableCarStation_Cable_Lead
	applymovement LOCALID_PLAYER, MtChimney_CableCarStation_Cable_Board
	waitmovement 0
	setvar VAR_0x8004, 1
	specialvar VAR_RESULT, HoennCableCarRide
	goto_if_eq VAR_RESULT, FALSE, MtChimney_CableCarStation_Cable_Abort
	waitstate
	end

MtChimney_CableCarStation_TY_Declined::
	release
	end

MtChimney_CableCarStation_Mountain_WaitForReport::
	lockall
	msgbox MtChimney_CableCarStation_Mountain_TextWait
	closemessage
	applymovement LOCALID_PLAYER, MtChimney_CableCarStation_Mountain_StepBack
	waitmovement 0
	releaseall
	end
MtChimney_CableCarStation_Mountain_StepBack::
	walk_up
	step_end

MtChimney_CableCarStation_Cable_Abort::
	applymovement LOCALID_PLAYER, MtChimney_CableCarStation_Cable_Exit
	applymovement 1, MtChimney_CableCarStation_Cable_Follow
	waitmovement 0
	releaseall
	end
MtChimney_CableCarStation_Cable_Lead:
	walk_up
	walk_left
	walk_in_place_faster_right
	step_end
MtChimney_CableCarStation_Cable_Board:
	walk_up
	walk_up
	delay_16
	step_end
MtChimney_CableCarStation_Cable_Exit:
	walk_down
	walk_down
	delay_16
	step_end
MtChimney_CableCarStation_Cable_Follow:
	delay_16
	walk_right
	walk_down
	step_end
