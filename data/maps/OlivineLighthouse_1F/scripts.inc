OlivineLighthouse_1F_MapScripts::
    .byte 0

OlivineLighthouse_1F_Keeper::
    goto_if_set FLAG_JOHTO_AMPHY_CURED, OlivineLighthouse_1F_KeeperRestored
msgbox OlivineLighthouse_1F_Text_Keeper, MSGBOX_NPC
    end
OlivineLighthouse_1F_KeeperRestored::
    msgbox OlivineLighthouse_1F_Text_KeeperRestored, MSGBOX_NPC
    end
