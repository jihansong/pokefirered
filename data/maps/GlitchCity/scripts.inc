GlitchCity_MapScripts::
	.byte 0

@ The Gen I Glitch City: if the SAFARI ZONE steps run out while the player
@ stands on the exit to the gate, they end up in a broken copy of FUCHSIA CITY
@ drawn with the wrong tileset. After some steps (TryStartGlitchCityStepScript)
@ everything snaps back to the gate. It only happens once.
GlitchCity_EventScript_Enter::
	setflag FLAG_VISITED_GLITCH_CITY
	special ExitSafariMode
	setvar VAR_MAP_SCENE_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE, 0
	closemessage
	playse SE_M_DETECT
	fadescreen FADE_TO_WHITE
	warpsilent MAP_GLITCH_CITY, 10, 6
	waitstate
	releaseall
	end

GlitchCity_EventScript_Return::
	lockall
	playse SE_M_REFLECT
	fadescreen FADE_TO_WHITE
	delay 20
	fadescreen FADE_FROM_WHITE
	waitse
	msgbox GlitchCity_Text_BackToNormal
	closemessage
	setvar VAR_MAP_SCENE_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE, 1
	warp MAP_FUCHSIA_CITY_SAFARI_ZONE_ENTRANCE, 4, 1
	waitstate
	releaseall
	end

GlitchCity_EventScript_OddFragment::
	finditem ITEM_ODD_FRAGMENT
	end
