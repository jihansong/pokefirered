@ Keep the original boarding bridge and existing flight specials.
Space_PadCaptain::
 lock
 faceplayer
 goto_if_unset FLAG_HOENN_SPACE_CREW_RESCUED, Space_PadCaptainBridge
 goto_if_lt VAR_HOENN_SPACE_MISSION_PHASE, 5, Space_PadCaptainBridge
 msgbox Space_Text_PadReturned
 release
 end
Space_PadCaptainBridge::
 msgbox Space_Text_Bridge
 release
 end
Space_PadSafety::
 msgbox Space_Text_PadSafety, MSGBOX_NPC
 end
Space_BoardingTrigger::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_BoardNotEnrolled
 msgbox Space_Text_Board, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_ReleaseAllEnd
 closemessage
 applymovement 1, Space_Movement_CaptainBoard
 waitmovement 0
 applymovement LOCALID_PLAYER, Common_Movement_WalkInPlaceFasterUp
 waitmovement 0
 playse SE_RS_DOOR
 waitse
 delay 30
 setvar VAR_0x8004, 0
 special QuestLog_CutRecording
 fadescreen FADE_TO_BLACK
 special HoennSpaceStory_PlayFlight
 goto_if_eq VAR_RESULT, 0, Space_FlightRejected
 waitstate
 end
Space_BoardNotEnrolled::
 msgbox Space_Text_NotEnrolled
 releaseall
 end
Space_Movement_CaptainBoard::
 walk_right
 walk_up
 walk_up
 face_up
 step_end
