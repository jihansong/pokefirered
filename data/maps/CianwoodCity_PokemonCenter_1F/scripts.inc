CianwoodCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, CianwoodCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

CianwoodCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_CIANWOOD_CITY
    end

CianwoodCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

CianwoodCity_PokemonCenter_1F_Traveler::
    msgbox CianwoodCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

CianwoodCity_PokemonCenter_1F_Hiker::
    msgbox CianwoodCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

