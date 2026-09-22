SilverMountain_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SilverMountain_1F_OnTransition
	.byte 0

@ Thunder Yellow v0.6.0: the snowbound mountain past SEVAULT CANYON. A blizzard
@ turns back anyone who isn't ready: the player needs the HALL OF FAME and either
@ every KANTO POKéMON caught or the INDIGO PLATEAU tournament won.
SilverMountain_1F_OnTransition::
	special SilverMountain_SetBlizzardGate
	end

SilverMountain_1F_EventScript_Blizzard::
	lockall
	playse SE_M_GUST
	msgbox SilverMountain_1F_Text_Blizzard
	closemessage
	warp MAP_SEVEN_ISLAND_SEVAULT_CANYON, 10, 4
	waitstate
	releaseall
	end
