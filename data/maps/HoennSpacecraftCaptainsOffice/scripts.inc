HoennSpacecraftCaptainsOffice_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_OfficeCaptain::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, SpaceFacility_OfficeSafe
 msgbox SpaceFacility_Text_CaptainOffice
 release
 end
SpaceFacility_OfficeSafe::
 msgbox SpaceFacility_Text_CaptainOfficeSafe
 release
 end
@ END PATCH
