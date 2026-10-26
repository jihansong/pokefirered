SpaceFacility_CockpitPilot::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_Cockpit
 release
 end
