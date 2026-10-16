JohtoIndigoPlateau_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, JohtoIndigoPlateau_OnTransition
    .byte 0
JohtoIndigoPlateau_OnTransition::
    setflag FLAG_JOHTO_LEAGUE_ARRIVED
    end
JohtoIndigoPlateau_Official::
    lock
    faceplayer
    goto_if_set FLAG_JOHTO_LEAGUE_CLEARED, JohtoIndigoPlateau_Champion
    msgbox JohtoIndigoPlateau_Text_Challenge
    release
    end
JohtoIndigoPlateau_Champion::
    msgbox JohtoIndigoPlateau_Text_Champion
    release
    end
