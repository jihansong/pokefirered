OlivineCity_Cafe_MapScripts::
    .byte 0

OlivineCity_Cafe_StrengthGift::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_STRENGTH_REWARDED, OlivineCity_Cafe_StrengthGiftAfter
    goto_if_set FLAG_GOT_HM04, OlivineCity_Cafe_StrengthGiftAlternate
    checkitem ITEM_HM04
    goto_if_eq VAR_RESULT, TRUE, OlivineCity_Cafe_StrengthGiftAlternate
    checkpcitem ITEM_HM04, 1
    goto_if_eq VAR_RESULT, TRUE, OlivineCity_Cafe_StrengthGiftAlternate
    giveitem ITEM_HM04
    goto_if_eq VAR_RESULT, FALSE, OlivineCity_Cafe_StrengthGiftFull
    setflag FLAG_GOT_HM04
    setflag FLAG_JOHTO_STRENGTH_REWARDED
    msgbox OlivineCity_Cafe_Text_StrengthGiftHM
    release
    end
OlivineCity_Cafe_StrengthGiftAlternate::
    giveitem ITEM_TM08
    goto_if_eq VAR_RESULT, FALSE, OlivineCity_Cafe_StrengthGiftFull
    setflag FLAG_JOHTO_STRENGTH_REWARDED
    msgbox OlivineCity_Cafe_Text_StrengthGiftAlternate
    release
    end
OlivineCity_Cafe_StrengthGiftBefore::
    msgbox OlivineCity_Cafe_Text_StrengthGiftBefore
    release
    end
OlivineCity_Cafe_StrengthGiftFull::
    msgbox OlivineCity_Cafe_Text_StrengthGiftFull
    release
    end
OlivineCity_Cafe_StrengthGiftAfter::
    msgbox OlivineCity_Cafe_Text_StrengthGiftAfter
    release
    end
