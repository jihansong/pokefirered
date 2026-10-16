NewBarkTown_ElmsLab_MapScripts::
    .byte 0

@ ELM's native assistant; the separate Silver story is still pending.
NewBarkTown_ElmsLab_Researcher::
    lock
    faceplayer
    setflag FLAG_JOHTO_MET_LAB_ASSISTANT
    goto_if_set FLAG_GOT_CYNDAQUIL_FROM_AIDE, NewBarkTown_ElmsLab_AlreadyReceived
    msgbox NewBarkTown_ElmsLab_Text_ResearchRequest
    showmonpic SPECIES_CYNDAQUIL, 10, 3
    playmoncry SPECIES_CYNDAQUIL, 0
    waitmoncry
    msgbox NewBarkTown_ElmsLab_Text_CyndaquilOffer, MSGBOX_YESNO
    hidemonpic
    goto_if_eq VAR_RESULT, NO, NewBarkTown_ElmsLab_Decline
    setvar VAR_TEMP_1, SPECIES_CYNDAQUIL
    call EventScript_GiveGiftMonLv5
    goto_if_eq VAR_RESULT, FALSE, EventScript_ReleaseEnd
    setflag FLAG_GOT_CYNDAQUIL_FROM_AIDE
    msgbox NewBarkTown_ElmsLab_Text_Received
    release
    end

NewBarkTown_ElmsLab_AlreadyReceived::
    msgbox NewBarkTown_ElmsLab_Text_AlreadyReceived
    release
    end

NewBarkTown_ElmsLab_Decline::
    msgbox NewBarkTown_ElmsLab_Text_Decline
    release
    end
