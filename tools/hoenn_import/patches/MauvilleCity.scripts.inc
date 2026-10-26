MauvilleCity_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_MAUVILLE_CITY
	special HoennMountain_SetupObjects
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MauvilleCity_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

MauvilleCity_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

@ The Z3 boundary: the desert road north is not part of this chapter.
MauvilleCity_EventScript_NorthNotice::
	msgbox MauvilleCity_Text_NorthNotice, MSGBOX_SIGN
	end

MauvilleCity_WallyChapter_Uncle::
	msgbox MauvilleCity_WallyChapter_TextUncle, MSGBOX_NPC
	end
MauvilleCity_WallyChapter_Wally::
	lockall
	goto_if_defeated TRAINER_HOENN_WALLY_MAUVILLE, MauvilleCity_WallyChapter_After
	applymovement 8, Common_Movement_FacePlayer
	waitmovement 0
	msgbox MauvilleCity_WallyChapter_TextIntro
	playse SE_PIN
	applymovement 8, Common_Movement_ExclamationMark
	waitmovement 0
	msgbox MauvilleCity_WallyChapter_TextAsk, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MauvilleCity_WallyChapter_Decline
	msgbox MauvilleCity_WallyChapter_TextReady
	trainerbattle_no_intro TRAINER_HOENN_WALLY_MAUVILLE, MauvilleCity_WallyChapter_TextDefeat
MauvilleCity_WallyChapter_After::
	msgbox MauvilleCity_WallyChapter_TextAfter
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	goto_if_eq VAR_0x8004, 7, MauvilleCity_WallyChapter_ExitEast
	applymovement 8, MauvilleCity_WallyChapter_ExitNorthWally
	applymovement 9, MauvilleCity_WallyChapter_ExitNorthUncle
	waitmovement 0
	goto MauvilleCity_WallyChapter_Leave
MauvilleCity_WallyChapter_ExitEast::
	applymovement 8, MauvilleCity_WallyChapter_ExitEastWally
	applymovement 9, MauvilleCity_WallyChapter_ExitEastUncle
	waitmovement 0
MauvilleCity_WallyChapter_Leave::
	applymovement 8, MauvilleCity_WallyChapter_WestWalk
	applymovement 9, MauvilleCity_WallyChapter_WestWalk
	waitmovement 0
	fadescreen FADE_TO_BLACK
	removeobject 8
	removeobject 9
	setflag FLAG_HOENN_MAUVILLE_WALLY_SCENE_DONE
	special HoennMountain_SetupObjects
	setvar VAR_TEMP_0, 2
	fadedefaultbgm
	fadescreen FADE_FROM_BLACK
	releaseall
	end
MauvilleCity_WallyChapter_Decline::
	msgbox MauvilleCity_WallyChapter_TextNo
	releaseall
	end

MauvilleCity_WallyChapter_ExitNorthWally::
	walk_left
	walk_left
	walk_down
	walk_down
	walk_left
	step_end

MauvilleCity_WallyChapter_ExitNorthUncle::
	delay_16
	walk_left
	walk_left
	walk_left
	walk_down
	walk_down
	step_end

MauvilleCity_WallyChapter_ExitEastWally::
	walk_down
	walk_down
	walk_left
	walk_left
	walk_left
	step_end

MauvilleCity_WallyChapter_ExitEastUncle::
	delay_16
	walk_left
	walk_down
	walk_down
	walk_left
	walk_left
	step_end

MauvilleCity_WallyChapter_WestWalk::
	walk_left
	walk_left
	walk_left
	walk_left
	step_end
