SpaceFacility_CargoResearcher::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_CabinNoOrder
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, SpaceFacility_CargoAlready
 goto_if_unset FLAG_HOENN_SPACE_ENGINEERING_CLEARED, SpaceFacility_CargoLocked
 msgbox SpaceFacility_Text_CargoOffer, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, EventScript_ReleaseEnd
 closemessage
 playse SE_UNLOCK
 waitse
 applymovement 1, Common_Movement_ExclamationMark
 waitmovement 0
 delay 30
 setflag FLAG_HOENN_SPACE_CREW_RESCUED
 setflag FLAG_HOENN_SPACE_RECORDS_RECOVERED
 goto_if_ge VAR_HOENN_SPACE_MISSION_PHASE, 4, SpaceFacility_CargoPhaseReady
 setvar VAR_HOENN_SPACE_MISSION_PHASE, 4
SpaceFacility_CargoPhaseReady::
 call Space_PrepareJirachiFlag
 msgbox SpaceFacility_Text_CargoRescued
 release
 end
SpaceFacility_CargoLocked::
 msgbox SpaceFacility_Text_CargoLocked
 release
 end
SpaceFacility_CargoAlready::
 msgbox SpaceFacility_Text_CargoAlready
 release
 end
SpaceFacility_CargoClue::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 goto_if_set FLAG_HOENN_SPACE_ENGINEERING_CLEARED, SpaceFacility_CargoClueSafe
 msgbox SpaceFacility_Text_CargoClueActive
 releaseall
 end
SpaceFacility_CargoClueSafe::
 msgbox SpaceFacility_Text_CargoClue
 releaseall
 end
