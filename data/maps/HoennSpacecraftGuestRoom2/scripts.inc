HoennSpacecraftGuestRoom2_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_Guest2::
 msgbox SpaceFacility_Text_Guest2, MSGBOX_NPC
 end
@ END PATCH
