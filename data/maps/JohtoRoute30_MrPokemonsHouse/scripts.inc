JohtoRoute30_MrPokemonsHouse_MapScripts::
    .byte 0


JohtoRoute30_MrPokemonsHouse_Researcher::
    lock
    faceplayer
    goto_if_unset FLAG_JOHTO_MET_CHERRYGROVE_GUIDE, JohtoRoute30_MrPokemonsHouse_BeforeReferral
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, JohtoRoute30_MrPokemonsHouse_AfterReport
    goto_if_set FLAG_JOHTO_MR_POKEMON_BRIEFED, JohtoRoute30_MrPokemonsHouse_Repeat
    msgbox JohtoRoute30_MrPokemonsHouse_Text_ResearchReport
    setflag FLAG_JOHTO_MR_POKEMON_BRIEFED
    release
    end
JohtoRoute30_MrPokemonsHouse_BeforeReferral::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_BeforeReferral
    release
    end
JohtoRoute30_MrPokemonsHouse_Repeat::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_Repeat
    release
    end
JohtoRoute30_MrPokemonsHouse_AfterReport::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_AfterReport
    release
    end
JohtoRoute30_MrPokemonsHouse_OaksAide::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_ELM_REPORT_DELIVERED, JohtoRoute30_MrPokemonsHouse_AideAfterReport
    msgbox JohtoRoute30_MrPokemonsHouse_Text_OaksAide
    release
    end
JohtoRoute30_MrPokemonsHouse_AideAfterReport::
    msgbox JohtoRoute30_MrPokemonsHouse_Text_AideAfterReport
    release
    end
