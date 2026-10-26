SpaceFacility_NavigationOfficer::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_CabinNoOrder
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, SpaceFacility_NavigationDone
 goto_if_set FLAG_HOENN_SPACE_ENGINEERING_CLEARED, SpaceFacility_NavigationSafe
 playse SE_PC_ON
 waitse
 msgbox SpaceFacility_Text_Navigation
 release
 end
SpaceFacility_NavigationSafe::
 msgbox SpaceFacility_Text_NavigationSafe
 release
 end
SpaceFacility_NavigationDone::
 msgbox SpaceFacility_Text_NavigationDone
 release
 end
SpaceFacility_NavigationConsole::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 msgbox SpaceFacility_Text_Decks
 releaseall
 end
