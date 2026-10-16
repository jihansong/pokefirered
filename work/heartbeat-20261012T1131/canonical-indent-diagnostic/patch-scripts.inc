Route114_EventScript_H5::
lock
faceplayer
goto_if_set FLAG_HOENN_ROUTE114_TM05_RECEIVED, Route114_EventScript_H5_Received
msgbox Route114_Text_H5, MSGBOX_DEFAULT
giveitem ITEM_TM05, 1
goto_if_eq VAR_RESULT, FALSE, Route114_EventScript_H5_NoRoom
setflag FLAG_HOENN_ROUTE114_TM05_RECEIVED
Route114_EventScript_H5_Received::
msgbox Route114_Text_H5Roar, MSGBOX_DEFAULT
release
end

Route114_EventScript_H5_NoRoom::
msgbox Route114_Text_H5NoRoom, MSGBOX_DEFAULT
release
end

Route114_EventScript_H6::
	msgbox Route114_Text_H6, MSGBOX_NPC
	end
