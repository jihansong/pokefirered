@ Thunder Yellow Hoenn sea-sky chapter v1
SkyPillar_Top_EventScript_TY_Rayquaza::
	goto_if_questlog EventScript_ReleaseEnd
	goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, SkyPillar_Top_TY_Done
	goto_if_set FLAG_HOENN_BADGE08_GET, SkyPillar_Top_TY_Wake
	goto_if_unset FLAG_HOENN_SEAFLOOR_CLEARED, SkyPillar_Top_TY_Sleep
SkyPillar_Top_TY_Wake::
	lockall
	msgbox SkyPillar_Top_Text_TY_Wake, MSGBOX_DEFAULT
	applymovement 1, SkyPillar_Top_Movement_TY_Awake
	waitmovement 0
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_NORMAL
	waitmoncry
	applymovement 1, SkyPillar_Top_Movement_TY_Call
	waitmovement 0
	delay 30
	applymovement 1, SkyPillar_Top_Movement_TY_Rise
	waitmovement 0
	removeobject 1
	setflag FLAG_HOENN_RAYQUAZA_AWAKENED
	msgbox SkyPillar_Top_Text_TY_After, MSGBOX_DEFAULT
	releaseall
	end

SkyPillar_Top_TY_Sleep::
	msgbox SkyPillar_Top_Text_TY_Sleep, MSGBOX_NPC
	end

SkyPillar_Top_TY_Done::
	end

SkyPillar_Top_Movement_TY_Awake::
	walk_in_place_fast_left
	step_end

SkyPillar_Top_Movement_TY_Call::
	walk_in_place_left
	step_end

SkyPillar_Top_Movement_TY_Rise::
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	walk_fast_up
	step_end
