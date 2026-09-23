AbandonedShip_CaptainsOffice_MapScripts::
	.byte 0

AbandonedShip_CaptainsOffice_EventScript_H0::
	msgbox AbandonedShip_CaptainsOffice_Text_H0, MSGBOX_NPC
	end

AbandonedShip_CaptainsOffice_EventScript_HItem131::
	finditem ITEM_STORAGE_KEY
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Event 5: the SCANNER that went down with the ship. STERN wants it back.
AbandonedShip_CaptainsOffice_EventScript_Scanner::
	finditem ITEM_SCANNER
	end
@ END PATCH
