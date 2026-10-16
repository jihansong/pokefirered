JohtoRoute44_MapScripts::
    .byte 0

JohtoRoute44_WestGate::
lockall
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, JohtoRoute44_WestGateOpen
    msgbox JohtoRoute44_Text_WestGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, JohtoRoute44_WestGateBack
    waitmovement 0
    releaseall
    end
JohtoRoute44_WestGateOpen::
    setvar VAR_TEMP_0, 1
    releaseall
    end
JohtoRoute44_WestGateBack:
    walk_left
    step_end

JohtoRoute44_Warden::
msgbox JohtoRoute44_Text_Warden, MSGBOX_NPC
    end

JohtoRoute44_WILTON::
trainerbattle_single TRAINER_JOHTO_WILTON, JohtoRoute44_Text_WILTONIntro, JohtoRoute44_Text_WILTONDefeat
    msgbox JohtoRoute44_Text_WILTONAfter, MSGBOX_NPC
    end

JohtoRoute44_VANCE::
trainerbattle_single TRAINER_JOHTO_VANCE, JohtoRoute44_Text_VANCEIntro, JohtoRoute44_Text_VANCEDefeat
    msgbox JohtoRoute44_Text_VANCEAfter, MSGBOX_NPC
    end
