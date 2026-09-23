@ Event 6: the three who keep the SEASHORE HOUSE busy. Beat all three and the
@ man who runs the place pays out in SODA POP. Their own scripts are untouched;
@ this reads their defeated flags (Hoenn trainers keep those in SaveBlock2).
Route109_SeashoreHouse_EventScript_Owner::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_ROUTE109_BROTHERS_DONE, Route109_SeashoreHouse_EventScript_OwnerAfter
	goto_if_not_defeated TRAINER_HOENN_DWAYNE, Route109_SeashoreHouse_EventScript_OwnerWaiting
	goto_if_not_defeated TRAINER_HOENN_SIMON, Route109_SeashoreHouse_EventScript_OwnerWaiting
	goto_if_not_defeated TRAINER_HOENN_JOHANNA, Route109_SeashoreHouse_EventScript_OwnerWaiting
	msgbox Route109_SeashoreHouse_Text_OwnerPrize
	checkitemspace ITEM_SODA_POP, 3
	goto_if_eq VAR_RESULT, FALSE, Route109_SeashoreHouse_EventScript_OwnerNoRoom
	giveitem_msg Route109_SeashoreHouse_Text_ReceivedSodaPop, ITEM_SODA_POP, 3
	setflag FLAG_HOENN_ROUTE109_BROTHERS_DONE
	setvar VAR_HOENN_ROUTE109_BROTHERS, 3
	msgbox Route109_SeashoreHouse_Text_OwnerAfterPrize
	release
	end

Route109_SeashoreHouse_EventScript_OwnerWaiting::
	msgbox Route109_SeashoreHouse_Text_OwnerWaiting
	release
	end

Route109_SeashoreHouse_EventScript_OwnerNoRoom::
	msgbox Route109_SeashoreHouse_Text_OwnerNoRoom
	release
	end

Route109_SeashoreHouse_EventScript_OwnerAfter::
	msgbox Route109_SeashoreHouse_Text_OwnerAfter
	release
	end
