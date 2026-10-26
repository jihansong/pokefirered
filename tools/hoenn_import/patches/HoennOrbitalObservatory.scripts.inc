@ No actor add/remove in ON_RESUME: field sprites do not exist yet.
Space_ObservatoryResume::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_MapCallbackEnd
 call Space_PrepareJirachiFlag
 end
Space_PrepareJirachiFlag::
 setflag FLAG_HIDE_HOENN_ORBITAL_JIRACHI
 goto_if_unset FLAG_HOENN_SPACE_CREW_RESCUED, EventScript_Return
 special HoennSpaceStory_CheckJirachiCaught
 goto_if_eq VAR_RESULT, TRUE, EventScript_Return
 clearflag FLAG_HIDE_HOENN_ORBITAL_JIRACHI
 return
Space_ObservatoryReturn::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_MapCallbackEnd
 call Space_PrepareJirachiFlag
 goto_if_set FLAG_HIDE_HOENN_ORBITAL_JIRACHI, Space_RemoveJirachi
 addobject 2
 end
Space_RemoveJirachi::
 removeobject 2
 end
Space_ObservatoryCrew::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, Space_ObserverRescued
 msgbox Space_Text_ObservatoryCrew
 release
 end
Space_ObserverRescued::
 msgbox Space_Text_ObserverRescued
 release
 end
Space_RecordsConsole::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_RecordsNoOrder
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, Space_RecordsAlready
 msgbox SpaceFacility_Text_NeedCargo
 releaseall
 end
Space_RecordsAlready::
 msgbox Space_Text_RecordsAlready
 releaseall
 end
Space_RecordsNoOrder::
 msgbox Space_Text_OldVisitor
 releaseall
 end
Space_ObservatoryLoad::
 goto_if_unset FLAG_HOENN_SPACE_RECORDS_RECOVERED, Space_MapLoadDone
 setmetatile 10, 8, 531, TRUE
 end
Space_JirachiEncounter::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 goto_if_unset FLAG_HOENN_SPACE_CREW_RESCUED, Space_ReleaseAllEnd
 special HoennSpaceStory_CheckJirachiCaught
 goto_if_eq VAR_RESULT, TRUE, Space_JirachiKnown
 specialvar VAR_RESULT, CalculatePlayerPartyCount
 goto_if_lt VAR_RESULT, 6, Space_JirachiOffer
 specialvar VAR_RESULT, IsThereRoomInAnyBoxForMorePokemon
 goto_if_eq VAR_RESULT, FALSE, Space_JirachiNoRoom
Space_JirachiOffer::
 msgbox Space_Text_JirachiOffer, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_ReleaseAllEnd
 closemessage
 special QuestLog_CutRecording
 playse SE_M_REFLECT
 waitse
 playmoncry SPECIES_JIRACHI, CRY_MODE_ENCOUNTER
 delay 40
 waitmoncry
 setvar VAR_LAST_TALKED, 2
 seteventmon SPECIES_JIRACHI, 70
 setflag FLAG_SYS_SPECIAL_WILD_BATTLE
 special StartLegendaryBattle
 waitstate
 clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
 specialvar VAR_RESULT, GetBattleOutcome
 goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Space_JirachiCaught
 msgbox Space_Text_JirachiRetry
 releaseall
 end
Space_JirachiCaught::
 setflag FLAG_HOENN_SPACE_JIRACHI_CAUGHT
 setflag FLAG_FOUGHT_JIRACHI
 setflag FLAG_HIDE_HOENN_ORBITAL_JIRACHI
 removeobject 2
 msgbox Space_Text_JirachiCaught
 releaseall
 end
Space_JirachiKnown::
 setflag FLAG_HIDE_HOENN_ORBITAL_JIRACHI
 removeobject 2
 msgbox Space_Text_JirachiKnown
 releaseall
 end
Space_JirachiNoRoom::
 msgbox Space_Text_JirachiNoRoom
 releaseall
 end
