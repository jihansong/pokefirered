OlivineLighthouse_6F_MapScripts::
    .byte 0

OlivineLighthouse_6F_Jasmine::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineLighthouse_6F_JasmineAfter
    goto_if_set FLAG_JOHTO_CIANWOOD_MEDICINE_RECEIVED, OlivineLighthouse_6F_Cure
    showmonpic SPECIES_AMPHAROS, 10, 3
    playmoncry SPECIES_AMPHAROS, CRY_MODE_NORMAL
    waitmoncry
    msgbox OlivineLighthouse_6F_Text_Request
    hidemonpic
    setflag FLAG_JOHTO_LIGHTHOUSE_MEDICINE_REQUESTED
    release
    end
OlivineLighthouse_6F_Cure::
    msgbox OlivineLighthouse_6F_Text_Deliver
    showmonpic SPECIES_AMPHAROS, 10, 3
    playmoncry SPECIES_AMPHAROS, CRY_MODE_NORMAL
    waitmoncry
    msgbox OlivineLighthouse_6F_Text_Healthy
    hidemonpic
    setflag FLAG_JOHTO_AMPHY_CURED
    clearflag FLAG_HIDE_JOHTO_JASMINE_GYM
    msgbox OlivineLighthouse_6F_Text_Return
    removeobject 1
    release
    end
OlivineLighthouse_6F_JasmineAfter::
    msgbox OlivineLighthouse_6F_Text_After
    release
    end
