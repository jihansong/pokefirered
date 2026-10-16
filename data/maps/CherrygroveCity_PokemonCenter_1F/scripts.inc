CherrygroveCity_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, CherrygroveCity_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

CherrygroveCity_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_CHERRYGROVE_CITY
    end

CherrygroveCity_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

CherrygroveCity_PokemonCenter_1F_Traveler::
    msgbox CherrygroveCity_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

CherrygroveCity_PokemonCenter_1F_Hiker::
    msgbox CherrygroveCity_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

