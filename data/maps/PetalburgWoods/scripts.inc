PetalburgWoods_MapScripts::
	.byte 0

PetalburgWoods_EventScript_HItem94::
	finditem ITEM_GREAT_BALL
	end

PetalburgWoods_EventScript_HItem95::
	finditem ITEM_X_ATTACK
	end

PetalburgWoods_EventScript_HItem96::
	finditem ITEM_ETHER
	end

PetalburgWoods_EventScript_H0::
	msgbox PetalburgWoods_Text_H0, MSGBOX_NPC
	end

PetalburgWoods_EventScript_H1::
	trainerbattle_single TRAINER_HOENN_LYLE, PetalburgWoods_Text_H1_0, PetalburgWoods_Text_H1_1
	msgbox PetalburgWoods_Text_H1_2, MSGBOX_AUTOCLOSE
	end

PetalburgWoods_EventScript_H2::
	trainerbattle_single TRAINER_HOENN_JAMES_1, PetalburgWoods_Text_H2_0, PetalburgWoods_Text_H2_1
	msgbox PetalburgWoods_Text_H2_2, MSGBOX_AUTOCLOSE
	end

PetalburgWoods_EventScript_H3::
	msgbox PetalburgWoods_Text_H3, MSGBOX_NPC
	end

PetalburgWoods_EventScript_HItem97::
	finditem ITEM_PARALYZE_HEAL
	end

PetalburgWoods_EventScript_H4::
	msgbox PetalburgWoods_Text_H4, MSGBOX_NPC
	end

PetalburgWoods_EventScript_H5::
	msgbox PetalburgWoods_Text_H5, MSGBOX_SIGN
	end

PetalburgWoods_EventScript_H6::
	msgbox PetalburgWoods_Text_H6, MSGBOX_SIGN
	end

