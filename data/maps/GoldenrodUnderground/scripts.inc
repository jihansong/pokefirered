GoldenrodUnderground_MapScripts::
    .byte 0

GoldenrodUnderground_Worker::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodUnderground_WorkerAfter
    goto_if_set FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodUnderground_WorkerCode
    msgbox GoldenrodUnderground_Text_WorkerBefore
    release
    end
GoldenrodUnderground_WorkerCode::
    msgbox GoldenrodUnderground_Text_WorkerCode
    release
    end
GoldenrodUnderground_WorkerAfter::
    msgbox GoldenrodUnderground_Text_WorkerAfter
    release
    end

GoldenrodUnderground_BasementGate::
lockall
    goto_if_unset FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodUnderground_BasementGateClosed
    releaseall
    warp MAP_GOLDENROD_UNDERGROUND_BASEMENT, 1
    waitstate
    end
GoldenrodUnderground_BasementGateClosed::
    msgbox GoldenrodUnderground_Text_BasementGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, GoldenrodUnderground_BasementGateBack
    waitmovement 0
    releaseall
    end
GoldenrodUnderground_BasementGateBack:
    walk_left
    step_end
