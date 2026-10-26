HoennSpacecraftLounge_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_LoungeGuest::
 msgbox SpaceFacility_Text_LoungeGuest, MSGBOX_NPC
 end
@ END PATCH
