GoldenrodCity_NorthGate_MapScripts::
    .byte 0

GoldenrodCity_NorthGate_CheckPass::
goto_if_set FLAG_JOHTO_BADGE03_GET, GoldenrodCity_NorthGate_Pass
    lockall
    msgbox GoldenrodCity_NorthGate_Text_Stop
    applymovement LOCALID_PLAYER, GoldenrodCity_NorthGate_StepBack
    waitmovement 0
    releaseall
    end
GoldenrodCity_NorthGate_Pass::
    setvar VAR_TEMP_0, 1
    end
GoldenrodCity_NorthGate_StepBack:
    walk_down
    step_end

GoldenrodCity_NorthGate_Officer::
msgbox GoldenrodCity_NorthGate_Text_Officer, MSGBOX_NPC
    end

GoldenrodCity_NorthGate_Florist::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED, GoldenrodCity_NorthGate_FloristAfter
    goto_if_unset FLAG_JOHTO_BADGE03_GET, GoldenrodCity_NorthGate_FloristBefore
    msgbox GoldenrodCity_NorthGate_Text_FloristLend
    setflag FLAG_JOHTO_SQUIRTBOTTLE_RECEIVED
    release
    end
GoldenrodCity_NorthGate_FloristBefore::
    msgbox GoldenrodCity_NorthGate_Text_FloristBefore
    release
    end
GoldenrodCity_NorthGate_FloristAfter::
    msgbox GoldenrodCity_NorthGate_Text_FloristAfter
    release
    end
