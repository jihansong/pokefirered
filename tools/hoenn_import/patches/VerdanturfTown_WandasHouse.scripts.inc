@ Event 6: WANDA. Her cousin is on the far side of RUSTURF TUNNEL (stage 3),
@ so all she can do here is vouch for the player with the friendship rater.
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
	msgbox VerdanturfTown_WandasHouse_Text_WandaDone
	release
	end
