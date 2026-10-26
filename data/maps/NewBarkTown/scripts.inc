NewBarkTown_MapScripts::
    map_script MAP_SCRIPT_ON_LOAD, NewBarkTown_TheftSetup
    map_script MAP_SCRIPT_ON_TRANSITION, NewBarkTown_TheftSetup
    map_script MAP_SCRIPT_ON_RESUME, NewBarkTown_TheftResume
    .byte 0

NewBarkTown_Resident::
    lock
    faceplayer
    msgbox NewBarkTown_Hns_Text_ElmResearch, MSGBOX_DEFAULT
    msgbox NewBarkTown_Text_Resident, MSGBOX_DEFAULT
    release
    end

NewBarkTown_Sign::
	msgbox NewBarkTown_Text_Sign, MSGBOX_NPC
	end


NewBarkTown_TheftSetup::
    call NewBarkTown_UpdateWindowSilverFlag
    end
NewBarkTown_TheftResume::
    call NewBarkTown_UpdateWindowSilverFlag
    goto_if_set FLAG_HIDE_JOHTO_WINDOW_SILVER, NewBarkTown_RemoveWindowSilver
    addobject LOCALID_NEWBARKTOWN_WINDOWSILVER
    end
NewBarkTown_RemoveWindowSilver::
    removeobject LOCALID_NEWBARKTOWN_WINDOWSILVER
    end
NewBarkTown_UpdateWindowSilverFlag::
    setflag FLAG_HIDE_JOHTO_WINDOW_SILVER
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, NewBarkTown_WindowFlagDone
    goto_if_set FLAG_JOHTO_LAB_THEFT_NOTIFIED, NewBarkTown_WindowFlagDone
    goto_if_set FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_WindowFlagDone
    clearflag FLAG_HIDE_JOHTO_WINDOW_SILVER
NewBarkTown_WindowFlagDone::
    return
NewBarkTown_WindowSilver::
    lockall
    faceplayer
    playse SE_PIN
    applymovement LOCALID_NEWBARKTOWN_WINDOWSILVER, Common_Movement_ExclamationMark
    waitmovement 0
    msgbox NewBarkTown_Text_WindowSilver, MSGBOX_DEFAULT
    getplayerxy VAR_0x8004, VAR_0x8005
    goto_if_ne VAR_0x8004, 14, NewBarkTown_WindowSilverFace
    goto_if_ne VAR_0x8005, 10, NewBarkTown_WindowSilverFace
    applymovement OBJ_EVENT_ID_PLAYER, NewBarkTown_WindowSilverPush
    waitmovement 0
NewBarkTown_WindowSilverFace::
    applymovement LOCALID_NEWBARKTOWN_WINDOWSILVER, NewBarkTown_WindowSilverFaceLeft
    waitmovement 0
    releaseall
    end
NewBarkTown_WindowSilverPush::
    walk_down
    step_end
NewBarkTown_WindowSilverFaceLeft::
    face_left
    step_end
