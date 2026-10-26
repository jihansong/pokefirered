HoennSpacecraftEngineering_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	map_script MAP_SCRIPT_ON_LOAD, Space_EngineeringLoad
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
Space_SystemsCheck::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_CabinNoOrder
 goto_if_set FLAG_HOENN_SPACE_ENGINEERING_CLEARED, Space_SystemsPassed
 goto_if_set FLAG_HOENN_SPACE_CABIN_CLEARED, Space_SystemsOffer
 msgbox Space_Text_NeedFlightCheck
 release
 end
Space_SystemsOffer::
 msgbox Space_Text_SystemsCheck, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_Decline
 closemessage
 playse SE_PIN
 applymovement 1, Common_Movement_ExclamationMark
 waitmovement 0
 waitse
 trainerbattle_no_intro TRAINER_HOENN_SPACE_SYSTEMS_CHECK, Space_Text_SystemsDefeat
 setflag FLAG_HOENN_SPACE_ENGINEERING_CLEARED
 setflag FLAG_HOENN_SPACE_SYSTEMS_SECURED
 closemessage
 applymovement 1, Common_Movement_WalkInPlaceFasterUp
 waitmovement 0
 fadescreen FADE_TO_BLACK
 removeobject 1
 delay 16
 fadescreen FADE_FROM_BLACK
Space_SystemsPassed::
 setmetatile 12, 4, 531, TRUE
 special DrawWholeMapView
 goto_if_ge VAR_HOENN_SPACE_MISSION_PHASE, 3, Space_SystemsAlready
 setvar VAR_HOENN_SPACE_MISSION_PHASE, 3
Space_SystemsAlready::
 msgbox Space_Text_SystemsPassed
 release
 end
Space_EngineeringCrew::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_ENGINEERING_CLEARED, Space_EngineerSafe
 msgbox Space_Text_EngineeringCrew
 release
 end
Space_EngineerSafe::
 msgbox Space_Text_EngineerSafe
 release
 end
Space_EngineeringConsole::
 lockall
 goto_if_unset FLAG_HOENN_SPACE_ENGINEERING_CLEARED, Space_ConsoleLocked
 msgbox Space_Text_ConsoleReady
 releaseall
 end
Space_ConsoleLocked::
 msgbox Space_Text_ConsoleLocked
 releaseall
 end
Space_EngineeringLoad::
 goto_if_unset FLAG_HOENN_SPACE_SYSTEMS_SECURED, Space_MapLoadDone
 setmetatile 12, 4, 531, TRUE
Space_MapLoadDone::
 end
@ END PATCH
