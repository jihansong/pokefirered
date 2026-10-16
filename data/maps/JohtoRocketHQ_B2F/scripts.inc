JohtoRocketHQ_B2F_MapScripts::
    .byte 0

JohtoRocketHQ_B2F_HQ_SCIENTIST::
trainerbattle_single TRAINER_JOHTO_HQ_SCIENTIST, JohtoRocketHQ_B2F_Text_HQ_SCIENTISTIntro, JohtoRocketHQ_B2F_Text_HQ_SCIENTISTDefeat
    msgbox JohtoRocketHQ_B2F_Text_HQ_SCIENTISTAfter, MSGBOX_NPC
    end

JohtoRocketHQ_B2F_PETREL::
trainerbattle_single TRAINER_JOHTO_PETREL, JohtoRocketHQ_B2F_Text_PETRELIntro, JohtoRocketHQ_B2F_Text_PETRELDefeat
    msgbox JohtoRocketHQ_B2F_Text_PETRELAfter, MSGBOX_NPC
    end

JohtoRocketHQ_B2F_SecurityDoor::
lockall
    goto_if_defeated TRAINER_JOHTO_PETREL, JohtoRocketHQ_B2F_Open
    msgbox JohtoRocketHQ_B2F_Text_Closed
    applymovement OBJ_EVENT_ID_PLAYER, JohtoRocketHQ_B2F_Back
    waitmovement 0
    releaseall
    end
JohtoRocketHQ_B2F_Open::
    releaseall
    warp MAP_JOHTO_ROCKET_HQ_B3F, 0
    waitstate
    end
JohtoRocketHQ_B2F_Back:
    walk_down
    step_end
