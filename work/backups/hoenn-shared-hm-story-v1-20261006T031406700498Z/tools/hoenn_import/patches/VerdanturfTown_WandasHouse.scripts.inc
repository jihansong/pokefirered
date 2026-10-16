@ Event 6: WANDA. Her cousin WALLY lives in PETALBURG (stage 3, v0.11.0); until
@ he comes to stay, all she can do is vouch for the player with the friendship
@ rater.
VerdanturfTown_WandasHouse_OnTransition::
	special HoennZ3_SetupObjects
	end

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
	msgbox VerdanturfTown_WandasHouse_Text_WandaWallyHere
	release
	end

VerdanturfTown_WandasHouse_EventScript_Wally::
	msgbox VerdanturfTown_WandasHouse_Text_Wally, MSGBOX_NPC
	end

@ E10 completion preserves WALLY's visit and WANDA's friendship-rater referral.
VerdanturfTown_WandasHouse_EventScript_WandaReunited::
	msgbox VerdanturfTown_WandasHouse_Text_ReunionWanda
	goto_if_lt VAR_HOENN_SCENE_WALLY, 2, VerdanturfTown_WandasHouse_EventScript_ReunionReferral
	msgbox VerdanturfTown_WandasHouse_Text_WandaWallyHere
VerdanturfTown_WandasHouse_EventScript_ReunionReferral::
	goto_if_set FLAG_HOENN_MET_WANDA, VerdanturfTown_WandasHouse_EventScript_ReunionDone
	goto_if_unset FLAG_HOENN_DEFEATED_MAUVILLE_GYM, VerdanturfTown_WandasHouse_EventScript_ReunionDone
	msgbox VerdanturfTown_WandasHouse_Text_WandaIntro
	setflag FLAG_HOENN_MET_WANDA
VerdanturfTown_WandasHouse_EventScript_ReunionDone::
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
