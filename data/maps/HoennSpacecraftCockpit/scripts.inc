HoennSpacecraftCockpit_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_CockpitPilot::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_Cockpit
 release
 end
@ END PATCH
