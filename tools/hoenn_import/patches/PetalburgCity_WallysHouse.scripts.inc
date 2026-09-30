@ v0.11.0: WALLY's parents, before and after his catching demo (E5)
PetalburgCity_WallysHouse_EventScript_H0::
	lock
	faceplayer
	goto_if_ge VAR_HOENN_SCENE_WALLY, 2, PetalburgCity_WallysHouse_EventScript_DadAfter
	msgbox PetalburgCity_WallysHouse_Text_H0
	release
	end

PetalburgCity_WallysHouse_EventScript_DadAfter::
	msgbox PetalburgCity_WallysHouse_Text_DadAfter
	release
	end

PetalburgCity_WallysHouse_EventScript_H1::
	lock
	faceplayer
	goto_if_ge VAR_HOENN_SCENE_WALLY, 2, PetalburgCity_WallysHouse_EventScript_MomAfter
	msgbox PetalburgCity_WallysHouse_Text_H1
	release
	end

PetalburgCity_WallysHouse_EventScript_MomAfter::
	msgbox PetalburgCity_WallysHouse_Text_MomAfter
	release
	end
