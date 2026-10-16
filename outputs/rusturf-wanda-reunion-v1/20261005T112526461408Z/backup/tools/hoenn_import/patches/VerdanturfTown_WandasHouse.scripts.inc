@ Event 6: WANDA. Her cousin WALLY lives in PETALBURG (stage 3, v0.11.0); until
@ he comes to stay, all she can do is vouch for the player with the friendship
@ rater.
VerdanturfTown_WandasHouse_OnTransition::
	special HoennZ3_SetupObjects
	end

VerdanturfTown_WandasHouse_EventScript_Wanda::
	lock
	faceplayer
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
