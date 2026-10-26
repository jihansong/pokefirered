JohtoRoute30_MapScripts::
    map_script MAP_SCRIPT_ON_TRANSITION, JohtoRoute30_TheftTransition
    map_script MAP_SCRIPT_ON_FRAME_TABLE, JohtoRoute30_TheftFrameTable
    .byte 0

JohtoRoute30_Youngster::
    msgbox JohtoRoute30_Text_Youngster, MSGBOX_NPC
    end

JohtoRoute30_Fisher::
    msgbox JohtoRoute30_Text_Fisher, MSGBOX_NPC
    end

JohtoRoute30_RouteSign::
    msgbox JohtoRoute30_Text_RouteSign, MSGBOX_NPC
    end

JohtoRoute30_HouseSign::
    msgbox JohtoRoute30_Text_HouseSign, MSGBOX_NPC
    end


JohtoRoute30_TheftTransition::
    setvar VAR_TEMP_1, 0
    end
JohtoRoute30_TheftFrameTable::
    map_script_2 VAR_TEMP_1, 0, JohtoRoute30_TheftFrame
    .2byte 0
JohtoRoute30_TheftFrame::
    setvar VAR_TEMP_1, 1
    call JohtoEarlySilver_CheckEligible
    goto_if_eq VAR_RESULT, FALSE, JohtoRoute30_TheftFrameEnd
    goto_if_unset FLAG_JOHTO_MR_POKEMON_BRIEFED, JohtoRoute30_TheftFrameEnd
    goto_if_set FLAG_JOHTO_LAB_THEFT_NOTIFIED, JohtoRoute30_TheftFrameEnd
    lockall
    call JohtoEarlySilver_NotifyTheft
    releaseall
JohtoRoute30_TheftFrameEnd::
    end
