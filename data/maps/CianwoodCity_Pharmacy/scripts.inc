CianwoodCity_Pharmacy_MapScripts::
    .byte 0

CianwoodCity_Pharmacy_Pharmacist::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_AMPHY_CURED, CianwoodCity_Pharmacy_After
    goto_if_set FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED, CianwoodCity_Pharmacy_Carrying
    goto_if_unset FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED, CianwoodCity_Pharmacy_Before
    msgbox CianwoodCity_Pharmacy_Text_Give
    setflag FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED
    release
    end
CianwoodCity_Pharmacy_Carrying::
    msgbox CianwoodCity_Pharmacy_Text_Carrying
    release
    end
CianwoodCity_Pharmacy_Before::
    msgbox CianwoodCity_Pharmacy_Text_Before
    release
    end
CianwoodCity_Pharmacy_After::
    msgbox CianwoodCity_Pharmacy_Text_After
    release
    end
