EcruteakCity_EastGate_MapScripts::
    .byte 0

EcruteakCity_EastGate_Officer::
lock
    faceplayer
    goto_if_unset FLAG_JOHTO_BADGE06_GET, EcruteakCity_EastGate_Before
    msgbox EcruteakCity_EastGate_Text_Open
    release
    end
EcruteakCity_EastGate_Before::
    msgbox EcruteakCity_EastGate_Text_Before
    release
    end

EcruteakCity_EastGate_Gate::
goto_if_set FLAG_JOHTO_BADGE06_GET, EcruteakCity_EastGate_Allow
    lockall
    msgbox EcruteakCity_EastGate_Text_Before
    applymovement OBJ_EVENT_ID_PLAYER, EcruteakCity_EastGate_Back
    waitmovement 0
    releaseall
    end
EcruteakCity_EastGate_Allow::
    setvar VAR_TEMP_0, 1
    end
EcruteakCity_EastGate_Back:
    walk_down
    step_end
