HoennSpacecraftGameRoom_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
SpaceFacility_GameAttendant::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 checkitem ITEM_COIN_CASE
 goto_if_eq VAR_RESULT, TRUE, SpaceFacility_GameBuy
 msgbox SpaceFacility_Text_GameCase
 checkitemspace ITEM_COIN_CASE, 1
 goto_if_eq VAR_RESULT, FALSE, SpaceFacility_GameCaseFull
 giveitem ITEM_COIN_CASE
 goto_if_eq VAR_RESULT, FALSE, SpaceFacility_GameCaseFull
 setflag FLAG_GOT_COIN_CASE
SpaceFacility_GameBuy::
 msgbox SpaceFacility_Text_GameWelcome, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, EventScript_ReleaseEnd
 checkcoins VAR_TEMP_1
 goto_if_ge VAR_TEMP_1, (MAX_COINS + 1) - 50, SpaceFacility_GameCoinsFull
 checkmoney 1000
 goto_if_eq VAR_RESULT, FALSE, SpaceFacility_GameMoney
 addcoins 50
 removemoney 1000
 playse SE_SHOP
 waitse
 msgbox SpaceFacility_Text_GameBought
 release
 end
SpaceFacility_GameCaseFull::
 msgbox SpaceFacility_Text_GameCaseFull
 release
 end
SpaceFacility_GameCoinsFull::
 msgbox SpaceFacility_Text_GameCoinsFull
 release
 end
SpaceFacility_GameMoney::
 msgbox SpaceFacility_Text_GameMoney
 release
 end
SpaceFacility_GameMachine::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 checkitem ITEM_COIN_CASE
 goto_if_eq VAR_RESULT, FALSE, SpaceFacility_GameNoCase
 checkcoins VAR_TEMP_1
 goto_if_eq VAR_TEMP_1, 0, SpaceFacility_GameNoCoins
 msgbox SpaceFacility_Text_GamePlay, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_ReleaseAllEnd
 closemessage
 special QuestLog_CutRecording
 playslotmachine 0
 releaseall
 end
SpaceFacility_GameNoCase::
 msgbox SpaceFacility_Text_GameNoCase
 releaseall
 end
SpaceFacility_GameNoCoins::
 msgbox SpaceFacility_Text_GameNoCoins
 releaseall
 end
@ END PATCH
