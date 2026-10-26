VerdanturfTown_WandasHouse_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, VerdanturfTown_WandasHouse_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, VerdanturfTown_WandasHouse_MountainResume
	map_script MAP_SCRIPT_ON_RETURN_TO_FIELD, VerdanturfTown_WandasHouse_MountainReturn
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
VerdanturfTown_WandasHouse_OnTransition::
	special HoennZ3_SetupObjects
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

VerdanturfTown_WandasHouse_MountainResume::
	special HoennMountain_SetupObjects
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

VerdanturfTown_WandasHouse_MountainReturn::
	special HoennMountain_RefreshActors
	special HoennMauvilleWally_GetPhase
	copyvar VAR_TEMP_0, VAR_RESULT
	end

@ Event 6: WANDA. Her cousin WALLY lives in PETALBURG (stage 3, v0.11.0); until
@ he comes to stay, all she can do is vouch for the player with the friendship
@ rater.
VerdanturfTown_WandasHouse_EventScript_Wanda::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_RUSTURF_OPEN, VerdanturfTown_WandasHouse_EventScript_WandaReunited
	goto_if_set FLAG_HOENN_MET_WANDA, VerdanturfTown_WandasHouse_EventScript_WandaDone
	goto_if_unset FLAG_HOENN_DEFEATED_MAUVILLE_GYM, VerdanturfTown_WandasHouse_EventScript_WandaBefore
	msgbox VerdanturfTown_WandasHouse_Text_WandaAfter
	msgbox VerdanturfTown_WandasHouse_Text_WandaIntro
	setflag FLAG_HOENN_MET_WANDA
	release
	end

VerdanturfTown_WandasHouse_EventScript_WandaBefore::
	msgbox VerdanturfTown_WandasHouse_Text_WandaBefore
	release
	end

VerdanturfTown_WandasHouse_EventScript_WandaDone::
	goto_if_ge VAR_HOENN_SCENE_WALLY, 2, VerdanturfTown_WandasHouse_EventScript_WandaWallyHere
	msgbox VerdanturfTown_WandasHouse_Text_WandaDone
	release
	end

@ v0.11.0: WALLY stays here after his catching demo in PETALBURG (E5)
VerdanturfTown_WandasHouse_EventScript_WandaWallyHere::
	call VerdanturfTown_WandasHouse_WallyChapter_WallyStatus
	release
	end

VerdanturfTown_WandasHouse_EventScript_Wally::
	goto_if_set FLAG_HOENN_MAUVILLE_WALLY_SCENE_DONE, VerdanturfTown_WandasHouse_WallyChapter_HomeWally
	msgbox VerdanturfTown_WandasHouse_Text_Wally, MSGBOX_NPC
	end

@ E10 completion preserves WALLY's visit and WANDA's friendship-rater referral.
VerdanturfTown_WandasHouse_EventScript_WandaReunited::
	msgbox VerdanturfTown_WandasHouse_Text_ReunionWanda
	goto_if_lt VAR_HOENN_SCENE_WALLY, 2, VerdanturfTown_WandasHouse_EventScript_ReunionReferral
	call VerdanturfTown_WandasHouse_WallyChapter_WallyStatus
VerdanturfTown_WandasHouse_EventScript_ReunionReferral::
	goto_if_set FLAG_HOENN_MET_WANDA, VerdanturfTown_WandasHouse_EventScript_ReunionDone
	goto_if_unset FLAG_HOENN_DEFEATED_MAUVILLE_GYM, VerdanturfTown_WandasHouse_EventScript_ReunionDone
	msgbox VerdanturfTown_WandasHouse_Text_WandaIntro
	setflag FLAG_HOENN_MET_WANDA
@ TY_HOENN_SHARED_HM_STORY_V1
VerdanturfTown_WandasHouse_EventScript_ReunionDone::
	goto_if_unset FLAG_HOENN_RUSTURF_OPEN, VerdanturfTown_WandasHouse_TYSharedHM_Done
	goto_if_set FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD, VerdanturfTown_WandasHouse_TYSharedHM_Done
	goto_if_set FLAG_GOT_HM04, VerdanturfTown_WandasHouse_TYSharedHM_Known
	checkitem ITEM_HM04
	goto_if_eq VAR_RESULT, TRUE, VerdanturfTown_WandasHouse_TYSharedHM_Known
	checkpcitem ITEM_HM04
	goto_if_eq VAR_RESULT, TRUE, VerdanturfTown_WandasHouse_TYSharedHM_Known
	msgbox VerdanturfTown_WandasHouse_TYSharedHM_FreshText
	checkitemspace ITEM_HM04
	goto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full
	giveitem ITEM_HM04
	goto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full
	setflag FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD
	msgbox VerdanturfTown_WandasHouse_TYSharedHM_FreshThanks
	release
	end

VerdanturfTown_WandasHouse_TYSharedHM_Known::
	msgbox VerdanturfTown_WandasHouse_TYSharedHM_KnownText
	checkitemspace ITEM_TM26
	goto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full
	giveitem ITEM_TM26
	goto_if_eq VAR_RESULT, FALSE, VerdanturfTown_WandasHouse_TYSharedHM_Full
	setflag FLAG_HOENN_GOT_WANDA_SHARED_HM_REWARD
	msgbox VerdanturfTown_WandasHouse_TYSharedHM_TechniqueText
	release
	end

VerdanturfTown_WandasHouse_TYSharedHM_Full::
	msgbox VerdanturfTown_WandasHouse_TYSharedHM_FullText
	release
	end

VerdanturfTown_WandasHouse_TYSharedHM_Done::
	release
	end

VerdanturfTown_WandasHouse_EventScript_WandaBoyfriend::
	msgbox VerdanturfTown_WandasHouse_Text_ReunionPartner, MSGBOX_NPC
	end

VerdanturfTown_WandasHouse_EventScript_H0::
	goto_if_set FLAG_HOENN_RUSTURF_OPEN, VerdanturfTown_WandasHouse_EventScript_ReunionMother
	msgbox VerdanturfTown_WandasHouse_Text_H0, MSGBOX_NPC
	end

VerdanturfTown_WandasHouse_EventScript_ReunionMother::
	msgbox VerdanturfTown_WandasHouse_Text_ReunionMother, MSGBOX_NPC
	end

VerdanturfTown_WandasHouse_WallyChapter_WallyStatus::
	goto_if_unset FLAG_HOENN_MAUVILLE_WALLY_CHAPTER_STARTED, VerdanturfTown_WandasHouse_WallyChapter_WallyHere
	goto_if_set FLAG_HOENN_MAUVILLE_WALLY_SCENE_DONE, VerdanturfTown_WandasHouse_WallyChapter_WallyHere
	msgbox VerdanturfTown_WandasHouse_WallyChapter_TextAway
	return
VerdanturfTown_WandasHouse_WallyChapter_WallyHere::
	msgbox VerdanturfTown_WandasHouse_Text_WandaWallyHere
	return
VerdanturfTown_WandasHouse_WallyChapter_HomeWally::
	msgbox VerdanturfTown_WandasHouse_WallyChapter_TextWally, MSGBOX_NPC
	end
VerdanturfTown_WandasHouse_WallyChapter_Uncle::
	msgbox VerdanturfTown_WandasHouse_WallyChapter_TextUncle, MSGBOX_NPC
	end
@ END PATCH
