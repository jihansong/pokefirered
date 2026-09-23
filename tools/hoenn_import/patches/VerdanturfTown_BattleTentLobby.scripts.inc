@ The tent never opens in this story; the man who signed up for it gives away
@ what he bought for it instead.
VerdanturfTown_BattleTentLobby_EventScript_TMGiver::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_TM17_AT_TENT, VerdanturfTown_BattleTentLobby_EventScript_TMGiven
	msgbox VerdanturfTown_BattleTentLobby_Text_H1
	checkitemspace ITEM_TM17
	goto_if_eq VAR_RESULT, FALSE, VerdanturfTown_BattleTentLobby_EventScript_NoRoom
	giveitem_msg VerdanturfTown_BattleTentLobby_Text_ReceivedTM17, ITEM_TM17
	setflag FLAG_HOENN_GOT_TM17_AT_TENT
	msgbox VerdanturfTown_BattleTentLobby_Text_H1b
	release
	end

VerdanturfTown_BattleTentLobby_EventScript_NoRoom::
	msgbox VerdanturfTown_BattleTentLobby_Text_NoRoom
	release
	end

VerdanturfTown_BattleTentLobby_EventScript_TMGiven::
	msgbox VerdanturfTown_BattleTentLobby_Text_H1b
	release
	end
