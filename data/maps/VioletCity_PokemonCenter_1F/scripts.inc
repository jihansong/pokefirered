VioletCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, VioletCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

VioletCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_VIOLET_CITY
    end

VioletCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

VioletCity_PokemonCenter_1F_Traveler::
    msgbox VioletCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

VioletCity_PokemonCenter_1F_Hiker::
    msgbox VioletCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

