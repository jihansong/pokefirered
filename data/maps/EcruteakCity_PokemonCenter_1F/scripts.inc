EcruteakCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, EcruteakCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

EcruteakCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_ECRUTEAK_CITY
    end

EcruteakCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

EcruteakCity_PokemonCenter_1F_Traveler::
    msgbox EcruteakCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

EcruteakCity_PokemonCenter_1F_Hiker::
    msgbox EcruteakCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

