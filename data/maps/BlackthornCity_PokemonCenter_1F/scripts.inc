BlackthornCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, BlackthornCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

BlackthornCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_BLACKTHORN_CITY
    end

BlackthornCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

BlackthornCity_PokemonCenter_1F_Traveler::
    msgbox BlackthornCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

BlackthornCity_PokemonCenter_1F_Hiker::
    msgbox BlackthornCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

