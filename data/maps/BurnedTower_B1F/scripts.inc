BurnedTower_B1F_MapScripts::
    .byte 0

BurnedTower_B1F_Investigate::
goto_if_set FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, BurnedTower_B1F_InvestigationDone
    goto_if_unset FLAG_JOHTO_SILVER_BURNED_TOWER_DEFEATED, BurnedTower_B1F_InvestigationDone
    lockall
    msgbox BurnedTower_B1F_Text_Awakening
    setvar VAR_0x8004, SPECIES_RAIKOU
    special SetSeenMon
    showmonpic SPECIES_RAIKOU, 10, 3
    playmoncry SPECIES_RAIKOU, 0
    waitmoncry
    hidemonpic
    setvar VAR_0x8004, SPECIES_ENTEI
    special SetSeenMon
    showmonpic SPECIES_ENTEI, 10, 3
    playmoncry SPECIES_ENTEI, 0
    waitmoncry
    hidemonpic
    setvar VAR_0x8004, SPECIES_SUICUNE
    special SetSeenMon
    showmonpic SPECIES_SUICUNE, 10, 3
    playmoncry SPECIES_SUICUNE, 0
    waitmoncry
    hidemonpic
    msgbox BurnedTower_B1F_Text_Escaped
    setflag FLAG_JOHTO_BURNED_TOWER_INVESTIGATED
    setvar VAR_TEMP_0, 1
    releaseall
    end
BurnedTower_B1F_InvestigationDone::
    setvar VAR_TEMP_0, 1
    end

BurnedTower_B1F_Morty::
lock
    faceplayer
    goto_if_set FLAG_JOHTO_BURNED_TOWER_INVESTIGATED, BurnedTower_B1F_MortyReady
    msgbox BurnedTower_B1F_Text_MortyBefore
    release
    end
BurnedTower_B1F_MortyReady::
    msgbox BurnedTower_B1F_Text_MortyReady
    release
    end

BurnedTower_B1F_Eusine::
msgbox BurnedTower_B1F_Text_Eusine, MSGBOX_NPC
    end
