SlowpokeWell_1F_MapScripts::
    .byte 0

SlowpokeWell_1F_GruntA::
    trainerbattle_single TRAINER_JOHTO_WELL_GRUNT_A, SlowpokeWell_1F_Text_GruntIntro, SlowpokeWell_1F_Text_GruntDefeat
    msgbox SlowpokeWell_1F_Text_GruntAfter, MSGBOX_AUTOCLOSE
    end

SlowpokeWell_1F_GruntB::
    trainerbattle_single TRAINER_JOHTO_WELL_GRUNT_B, SlowpokeWell_1F_Text_GruntIntro, SlowpokeWell_1F_Text_GruntDefeat
    msgbox SlowpokeWell_1F_Text_GruntAfter, MSGBOX_AUTOCLOSE
    end

SlowpokeWell_1F_Commander::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_KURT_RESCUE_REQUESTED, SlowpokeWell_1F_NoRequest
    goto_if_not_defeated TRAINER_JOHTO_WELL_GRUNT_A, SlowpokeWell_1F_Guards
    goto_if_not_defeated TRAINER_JOHTO_WELL_GRUNT_B, SlowpokeWell_1F_Guards
    trainerbattle_single TRAINER_JOHTO_WELL_COMMANDER, SlowpokeWell_1F_Text_Intro, SlowpokeWell_1F_Text_Defeat, SlowpokeWell_1F_Victory, NO_MUSIC
    goto SlowpokeWell_1F_Victory
SlowpokeWell_1F_Victory::
    msgbox SlowpokeWell_1F_Text_Rescue
    setflag FLAG_JOHTO_SLOWPOKE_WELL_CLEARED
    removeobject 1
    removeobject 2
    removeobject 3
    release
    end
SlowpokeWell_1F_NoRequest::
    msgbox SlowpokeWell_1F_Text_NoRequest
    release
    end
SlowpokeWell_1F_Guards::
    msgbox SlowpokeWell_1F_Text_Guards
    release
    end
SlowpokeWell_1F_Slowpoke::
    lock
    faceplayer
    playmoncry SPECIES_SLOWPOKE, 0
    waitmoncry
    goto_if_set FLAG_JOHTO_SLOWPOKE_WELL_CLEARED, SlowpokeWell_1F_Safe
    msgbox SlowpokeWell_1F_Text_SlowpokeWorried
    release
    end
SlowpokeWell_1F_Safe::
    msgbox SlowpokeWell_1F_Text_SlowpokeSafe
    release
    end
