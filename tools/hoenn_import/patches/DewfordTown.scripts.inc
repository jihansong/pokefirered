@ v0.11.0: the island's world map flag as before, and MR. BRINEY's boat at the
@ dock when its last trip ended here (E9)
DewfordTown_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_DEWFORD_TOWN
	special HoennZ3_SetupObjects
	end

DewfordTown_OnFrame::
	map_script_2 VAR_HOENN_BRINEY_STATE, BRINEY_AT_DEWFORD | BRINEY_ARRIVING, DewfordTown_EventScript_BrineyArrived
	.2byte 0

DewfordTown_EventScript_BrineyArrived::
	setvar VAR_HOENN_BRINEY_STATE, BRINEY_AT_DEWFORD
	applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterLeft
	waitmovement 0
	goto Route104_EventScript_BrineyArrived
	end

DewfordTown_EventScript_H0::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_PEEKO_RESCUED, DewfordTown_EventScript_H0BrineyBack
	msgbox DewfordTown_Text_H0
	release
	end

DewfordTown_EventScript_H0BrineyBack::
	msgbox DewfordTown_Text_H0_BrineyBack
	release
	end
