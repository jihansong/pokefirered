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
	lock
	faceplayer
	msgbox SootopolisCity_Text_TY_WallaceCalm, MSGBOX_DEFAULT
	goto SootopolisCity_TY_WaterfallReward

SootopolisCity_TY_WallaceLegacy::
	lock
	faceplayer
	msgbox SootopolisCity_Text_TY_WallaceLegacy, MSGBOX_DEFAULT
	goto SootopolisCity_TY_WaterfallReward

@ Thunder Yellow Waterfall league bridge v1
SootopolisCity_TY_WaterfallReward::
	goto_if_set FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD, SootopolisCity_TY_WaterfallDirections
	goto_if_set FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07, SootopolisCity_TY_WaterfallAlternate
	checkitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, TRUE, SootopolisCity_TY_WaterfallAlternate
	checkpcitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, TRUE, SootopolisCity_TY_WaterfallAlternate
	msgbox SootopolisCity_Text_TY_WaterfallFirst
	checkitemspace ITEM_HM07, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	giveitem ITEM_HM07, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	setflag FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD
	goto SootopolisCity_TY_WaterfallDirections

SootopolisCity_TY_WaterfallAlternate::
	msgbox SootopolisCity_Text_TY_WaterfallAlternate
	checkitemspace ITEM_TM26, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	giveitem ITEM_TM26, 1
	goto_if_eq VAR_RESULT, FALSE, SootopolisCity_TY_WaterfallFull
	setflag FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD

SootopolisCity_TY_WaterfallDirections::
	msgbox SootopolisCity_Text_TY_WaterfallDirections
	release
	end

SootopolisCity_TY_WaterfallFull::
	msgbox SootopolisCity_Text_TY_WaterfallFull
	release
	end
