GoldenrodCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, GoldenrodCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

GoldenrodCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_GOLDENROD_CITY
    end

GoldenrodCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

GoldenrodCity_PokemonCenter_1F_Traveler::
    msgbox GoldenrodCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

GoldenrodCity_PokemonCenter_1F_Hiker::
    msgbox GoldenrodCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

