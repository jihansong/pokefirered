BlackthornCity_Mart_MapScripts::
    .byte 0

BlackthornCity_Mart_Clerk::
    lock
    faceplayer
    message Text_MayIHelpYou
    waitmessage
    pokemart BlackthornCity_Mart_Items
    msgbox Text_PleaseComeAgain, MSGBOX_DEFAULT
    release
    end
BlackthornCity_Mart_Items:
    .2byte ITEM_ULTRA_BALL
    .2byte ITEM_HYPER_POTION
    .2byte ITEM_FULL_HEAL
    .2byte ITEM_REVIVE
    .2byte ITEM_MAX_REPEL
    .2byte ITEM_NONE
    .align 2
