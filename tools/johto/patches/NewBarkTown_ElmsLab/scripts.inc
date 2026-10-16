NewBarkTown_ElmsLab_MapScripts::
    .byte 0

@ ELM's native assistant; the separate Silver story is still pending.
NewBarkTown_ElmsLab_Researcher::
    lock
    faceplayer
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
    msgbox NewBarkTown_ElmsLab_Text_ResearchReportDelivered
    setflag FLAG_JOHTO_ELM_REPORT_DELIVERED
NewBarkTown_ElmsLab_ResearchFollowupEnd::
    return

@ Named professor uses a temporary native research sprite; dedicated Elm art pending.
NewBarkTown_ElmsLab_ProfessorElm::
    lock
    faceplayer
    @ Visiting the professor also registers this visit to his research team.
    @ CYNDAQUIL receipt remains controlled by its separate gift flag.
    setflag FLAG_JOHTO_MET_LAB_ASSISTANT
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, NewBarkTown_ElmsLab_ProfessorElmComplete
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, NewBarkTown_ElmsLab_ProfessorElmIntroduction
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
