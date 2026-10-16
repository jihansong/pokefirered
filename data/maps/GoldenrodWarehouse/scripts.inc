GoldenrodWarehouse_MapScripts::
    .byte 0

GoldenrodWarehouse_WAREHOUSE_GRUNT_A::
trainerbattle_single TRAINER_JOHTO_WAREHOUSE_GRUNT_A, GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_AIntro, GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_ADefeat
    msgbox GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_AAfter, MSGBOX_NPC
    end

GoldenrodWarehouse_WAREHOUSE_GRUNT_B::
trainerbattle_single TRAINER_JOHTO_WAREHOUSE_GRUNT_B, GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_BIntro, GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_BDefeat
    msgbox GoldenrodWarehouse_Text_WAREHOUSE_GRUNT_BAfter, MSGBOX_NPC
    end

GoldenrodWarehouse_WAREHOUSE_SCIENTIST::
trainerbattle_single TRAINER_JOHTO_WAREHOUSE_SCIENTIST, GoldenrodWarehouse_Text_WAREHOUSE_SCIENTISTIntro, GoldenrodWarehouse_Text_WAREHOUSE_SCIENTISTDefeat
    msgbox GoldenrodWarehouse_Text_WAREHOUSE_SCIENTISTAfter, MSGBOX_NPC
    end

GoldenrodWarehouse_Director::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_RADIO_TOWER_CLEARED, GoldenrodWarehouse_DirectorReward
    goto_if_set FLAG_JOHTO_RADIO_DIRECTOR_RESCUED, GoldenrodWarehouse_DirectorWaiting
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_GRUNT_A, GoldenrodWarehouse_DirectorBefore
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_GRUNT_B, GoldenrodWarehouse_DirectorBefore
    goto_if_not_defeated TRAINER_JOHTO_WAREHOUSE_SCIENTIST, GoldenrodWarehouse_DirectorBefore
    setflag FLAG_JOHTO_RADIO_DIRECTOR_RESCUED
    msgbox GoldenrodWarehouse_Text_DirectorRescued
    release
    end
GoldenrodWarehouse_DirectorBefore::
    msgbox GoldenrodWarehouse_Text_DirectorBefore
    release
    end
GoldenrodWarehouse_DirectorWaiting::
    msgbox GoldenrodWarehouse_Text_DirectorWaiting
    release
    end
GoldenrodWarehouse_DirectorReward::
    goto_if_set FLAG_JOHTO_RADIO_GOT_TM11, GoldenrodWarehouse_DirectorAfter
    giveitem ITEM_TM11
    goto_if_eq VAR_RESULT, FALSE, GoldenrodWarehouse_DirectorFull
    setflag FLAG_JOHTO_RADIO_GOT_TM11
GoldenrodWarehouse_DirectorAfter::
    goto_if_set FLAG_HOENN_RAYQUAZA_AWAKENED, GoldenrodWarehouse_DirectorHoennCalm
    goto_if_set FLAG_HOENN_SEAFLOOR_CLEARED, GoldenrodWarehouse_DirectorHoennStorm
    msgbox GoldenrodWarehouse_Text_DirectorAfter
    release
    end
GoldenrodWarehouse_DirectorHoennCalm::
    msgbox GoldenrodWarehouse_Text_DirectorHoennCalm
    release
    end
GoldenrodWarehouse_DirectorHoennStorm::
    msgbox GoldenrodWarehouse_Text_DirectorHoennStorm
    release
    end
GoldenrodWarehouse_DirectorFull::
    msgbox GoldenrodWarehouse_Text_DirectorFull
    release
    end
