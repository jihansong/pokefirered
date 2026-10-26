HoennSpacecraftCrewQuarters_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_CrewSleeper::
 msgbox SpaceFacility_Text_CrewQuarters, MSGBOX_NPC
 end
@ END PATCH
