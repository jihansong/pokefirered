CianwoodCity_MapScripts::
    .byte 0

CianwoodCity_Resident::
msgbox CianwoodCity_Text_Resident, MSGBOX_NPC
    end

CianwoodCity_CenterSign::
msgbox CianwoodCity_Text_CenterSign, MSGBOX_NPC
    end

CianwoodCity_PharmacySign::
msgbox CianwoodCity_Text_PharmacySign, MSGBOX_NPC
    end

CianwoodCity_GymSign::
msgbox CianwoodCity_Text_GymSign, MSGBOX_NPC
    end

CianwoodCity_FlyGift::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_FLY_REWARDED, CianwoodCity_FlyGiftAfter
    goto_if_unset FLAG_JOHTO_BADGE05_GET, CianwoodCity_FlyGiftBefore
    goto_if_set FLAG_GOT_HM02, CianwoodCity_FlyGiftAlternate
    checkitem ITEM_HM02
    goto_if_eq VAR_RESULT, TRUE, CianwoodCity_FlyGiftAlternate
    checkpcitem ITEM_HM02, 1
    goto_if_eq VAR_RESULT, TRUE, CianwoodCity_FlyGiftAlternate
    giveitem ITEM_HM02
    goto_if_eq VAR_RESULT, FALSE, CianwoodCity_FlyGiftFull
    setflag FLAG_GOT_HM02
    setflag FLAG_JOHTO_FLY_REWARDED
    msgbox CianwoodCity_Text_FlyGiftHM
    release
    end
CianwoodCity_FlyGiftAlternate::
    giveitem ITEM_TM02
    goto_if_eq VAR_RESULT, FALSE, CianwoodCity_FlyGiftFull
    setflag FLAG_JOHTO_FLY_REWARDED
    msgbox CianwoodCity_Text_FlyGiftAlternate
    release
    end
CianwoodCity_FlyGiftBefore::
    msgbox CianwoodCity_Text_FlyGiftBefore
    release
    end
CianwoodCity_FlyGiftFull::
    msgbox CianwoodCity_Text_FlyGiftFull
    release
    end
CianwoodCity_FlyGiftAfter::
    msgbox CianwoodCity_Text_FlyGiftAfter
    release
    end
