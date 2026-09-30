@ v0.11.0 E9: MR. BRINEY and PEEKO are home once PEEKO is back from RUSTURF
@ TUNNEL (FLAG_HIDE_HOENN_BRINEY, set up on entry)
Route104_MrBrineysHouse_OnTransition::
	special HoennZ3_SetupObjects
	end

Route104_MrBrineysHouse_EventScript_Briney::
	lock
	faceplayer
	msgbox Route104_MrBrineysHouse_Text_Briney
	goto_if_set FLAG_HOENN_GOT_MUDKIP_ON_BEACH, Route104_MrBrineysHouse_EventScript_BrineyMudkipGot
	msgbox Route104_MrBrineysHouse_Text_BrineyMudkipHint
	release
	end

Route104_MrBrineysHouse_EventScript_BrineyMudkipGot::
	msgbox Route104_MrBrineysHouse_Text_BrineyMudkipGot
	release
	end

Route104_MrBrineysHouse_EventScript_Peeko::
	lock
	faceplayer
	playmoncry SPECIES_WINGULL, CRY_MODE_NORMAL
	msgbox Route104_MrBrineysHouse_Text_Peeko
	waitmoncry
	release
	end
