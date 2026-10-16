OlivineCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, OlivineCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

OlivineCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_OLIVINE_CITY
    end

OlivineCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

OlivineCity_PokemonCenter_1F_Traveler::
    msgbox OlivineCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

OlivineCity_PokemonCenter_1F_Hiker::
    msgbox OlivineCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

