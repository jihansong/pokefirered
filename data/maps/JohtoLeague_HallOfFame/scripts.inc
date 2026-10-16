JohtoLeague_HallOfFame_MapScripts::
    .byte 0

JohtoLeague_HallOfFame_Record::
    lock
    faceplayer
    goto_if_unset FLAG_SYS_GAME_CLEAR, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE01_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE02_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE03_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE04_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE05_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE06_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE07_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_BADGE08_GET, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_JOHTO_LANCE_CHAMPION_CLEARED, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_JOHTO_WILL_CLEARED, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_JOHTO_KOGA_CLEARED, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_JOHTO_BRUNO_CLEARED, JohtoLeague_HallOfFame_NotReady
    goto_if_unset FLAG_JOHTO_KAREN_CLEARED, JohtoLeague_HallOfFame_NotReady
    msgbox JohtoLeague_HallOfFame_Text_Record, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, JohtoLeague_HallOfFame_Later
    closemessage
    dofieldeffect FLDEFF_HALL_OF_FAME_RECORD
    waitfieldeffect FLDEFF_HALL_OF_FAME_RECORD
    delay 40
    setflag FLAG_JOHTO_LEAGUE_CLEARED
    fadescreenspeed FADE_TO_BLACK, 24
    special EnterHallOfFame
    waitstate
    release
    end
JohtoLeague_HallOfFame_NotReady::
    msgbox JohtoLeague_HallOfFame_Text_NotReady
    release
    end
JohtoLeague_HallOfFame_Later::
    msgbox JohtoLeague_HallOfFame_Text_Later
    release
    end
