@ Thunder Yellow Sootopolis Dive v1
SootopolisCity_NativeDiveWarp::
	setdivewarp MAP_UNDERWATER_SOOTOPOLIS_CITY, 9, 6
	end

@ Thunder Yellow Hoenn sea-sky chapter v1
SootopolisCity_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_SOOTOPOLIS_CITY
	goto_if_set FLAG_HOENN_BADGE08_GET, SootopolisCity_TY_Calm
	goto_if_unset FLAG_HOENN_SEAFLOOR_CLEARED, SootopolisCity_TY_Calm
	goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, SootopolisCity_TY_Calm
	setweather WEATHER_RAIN_THUNDERSTORM
	doweather
	end

SootopolisCity_TY_Calm::
	setweather WEATHER_SUNNY
	doweather
	end

SootopolisCity_EventScript_TY_Wallace::
	goto_if_set FLAG_HOENN_BADGE08_GET, SootopolisCity_TY_WallaceLegacy
	goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, SootopolisCity_TY_WallaceCalm
	goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, SootopolisCity_TY_WallaceStorm
	msgbox SootopolisCity_Text_TY_WallaceBefore, MSGBOX_NPC
	end

SootopolisCity_TY_WallaceStorm::
	msgbox SootopolisCity_Text_TY_WallaceStorm, MSGBOX_NPC
	end

SootopolisCity_TY_WallaceCalm::
	msgbox SootopolisCity_Text_TY_WallaceCalm, MSGBOX_NPC
	end

SootopolisCity_TY_WallaceLegacy::
	msgbox SootopolisCity_Text_TY_WallaceLegacy, MSGBOX_NPC
	end
