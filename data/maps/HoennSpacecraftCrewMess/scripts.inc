HoennSpacecraftCrewMess_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_Cook::
 msgbox SpaceFacility_Text_CrewMess, MSGBOX_NPC
 end
@ END PATCH
