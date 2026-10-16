MahoganyTown_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, MahoganyTown_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

MahoganyTown_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_MAHOGANY_TOWN
    end

MahoganyTown_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

MahoganyTown_PokemonCenter_1F_Traveler::
    msgbox MahoganyTown_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

MahoganyTown_PokemonCenter_1F_Hiker::
    msgbox MahoganyTown_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

