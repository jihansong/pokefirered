AzaleaTown_Mart_MapScripts::
    .byte 0


AzaleaTown_Mart_Clerk::
    goto_if_questlog EventScript_ReleaseEnd
    lock
    faceplayer
    message Text_MayIHelpYou
    waitmessage
    pokemart AzaleaTown_Mart_Items
    msgbox Text_PleaseComeAgain
    release
    end

    .align 2
AzaleaTown_Mart_Items::
    .2byte ITEM_POKE_BALL
    .2byte ITEM_GREAT_BALL
    .2byte ITEM_SUPER_POTION
    .2byte ITEM_ANTIDOTE
    .2byte ITEM_PARALYZE_HEAL
    .2byte ITEM_AWAKENING
    .2byte ITEM_REPEL
    .2byte ITEM_NONE

AzaleaTown_Mart_Customer::
    msgbox AzaleaTown_Mart_Text_Customer, MSGBOX_NPC
    end

AzaleaTown_Mart_Traveler::
    msgbox AzaleaTown_Mart_Text_Traveler, MSGBOX_NPC
    end

