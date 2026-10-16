GoldenrodCity_RadioTower_3F_MapScripts::
    .byte 0

GoldenrodCity_RadioTower_3F_RADIO_SCIENTIST::
trainerbattle_single TRAINER_JOHTO_RADIO_SCIENTIST, GoldenrodCity_RadioTower_3F_Text_RADIO_SCIENTISTIntro, GoldenrodCity_RadioTower_3F_Text_RADIO_SCIENTISTDefeat
    msgbox GoldenrodCity_RadioTower_3F_Text_RADIO_SCIENTISTAfter, MSGBOX_NPC
    end

GoldenrodCity_RadioTower_3F_Petrel::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_BASEMENT_ACCESS, GoldenrodCity_RadioTower_3F_PetrelAfter
    goto_if_unset FLAG_JOHTO_BADGE07_GET, GoldenrodCity_RadioTower_3F_PetrelBefore
    goto_if_defeated TRAINER_JOHTO_PETREL_RADIO, GoldenrodCity_RadioTower_3F_PetrelVictory
    trainerbattle_single TRAINER_JOHTO_PETREL_RADIO, GoldenrodCity_RadioTower_3F_Text_PetrelIntro, GoldenrodCity_RadioTower_3F_Text_PetrelDefeat, GoldenrodCity_RadioTower_3F_PetrelVictory, NO_MUSIC
    goto GoldenrodCity_RadioTower_3F_PetrelVictory
GoldenrodCity_RadioTower_3F_PetrelVictory::
    setflag FLAG_JOHTO_RADIO_BASEMENT_ACCESS
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelAfter
    setflag FLAG_HIDE_JOHTO_RADIO_PETREL
    removeobject LOCALID_RADIO_PETREL
    release
    end
GoldenrodCity_RadioTower_3F_PetrelBefore::
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelBefore
    release
    end
GoldenrodCity_RadioTower_3F_PetrelAfter::
    msgbox GoldenrodCity_RadioTower_3F_Text_PetrelAfter
    release
    end

GoldenrodCity_RadioTower_3F_UpperGate::
lockall
    goto_if_unset FLAG_JOHTO_RADIO_DIRECTOR_RESCUED, GoldenrodCity_RadioTower_3F_UpperGateClosed
    releaseall
    warp MAP_GOLDENROD_CITY_RADIO_TOWER_4F, 1
    waitstate
    end
GoldenrodCity_RadioTower_3F_UpperGateClosed::
    msgbox GoldenrodCity_RadioTower_3F_Text_UpperGateClosed
    applymovement OBJ_EVENT_ID_PLAYER, GoldenrodCity_RadioTower_3F_UpperGateBack
    waitmovement 0
    releaseall
    end
GoldenrodCity_RadioTower_3F_UpperGateBack:
    walk_left
    step_end
