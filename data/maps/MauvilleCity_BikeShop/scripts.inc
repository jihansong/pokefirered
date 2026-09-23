MauvilleCity_BikeShop_MapScripts::
	.byte 0

MauvilleCity_BikeShop_EventScript_H0::
	msgbox MauvilleCity_BikeShop_Text_H0, MSGBOX_NPC
	end

MauvilleCity_BikeShop_EventScript_H1::
	msgbox MauvilleCity_BikeShop_Text_H1, MSGBOX_NPC
	end

MauvilleCity_BikeShop_EventScript_H2::
	msgbox MauvilleCity_BikeShop_Text_H2, MSGBOX_SIGN
	end

MauvilleCity_BikeShop_EventScript_H3::
	msgbox MauvilleCity_BikeShop_Text_H3, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ RYDEL reads the gate's board (event 1) and has something to say about it.
MauvilleCity_BikeShop_EventScript_Rydel::
	lock
	faceplayer
	msgbox MauvilleCity_BikeShop_Text_H0
	special CyclingRoad_GetRecord
	goto_if_eq VAR_RESULT, 0, MauvilleCity_BikeShop_EventScript_NoRecord
	buffernumberstring STR_VAR_1, VAR_RESULT
	goto_if_le VAR_RESULT, 60, MauvilleCity_BikeShop_EventScript_RecordGold
	msgbox MauvilleCity_BikeShop_Text_Record
	release
	end

MauvilleCity_BikeShop_EventScript_RecordGold::
	msgbox MauvilleCity_BikeShop_Text_RecordGold
	release
	end

MauvilleCity_BikeShop_EventScript_NoRecord::
	msgbox MauvilleCity_BikeShop_Text_NoRecord
	release
	end
@ END PATCH
