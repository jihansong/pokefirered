IcePath_B2F_MapScripts::
    .byte 0

IcePath_B2F_WaterfallKeeper::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED, IcePath_B2F_WaterfallAfter
    goto_if_unset FLAG_JOHTO_RADIO_TOWER_CLEARED, IcePath_B2F_WaterfallBefore
    checkitem ITEM_HM07
    goto_if_eq VAR_RESULT, TRUE, IcePath_B2F_WaterfallAlternate
    checkpcitem ITEM_HM07
    goto_if_eq VAR_RESULT, TRUE, IcePath_B2F_WaterfallAlternate
    goto_if_set FLAG_HIDE_FOUR_ISLAND_ICEFALL_CAVE_1F_HM07, IcePath_B2F_WaterfallAlternate
    goto_if_set FLAG_HOENN_GOT_WALLACE_WATERFALL_REWARD, IcePath_B2F_WaterfallAlternate
    giveitem ITEM_HM07
    goto_if_eq VAR_RESULT, FALSE, IcePath_B2F_WaterfallFull
    setflag FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED
    msgbox IcePath_B2F_Text_WaterfallNew
    release
    end
IcePath_B2F_WaterfallAlternate::
    giveitem ITEM_TM50
    goto_if_eq VAR_RESULT, FALSE, IcePath_B2F_WaterfallFull
    setflag FLAG_JOHTO_ICE_PATH_WATERFALL_REWARDED
    msgbox IcePath_B2F_Text_WaterfallAlternate
    release
    end
IcePath_B2F_WaterfallBefore::
    msgbox IcePath_B2F_Text_WaterfallBefore
    release
    end
IcePath_B2F_WaterfallAfter::
    msgbox IcePath_B2F_Text_WaterfallAfter
    release
    end
IcePath_B2F_WaterfallFull::
    msgbox IcePath_B2F_Text_WaterfallFull
    release
    end
