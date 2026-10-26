NewBarkTown_ElmsLab_MapScripts::
    map_script MAP_SCRIPT_ON_LOAD, NewBarkTown_ElmsLab_TheftSetup
    map_script MAP_SCRIPT_ON_TRANSITION, NewBarkTown_ElmsLab_TheftTransition
    map_script MAP_SCRIPT_ON_RESUME, NewBarkTown_ElmsLab_TheftResume
    map_script MAP_SCRIPT_ON_FRAME_TABLE, NewBarkTown_ElmsLab_TheftFrameTable
    .byte 0

@ Existing shared partner receipts remain independent of the theft episode.
NewBarkTown_ElmsLab_Researcher::
    lock
    faceplayer
    call_if_unset FLAG_JOHTO_MET_LAB_ASSISTANT, NewBarkTown_ElmsLab_Hns_AideBusy
    setflag FLAG_JOHTO_MET_LAB_ASSISTANT
    call NewBarkTown_ElmsLab_ResearchFollowup
    goto_if_unset FLAG_GOT_CYNDAQUIL_FROM_AIDE, NewBarkTown_ElmsLab_OfferCyndaquil
    goto_if_unset FLAG_GOT_CHIKORITA_FROM_AIDE, NewBarkTown_ElmsLab_OfferChikorita
    goto_if_unset FLAG_GOT_TOTODILE_FROM_AIDE, NewBarkTown_ElmsLab_OfferTotodile
    goto NewBarkTown_ElmsLab_AlreadyReceived

NewBarkTown_ElmsLab_OfferCyndaquil::
    msgbox NewBarkTown_ElmsLab_Text_ResearchRequest
    setvar VAR_TEMP_1, SPECIES_CYNDAQUIL
    bufferspeciesname STR_VAR_1, SPECIES_CYNDAQUIL
    showmonpic SPECIES_CYNDAQUIL, 10, 3
    playmoncry SPECIES_CYNDAQUIL, 0
    waitmoncry
    call NewBarkTown_ElmsLab_OfferStarter
    setflag FLAG_GOT_CYNDAQUIL_FROM_AIDE
    bufferspeciesname STR_VAR_1, SPECIES_CYNDAQUIL
    goto NewBarkTown_ElmsLab_StarterReceived

NewBarkTown_ElmsLab_OfferChikorita::
    msgbox NewBarkTown_ElmsLab_Text_ResearchRequest
    setvar VAR_TEMP_1, SPECIES_CHIKORITA
    bufferspeciesname STR_VAR_1, SPECIES_CHIKORITA
    showmonpic SPECIES_CHIKORITA, 10, 3
    playmoncry SPECIES_CHIKORITA, 0
    waitmoncry
    call NewBarkTown_ElmsLab_OfferStarter
    setflag FLAG_GOT_CHIKORITA_FROM_AIDE
    bufferspeciesname STR_VAR_1, SPECIES_CHIKORITA
    goto NewBarkTown_ElmsLab_StarterReceived

NewBarkTown_ElmsLab_OfferTotodile::
    msgbox NewBarkTown_ElmsLab_Text_ResearchRequest
    setvar VAR_TEMP_1, SPECIES_TOTODILE
    bufferspeciesname STR_VAR_1, SPECIES_TOTODILE
    showmonpic SPECIES_TOTODILE, 10, 3
    playmoncry SPECIES_TOTODILE, 0
    waitmoncry
    call NewBarkTown_ElmsLab_OfferStarter
    setflag FLAG_GOT_TOTODILE_FROM_AIDE
    bufferspeciesname STR_VAR_1, SPECIES_TOTODILE
    goto NewBarkTown_ElmsLab_StarterReceived

NewBarkTown_ElmsLab_OfferStarter::
    msgbox NewBarkTown_ElmsLab_Text_StarterOffer, MSGBOX_YESNO
    hidemonpic
    goto_if_eq VAR_RESULT, NO, NewBarkTown_ElmsLab_Decline
    call EventScript_GivePerfectRegionalStarterLv5
    goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
    return

NewBarkTown_ElmsLab_StarterReceived::
    msgbox NewBarkTown_ElmsLab_Text_StarterReceived
    release
    end

NewBarkTown_ElmsLab_AlreadyReceived::
    msgbox NewBarkTown_ElmsLab_Text_AllStartersGiven
    release
    end

NewBarkTown_ElmsLab_Decline::
    msgbox NewBarkTown_ElmsLab_Text_StarterDeclined
    release
    end

@ JOHTO_CHERRYGROVE_ROUTE30_V1
NewBarkTown_ElmsLab_ResearchFollowup::
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_ElmsLab_ResearchFollowupEnd
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, NewBarkTown_ElmsLab_ResearchFollowupEnd
    call NewBarkTown_ElmsLab_AllowResearchReport
    goto_if_eq VAR_RESULT, FALSE, NewBarkTown_ElmsLab_ResearchFollowupEnd
    msgbox NewBarkTown_ElmsLab_Text_ResearchReportDelivered
    setflag FLAG_JOHTO_ELM_REPORT_DELIVERED
NewBarkTown_ElmsLab_ResearchFollowupEnd::
    return

@ Dedicated source Elm art is registered separately; existing research rewards remain native.
NewBarkTown_ElmsLab_ProfessorElm::
    lock
    faceplayer
    @ Visiting the professor also registers this visit to his research team.
    @ CYNDAQUIL receipt remains controlled by its separate gift flag.
    setflag FLAG_JOHTO_MET_LAB_ASSISTANT
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, NewBarkTown_ElmsLab_ProfessorElmComplete
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_ElmsLab_ProfessorElmIntroduction
    call NewBarkTown_ElmsLab_AllowResearchReport
    goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElmReport, MSGBOX_DEFAULT
    setflag FLAG_JOHTO_ELM_REPORT_DELIVERED
    release
    end

NewBarkTown_ElmsLab_ProfessorElmIntroduction::
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElm, MSGBOX_DEFAULT
    release
    end

NewBarkTown_ElmsLab_ProfessorElmComplete::
    msgbox NewBarkTown_ElmsLab_Text_ProfessorElmComplete, MSGBOX_DEFAULT
    release
    end

NewBarkTown_ElmsLab_Hns_AideBusy::
    msgbox NewBarkTown_ElmsLab_Hns_Text_AideBusy, MSGBOX_DEFAULT
    return

@ HNS early Silver: adapt the episode to the native research-report window.
JohtoEarlySilver_CheckEligible::
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE01_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE02_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE03_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE04_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE05_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE06_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE07_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_BADGE08_GET, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_SILVER_AZALEA_DEFEATED, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_HIDE_JOHTO_RADIO_SILVER, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_SILVER_LEAGUE_RESOLVED, JohtoEarlySilver_Ineligible
    goto_if_set FLAG_JOHTO_LEAGUE_CLEARED, JohtoEarlySilver_Ineligible
    goto_if_defeated TRAINER_JOHTO_SILVER_AZALEA, JohtoEarlySilver_Ineligible
    goto_if_defeated TRAINER_JOHTO_SILVER_BURNED_TOWER, JohtoEarlySilver_Ineligible
    goto_if_defeated TRAINER_JOHTO_SILVER_UNDERGROUND, JohtoEarlySilver_Ineligible
    goto_if_defeated TRAINER_JOHTO_SILVER_VICTORY_ROAD, JohtoEarlySilver_Ineligible
    setvar VAR_RESULT, TRUE
    return
JohtoEarlySilver_Ineligible::
    setvar VAR_RESULT, FALSE
    return

JohtoEarlySilver_NotifyTheft::
    goto_if_set FLAG_JOHTO_LAB_THEFT_NOTIFIED, JohtoEarlySilver_NotifyDone
    msgbox NewBarkTown_ElmsLab_Text_TheftEmergency, MSGBOX_DEFAULT
    setflag FLAG_JOHTO_LAB_THEFT_NOTIFIED
    setflag FLAG_HIDE_JOHTO_WINDOW_SILVER
JohtoEarlySilver_NotifyDone::
    return

NewBarkTown_ElmsLab_TheftTransition::
    setvar VAR_TEMP_1, 0
    call NewBarkTown_ElmsLab_UpdateOfficerFlag
    end
NewBarkTown_ElmsLab_TheftSetup::
    call NewBarkTown_ElmsLab_UpdateOfficerFlag
    end
NewBarkTown_ElmsLab_TheftResume::
    call NewBarkTown_ElmsLab_UpdateOfficerFlag
    goto_if_set FLAG_HIDE_JOHTO_THEFT_OFFICER, NewBarkTown_ElmsLab_RemoveOfficer
    addobject LOCALID_NEWBARKTOWN_ELMSLAB_THEFTOFFICER
    end
NewBarkTown_ElmsLab_RemoveOfficer::
    removeobject LOCALID_NEWBARKTOWN_ELMSLAB_THEFTOFFICER
    end
NewBarkTown_ElmsLab_UpdateOfficerFlag::
    setflag FLAG_HIDE_JOHTO_THEFT_OFFICER
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, NewBarkTown_ElmsLab_OfficerFlagDone
    goto_if_unset FLAG_JOHTO_LAB_THEFT_NOTIFIED, NewBarkTown_ElmsLab_OfficerFlagDone
    goto_if_set FLAG_JOHTO_THEFT_REPORT_RESOLVED, NewBarkTown_ElmsLab_OfficerFlagDone
    clearflag FLAG_HIDE_JOHTO_THEFT_OFFICER
NewBarkTown_ElmsLab_OfficerFlagDone::
    return

NewBarkTown_ElmsLab_TheftFrameTable::
    map_script_2 VAR_TEMP_1, 0, NewBarkTown_ElmsLab_TheftFrame
    .2byte 0
NewBarkTown_ElmsLab_TheftFrame::
    setvar VAR_TEMP_1, 1
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, NewBarkTown_ElmsLab_TheftFrameEnd
    goto_if_unset FLAG_JOHTO_LAB_THEFT_NOTIFIED, NewBarkTown_ElmsLab_TheftFrameEnd
    goto_if_unset FLAG_JOHTO_SILVER_FIRST_DEFEATED, NewBarkTown_ElmsLab_TheftFrameEnd
    goto_if_set FLAG_JOHTO_THEFT_REPORT_RESOLVED, NewBarkTown_ElmsLab_TheftFrameEnd
    lockall
    call NewBarkTown_ElmsLab_RecordWitness
    releaseall
NewBarkTown_ElmsLab_TheftFrameEnd::
    end

NewBarkTown_ElmsLab_AllowResearchReport::
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, NewBarkTown_ElmsLab_ReportAllowed
    call JohtoEarlySilver_NotifyTheft
    goto_if_set FLAG_JOHTO_THEFT_REPORT_RESOLVED, NewBarkTown_ElmsLab_ReportAllowed
    clearflag FLAG_HIDE_JOHTO_THEFT_OFFICER
    addobject LOCALID_NEWBARKTOWN_ELMSLAB_THEFTOFFICER
    goto_if_unset FLAG_JOHTO_SILVER_FIRST_DEFEATED, NewBarkTown_ElmsLab_NeedWitness
    call NewBarkTown_ElmsLab_RecordWitness
NewBarkTown_ElmsLab_ReportAllowed::
    setvar VAR_RESULT, TRUE
    return
NewBarkTown_ElmsLab_NeedWitness::
    msgbox NewBarkTown_ElmsLab_Text_TheftNeedWitness, MSGBOX_DEFAULT
    setvar VAR_RESULT, FALSE
    return
NewBarkTown_ElmsLab_RecordWitness::
    msgbox NewBarkTown_ElmsLab_Text_OfficerWitness, MSGBOX_DEFAULT
    msgbox NewBarkTown_ElmsLab_Text_SeparateSpecimen, MSGBOX_DEFAULT
    setflag FLAG_JOHTO_THEFT_REPORT_RESOLVED
    setflag FLAG_HIDE_JOHTO_THEFT_OFFICER
    removeobject LOCALID_NEWBARKTOWN_ELMSLAB_THEFTOFFICER
    return
NewBarkTown_ElmsLab_TheftOfficer::
    lock
    faceplayer
    call NewBarkTown_ElmsLab_AllowResearchReport
    release
    end

NewBarkTown_ElmsLab_HealingMachine::
    lockall
    msgbox NewBarkTown_ElmsLab_Text_HealOffer, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, NewBarkTown_ElmsLab_HealCancel
    closemessage
    call EventScript_OutOfCenterPartyHeal
    msgbox NewBarkTown_ElmsLab_Text_HealDone, MSGBOX_DEFAULT
    releaseall
    end
NewBarkTown_ElmsLab_HealCancel::
    msgbox NewBarkTown_ElmsLab_Text_HealCancel, MSGBOX_DEFAULT
    releaseall
    end
