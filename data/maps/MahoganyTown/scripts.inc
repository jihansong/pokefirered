MahoganyTown_MapScripts::
    .byte 0

MahoganyTown_Resident::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_ResidentAfter
    msgbox MahoganyTown_Text_ResidentBefore
    release
    end
MahoganyTown_ResidentAfter::
    msgbox MahoganyTown_Text_ResidentAfter
    release
    end

MahoganyTown_EastGuard::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, MahoganyTown_EastOpen
    goto_if_set FLAG_JOHTO_BADGE07_GET, MahoganyTown_RadioNews
    msgbox MahoganyTown_Text_EastBefore
    release
    end
MahoganyTown_RadioNews::
    msgbox MahoganyTown_Text_RadioNews
    release
    end
MahoganyTown_EastOpen::
    msgbox MahoganyTown_Text_EastOpen
    release
    end
