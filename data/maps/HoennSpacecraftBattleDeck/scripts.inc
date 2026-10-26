HoennSpacecraftBattleDeck_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
Space_BattleDeckOrbit::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_CabinNoOrder
 goto_if_set FLAG_HOENN_SPACE_CABIN_CLEARED, SpaceFacility_ArenaCleared
 msgbox Space_Text_FlightCheck, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_Decline
 closemessage
 playse SE_PIN
 applymovement 1, Common_Movement_ExclamationMark
 waitmovement 0
 waitse
 trainerbattle_no_intro TRAINER_HOENN_SPACE_FLIGHT_CHECK, Space_Text_FlightDefeat
 setflag FLAG_HOENN_SPACE_CABIN_CLEARED
 closemessage
 applymovement 1, Common_Movement_WalkInPlaceFasterUp
 waitmovement 0
 fadescreen FADE_TO_BLACK
 removeobject 1
 delay 16
 fadescreen FADE_FROM_BLACK
SpaceFacility_ArenaCleared::
 msgbox Space_Text_FlightPassed
 release
 end
SpaceFacility_ArenaSpectator::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_set FLAG_HOENN_SPACE_CABIN_CLEARED, SpaceFacility_ArenaPeace
 msgbox SpaceFacility_Text_ArenaSpectator
 release
 end
SpaceFacility_ArenaPeace::
 msgbox SpaceFacility_Text_ArenaPeace
 release
 end
@ END PATCH
