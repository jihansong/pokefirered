IlexForest_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, IlexForest_OnTransition
    .byte 0

IlexForest_OnTransition::
goto_if_unset FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_KeepWildPosition
    setobjectxyperm 2, 26, 35
    end
IlexForest_KeepWildPosition::
    end

IlexForest_Apprentice::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_ApprenticeThanks
    goto_if_set FLAG_JOHTO_ILEX_HELP_REQUESTED, IlexForest_ApprenticeWait
    msgbox IlexForest_Text_ApprenticeRequest
    setflag FLAG_JOHTO_ILEX_HELP_REQUESTED
    release
    end
IlexForest_ApprenticeWait::
    msgbox IlexForest_Text_ApprenticeWait
    release
    end
IlexForest_ApprenticeThanks::
    msgbox IlexForest_Text_ApprenticeThanks
    release
    end

IlexForest_Farfetchd::
lock
    faceplayer
    playmoncry SPECIES_FARFETCHD, 0
    waitmoncry
    goto_if_set FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_FarfetchdHome
    goto_if_unset FLAG_JOHTO_ILEX_HELP_REQUESTED, IlexForest_FarfetchdShy
    showmonpic SPECIES_FARFETCHD, 10, 3
    msgbox IlexForest_Text_FarfetchdReturn
    hidemonpic
    applymovement 2, IlexForest_FarfetchdHop
    waitmovement 0
    fadescreen FADE_TO_BLACK
    setflag FLAG_JOHTO_ILEX_FARFETCHD_RETURNED
    setobjectxy 2, 26, 35
    setobjectxyperm 2, 26, 35
    fadescreen FADE_FROM_BLACK
    msgbox IlexForest_Text_FarfetchdBack
    release
    end
IlexForest_FarfetchdHome::
    msgbox IlexForest_Text_FarfetchdHome
    release
    end
IlexForest_FarfetchdShy::
    msgbox IlexForest_Text_FarfetchdShy
    release
    end
IlexForest_FarfetchdHop:
    jump_in_place_down
    step_end

IlexForest_Master::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_ILEX_FARFETCHD_RETURNED, IlexForest_MasterBefore
    goto_if_set FLAG_JOHTO_ILEX_CUT_BRIEFED, IlexForest_MasterAfter
    goto_if_set FLAG_GOT_HM01, IlexForest_MasterAlreadyHasCut
    checkitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, TRUE, IlexForest_MasterAlreadyHasCut
    checkpcitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, TRUE, IlexForest_MasterAlreadyHasCut
    checkitemspace ITEM_HM01, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    giveitem ITEM_HM01, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    setflag FLAG_JOHTO_ILEX_CUT_BRIEFED
    msgbox IlexForest_Text_MasterCut
    release
    end
IlexForest_MasterAlreadyHasCut::
    checkitemspace ITEM_TM48, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    msgbox IlexForest_Text_MasterAlreadyHasCut
    giveitem ITEM_TM48, 1
    goto_if_eq VAR_RESULT, FALSE, IlexForest_MasterBagFull
    setflag FLAG_JOHTO_ILEX_CUT_BRIEFED
    msgbox IlexForest_Text_MasterAlternate
    release
    end
IlexForest_MasterAfter::
    msgbox IlexForest_Text_MasterAfter
    release
    end
IlexForest_MasterBefore::
    msgbox IlexForest_Text_MasterBefore
    release
    end
IlexForest_MasterBagFull::
    msgbox IlexForest_Text_MasterBagFull
    release
    end

IlexForest_ForestSign::
msgbox IlexForest_Text_ForestSign, MSGBOX_NPC
    end
