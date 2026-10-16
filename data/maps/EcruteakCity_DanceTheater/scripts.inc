EcruteakCity_DanceTheater_MapScripts::
    .byte 0

EcruteakCity_DanceTheater_NAOKO::
trainerbattle_single TRAINER_JOHTO_KIMONO_NAOKO, EcruteakCity_DanceTheater_Text_NAOKOIntro, EcruteakCity_DanceTheater_Text_NAOKODefeat
    msgbox EcruteakCity_DanceTheater_Text_NAOKOAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_DanceTheater_SAYO::
trainerbattle_single TRAINER_JOHTO_KIMONO_SAYO, EcruteakCity_DanceTheater_Text_SAYOIntro, EcruteakCity_DanceTheater_Text_SAYODefeat
    msgbox EcruteakCity_DanceTheater_Text_SAYOAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_DanceTheater_ZUKI::
trainerbattle_single TRAINER_JOHTO_KIMONO_ZUKI, EcruteakCity_DanceTheater_Text_ZUKIIntro, EcruteakCity_DanceTheater_Text_ZUKIDefeat
    msgbox EcruteakCity_DanceTheater_Text_ZUKIAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_DanceTheater_KUNI::
trainerbattle_single TRAINER_JOHTO_KIMONO_KUNI, EcruteakCity_DanceTheater_Text_KUNIIntro, EcruteakCity_DanceTheater_Text_KUNIDefeat
    msgbox EcruteakCity_DanceTheater_Text_KUNIAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_DanceTheater_MIKI::
trainerbattle_single TRAINER_JOHTO_KIMONO_MIKI, EcruteakCity_DanceTheater_Text_MIKIIntro, EcruteakCity_DanceTheater_Text_MIKIDefeat
    msgbox EcruteakCity_DanceTheater_Text_MIKIAfter, MSGBOX_AUTOCLOSE
    end

EcruteakCity_DanceTheater_Patron::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_DANCE_SURF_REWARDED, EcruteakCity_DanceTheater_PatronAfter
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_NAOKO, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_SAYO, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_ZUKI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_KUNI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_not_defeated TRAINER_JOHTO_KIMONO_MIKI, EcruteakCity_DanceTheater_PatronBefore
    goto_if_set FLAG_GOT_HM03, EcruteakCity_DanceTheater_Alternate
    checkitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, TRUE, EcruteakCity_DanceTheater_Alternate
    checkpcitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, TRUE, EcruteakCity_DanceTheater_Alternate
    checkitemspace ITEM_HM03, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    giveitem ITEM_HM03, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    setflag FLAG_JOHTO_DANCE_SURF_REWARDED
    msgbox EcruteakCity_DanceTheater_Text_Surf
    release
    end
EcruteakCity_DanceTheater_Alternate::
    checkitemspace ITEM_TM35, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    msgbox EcruteakCity_DanceTheater_Text_AlreadySurf
    giveitem ITEM_TM35, 1
    goto_if_eq VAR_RESULT, FALSE, EcruteakCity_DanceTheater_BagFull
    setflag FLAG_JOHTO_DANCE_SURF_REWARDED
    msgbox EcruteakCity_DanceTheater_Text_Alternate
    release
    end
EcruteakCity_DanceTheater_PatronBefore::
    msgbox EcruteakCity_DanceTheater_Text_PatronBefore
    release
    end
EcruteakCity_DanceTheater_PatronAfter::
    msgbox EcruteakCity_DanceTheater_Text_PatronAfter
    release
    end
EcruteakCity_DanceTheater_BagFull::
    msgbox EcruteakCity_DanceTheater_Text_BagFull
    release
    end
