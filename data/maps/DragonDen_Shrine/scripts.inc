DragonDen_Shrine_MapScripts::
    .byte 0

DragonDen_Shrine_DragonMaster::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_DRAGON_TRIAL_CLEARED, DragonDen_Shrine_DragonMasterReward
    goto_if_unset FLAG_JOHTO_CLAIR_DEFEATED, DragonDen_Shrine_DragonMasterBefore
    msgbox DragonDen_Shrine_Text_DragonMasterQuestion, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, FALSE, DragonDen_Shrine_DragonMasterReflect
    setflag FLAG_JOHTO_DRAGON_TRIAL_CLEARED
    setflag FLAG_JOHTO_BADGE08_GET
    msgbox DragonDen_Shrine_Text_DragonMasterAccepted
DragonDen_Shrine_DragonMasterReward::
    goto_if_set FLAG_JOHTO_CLAIR_TM02_RECEIVED, DragonDen_Shrine_DragonMasterAfter
    giveitem ITEM_TM02
    goto_if_eq VAR_RESULT, FALSE, DragonDen_Shrine_DragonMasterFull
    setflag FLAG_JOHTO_CLAIR_TM02_RECEIVED
DragonDen_Shrine_DragonMasterAfter::
    msgbox DragonDen_Shrine_Text_DragonMasterAfter
    release
    end
DragonDen_Shrine_DragonMasterBefore::
    msgbox DragonDen_Shrine_Text_DragonMasterBefore
    release
    end
DragonDen_Shrine_DragonMasterReflect::
    msgbox DragonDen_Shrine_Text_DragonMasterReflect
    release
    end
DragonDen_Shrine_DragonMasterFull::
    msgbox DragonDen_Shrine_Text_DragonMasterFull
    release
    end
