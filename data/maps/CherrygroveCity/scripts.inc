CherrygroveCity_MapScripts::
    map_script MAP_SCRIPT_ON_LOAD, CherrygroveCity_TheftSetup
    map_script MAP_SCRIPT_ON_TRANSITION, CherrygroveCity_TheftTransition
    map_script MAP_SCRIPT_ON_RESUME, CherrygroveCity_TheftResume
    .byte 0


CherrygroveCity_Guide::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MET_LAB_ASSISTANT, CherrygroveCity_GuideBeforeLab
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, CherrygroveCity_GuideReportDone
    goto_if_set FLAG_JOHTO_MET_CHERRYGROVE_GUIDE, CherrygroveCity_GuideAgain
    call CherrygroveCity_Hns_LocalGuide
    msgbox CherrygroveCity_Text_GuideRequest
    setflag FLAG_JOHTO_MET_CHERRYGROVE_GUIDE
    release
    end
CherrygroveCity_GuideBeforeLab::
    msgbox CherrygroveCity_Text_GuideBeforeLab
    release
    end
CherrygroveCity_GuideAgain::
    msgbox CherrygroveCity_Text_GuideAgain
    release
    end
CherrygroveCity_GuideReportDone::
    msgbox CherrygroveCity_Text_GuideReportDone
    release
    end

CherrygroveCity_Girl::
    msgbox CherrygroveCity_Text_Girl, MSGBOX_NPC
    end

CherrygroveCity_Fisher::
    msgbox CherrygroveCity_Text_Fisher, MSGBOX_NPC
    end

CherrygroveCity_CenterSign::
    msgbox CherrygroveCity_Text_CenterSign, MSGBOX_NPC
    end

CherrygroveCity_MartSign::
    msgbox CherrygroveCity_Text_MartSign, MSGBOX_NPC
    end

CherrygroveCity_GuideSign::
    msgbox CherrygroveCity_Text_GuideSign, MSGBOX_NPC
    end

@ Donor: Cherrygrove guide reaction and optional town introduction.
@ No positional movement: current and donor city geometry differ.
CherrygroveCity_Hns_LocalGuide::
    playse SE_PIN
    applymovement VAR_LAST_TALKED, Common_Movement_ExclamationMark
    waitmovement 0
    msgbox CherrygroveCity_Hns_Text_GuideOffer, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, CherrygroveCity_Hns_LocalGuideEnd
    msgbox CherrygroveCity_Hns_Text_Center, MSGBOX_DEFAULT
    msgbox CherrygroveCity_Hns_Text_Mart, MSGBOX_DEFAULT
    msgbox CherrygroveCity_Hns_Text_Route30, MSGBOX_DEFAULT
CherrygroveCity_Hns_LocalGuideEnd::
    return

CherrygroveCity_TheftTransition::
    setvar VAR_TEMP_2, 0
    call CherrygroveCity_UpdateFirstSilverFlag
    end
CherrygroveCity_TheftSetup::
    call CherrygroveCity_UpdateFirstSilverFlag
    end
CherrygroveCity_TheftResume::
    call CherrygroveCity_UpdateFirstSilverFlag
    goto_if_set FLAG_HIDE_JOHTO_FIRST_SILVER, CherrygroveCity_RemoveFirstSilver
    addobject LOCALID_CHERRYGROVE_FIRSTSILVER
    end
CherrygroveCity_RemoveFirstSilver::
    removeobject LOCALID_CHERRYGROVE_FIRSTSILVER
    end
CherrygroveCity_UpdateFirstSilverFlag::
    setflag FLAG_HIDE_JOHTO_FIRST_SILVER
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, CherrygroveCity_FirstSilverFlagDone
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, CherrygroveCity_FirstSilverFlagDone
    goto_if_set FLAG_JOHTO_SILVER_FIRST_DEFEATED, CherrygroveCity_FirstSilverFlagDone
    clearflag FLAG_HIDE_JOHTO_FIRST_SILVER
CherrygroveCity_FirstSilverFlagDone::
    return
CherrygroveCity_FirstSilverApproach::
    setvar VAR_TEMP_2, 1
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, CherrygroveCity_FirstSilverEnd
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, CherrygroveCity_FirstSilverEnd
    goto_if_set FLAG_JOHTO_SILVER_FIRST_DEFEATED, CherrygroveCity_FirstSilverEnd
CherrygroveCity_FirstSilverBattle::
    lockall
    setvar VAR_LAST_TALKED, LOCALID_CHERRYGROVE_FIRSTSILVER
    faceplayer
    call JohtoEarlySilver_NotifyTheft
    msgbox CherrygroveCity_Text_FirstSilverIntro, MSGBOX_DEFAULT
    trainerbattle_no_intro TRAINER_JOHTO_SILVER_CHERRYGROVE, CherrygroveCity_Text_FirstSilverDefeat
    setflag FLAG_JOHTO_SILVER_FIRST_DEFEATED
    msgbox CherrygroveCity_Text_FirstSilverAfter, MSGBOX_DEFAULT
    setflag FLAG_HIDE_JOHTO_FIRST_SILVER
    removeobject LOCALID_CHERRYGROVE_FIRSTSILVER
    releaseall
CherrygroveCity_FirstSilverEnd::
    end
CherrygroveCity_FirstSilver::
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, CherrygroveCity_FirstSilverEnd
    goto_if_set FLAG_JOHTO_SILVER_FIRST_DEFEATED, CherrygroveCity_FirstSilverEnd
    goto CherrygroveCity_FirstSilverBattle
