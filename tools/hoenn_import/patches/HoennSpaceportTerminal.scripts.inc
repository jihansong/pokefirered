@ ORBIT intrusion chapter. Original flight phase0..6 remains independent.
Space_MapTransition::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_MapCallbackEnd
 setvar VAR_TEMP_0, 0
 call Space_PrepareJirachiFlag
Space_MapCallbackEnd::
 end

Space_Guard::
 special HoennSpaceStory_GetPhase
 return

Space_ReleaseAllEnd::
 releaseall
 end
Space_FlightRejected::
 fadescreen FADE_FROM_BLACK
 releaseall
 end
Space_CenterHatchGuard::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 goto_if_set FLAG_HOENN_SPACE_CENTER_SECURED, Space_ReleaseAllEnd
 msgbox Space_Text_NotReady
 closemessage
 applymovement LOCALID_PLAYER, Space_Movement_HatchBack
 waitmovement 0
 releaseall
 end
Space_Movement_HatchBack::
 walk_down
 step_end

Space_TerminalClerk::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_CENTER_SECURED, Space_NotReady
 goto_if_set FLAG_HOENN_SPACE_INTRUSION_REPORTED, Space_ClerkRepeat
 goto_if_set FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_ClerkEnrolled
 msgbox Space_Text_Offer, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_Decline
 setflag FLAG_HOENN_SPACE_INTRUSION_STARTED
 setflag FLAG_HOENN_SPACE_MISSION_ENROLLED
 goto_if_ge VAR_HOENN_SPACE_MISSION_PHASE, 1, Space_ClerkEnrolled
 setvar VAR_HOENN_SPACE_MISSION_PHASE, 1
Space_ClerkEnrolled::
 msgbox Space_Text_Enrolled
 release
 end
Space_ClerkRepeat::
 msgbox Space_Text_Repeat
 release
 end
Space_NotReady::
 msgbox Space_Text_NotReady
 release
 end
Space_Decline::
 msgbox Space_Text_Decline
 release
 end
Space_TerminalSafety::
 msgbox Space_Text_Safety, MSGBOX_NPC
 end
Space_TerminalCrew::
 msgbox Space_Text_Crew, MSGBOX_NPC
 end

Space_ControlOffer::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_set FLAG_HOENN_SPACE_INTRUSION_REPORTED, Space_ControlReward
 goto_if_unset FLAG_HOENN_SPACE_CREW_RESCUED, Space_ControlInvite
 goto_if_lt VAR_HOENN_SPACE_MISSION_PHASE, 5, Space_ControlInvite
 setflag FLAG_HOENN_SPACE_INTRUSION_REPORTED
 setflag FLAG_HOENN_SPACE_MISSION_REPORTED
 setvar VAR_HOENN_SPACE_MISSION_PHASE, 6
 msgbox Space_Text_Report
Space_ControlReward::
 goto_if_set FLAG_HOENN_SPACE_GOT_ORBIT_REWARD, Space_ControlDone
 checkitemspace ITEM_STAR_PIECE, 3
 goto_if_eq VAR_RESULT, FALSE, Space_ControlRewardFull
 giveitem ITEM_STAR_PIECE, 3
 goto_if_eq VAR_RESULT, FALSE, Space_ControlRewardFull
 setflag FLAG_HOENN_SPACE_GOT_ORBIT_REWARD
 msgbox Space_Text_Reward
 release
 end
Space_ControlRewardFull::
 msgbox Space_Text_RewardFull
 release
 end
Space_ControlInvite::
 goto_if_set FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_ControlProgress
 msgbox Space_Text_Hatch
 release
 end
Space_ControlProgress::
 msgbox Space_Text_ControlProgress
 release
 end
Space_ControlDone::
 msgbox Space_Text_ReportAfter
 release
 end
