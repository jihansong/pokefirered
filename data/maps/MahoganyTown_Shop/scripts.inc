MahoganyTown_Shop_MapScripts::
    .byte 0

MahoganyTown_Shop_Clerk::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_LANCE_INVESTIGATION_JOINED, MahoganyTown_Shop_Before
    goto_if_set FLAG_JOHTO_ROCKET_HQ_CLEARED, MahoganyTown_Shop_After
    msgbox MahoganyTown_Shop_Text_Entry
    setflag FLAG_JOHTO_LANCE_MOVED_TO_HQ
    release
    warp MAP_JOHTO_ROCKET_HQ_B1F, -1, 6, 17
    waitstate
    end
MahoganyTown_Shop_Before::
    msgbox MahoganyTown_Shop_Text_Before
    release
    end
MahoganyTown_Shop_After::
    msgbox MahoganyTown_Shop_Text_After
    release
    end

MahoganyTown_Shop_StairGuard::
lockall
    goto_if_set FLAG_JOHTO_LANCE_INVESTIGATION_JOINED, MahoganyTown_Shop_StairOpen
    msgbox MahoganyTown_Shop_Text_Before
    applymovement OBJ_EVENT_ID_PLAYER, MahoganyTown_Shop_StairBack
    waitmovement 0
    releaseall
    end
MahoganyTown_Shop_StairOpen::
    setflag FLAG_JOHTO_LANCE_MOVED_TO_HQ
    releaseall
    warp MAP_JOHTO_ROCKET_HQ_B1F, 0
    waitstate
    end
MahoganyTown_Shop_StairBack:
    walk_down
    step_end
