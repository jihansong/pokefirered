VerdanturfTown_BattleTentLobby_MapScripts::
	.byte 0

VerdanturfTown_BattleTentLobby_EventScript_H0::
	msgbox VerdanturfTown_BattleTentLobby_Text_H0, MSGBOX_NPC
	end

VerdanturfTown_BattleTentLobby_EventScript_H1::
	msgbox VerdanturfTown_BattleTentLobby_Text_H1, MSGBOX_NPC
	end

VerdanturfTown_BattleTentLobby_EventScript_H2::
	msgbox VerdanturfTown_BattleTentLobby_Text_H2, MSGBOX_NPC
	end

VerdanturfTown_BattleTentLobby_EventScript_H3::
	msgbox VerdanturfTown_BattleTentLobby_Text_H3, MSGBOX_NPC
	end

VerdanturfTown_BattleTentLobby_EventScript_H4::
	msgbox VerdanturfTown_BattleTentLobby_Text_H4, MSGBOX_NPC
	end

VerdanturfTown_BattleTentLobby_EventScript_H5::
	msgbox VerdanturfTown_BattleTentLobby_Text_H5, MSGBOX_SIGN
	end

@ BEGIN PATCH (tools/hoenn_import/patches)
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
@ END PATCH
