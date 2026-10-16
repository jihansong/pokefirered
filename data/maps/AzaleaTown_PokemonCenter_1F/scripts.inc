AzaleaTown_PokemonCenter_1F_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, AzaleaTown_PokemonCenter_1F_OnTransition
    map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
    .byte 0

AzaleaTown_PokemonCenter_1F_OnTransition::
    setrespawn HEAL_LOCATION_AZALEA_TOWN
    end

AzaleaTown_PokemonCenter_1F_Nurse::
    lock
    faceplayer
    call EventScript_PkmnCenterNurse
    release
    end

AzaleaTown_PokemonCenter_1F_Traveler::
    msgbox AzaleaTown_PokemonCenter_1F_Text_Traveler, MSGBOX_NPC
    end

AzaleaTown_PokemonCenter_1F_Hiker::
    msgbox AzaleaTown_PokemonCenter_1F_Text_Hiker, MSGBOX_NPC
    end

