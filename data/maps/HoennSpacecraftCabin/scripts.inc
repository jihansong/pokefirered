HoennSpacecraftCabin_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Space_MapTransition
	.byte 0

@ BEGIN PATCH (tools/hoenn_import/patches)
@ Original captain/medic IDs stay1/3. New receipt, not old trainer flag.
Space_CabinCaptain::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto_if_unset FLAG_HOENN_SPACE_INTRUSION_STARTED, Space_CaptainOldVisitor
 goto_if_set FLAG_HOENN_SPACE_CREW_RESCUED, Space_CaptainRescued
 msgbox Space_Text_CaptainAlert
 goto Space_ReturnOffer
Space_CaptainRescued::
 msgbox Space_Text_CaptainRescued
 goto Space_ReturnOffer
Space_CaptainOldVisitor::
 msgbox Space_Text_OldVisitor
 goto Space_ReturnOffer
Space_CabinExit::
 lockall
 goto Space_ReturnOffer
Space_ReturnOffer::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 msgbox Space_Text_Return, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_ReleaseAllEnd
 msgbox Space_Text_SecureSeats
 closemessage
 playse SE_RS_DOOR
 waitse
 setvar VAR_0x8004, 1
 special QuestLog_CutRecording
 fadescreen FADE_TO_BLACK
 special HoennSpaceStory_PlayFlight
 goto_if_eq VAR_RESULT, 0, Space_FlightRejected
 waitstate
 end
@ Old local2 is now a steward; the actual ORBIT battle is in BattleDeck.
Space_FlightCheck::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_LobbyDirections
 release
 end
Space_CabinNoOrder::
 msgbox Space_Text_OldVisitor
 release
 end
Space_Heal::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox Space_Text_Heal, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_HealDecline
 closemessage
 special HealPlayerParty
 playfanfare MUS_HEAL
 waitfanfare
 msgbox Space_Text_Healed
 release
 end
Space_HealDecline::
 msgbox Space_Text_HealDecline
 release
 end
Space_CabinPilot::
 msgbox Space_Text_Pilot, MSGBOX_NPC
 end
Space_CabinAttendant::
 lock
 faceplayer
 goto_if_set FLAG_HOENN_SPACE_CABIN_CLEARED, Space_AttendantSafe
 msgbox Space_Text_AttendantAlert
 release
 end
Space_AttendantSafe::
 msgbox Space_Text_AttendantSafe
 release
 end
Space_CabinPassengerA::
 msgbox Space_Text_PassengerA, MSGBOX_NPC
 end
Space_CabinPassengerB::
 msgbox Space_Text_PassengerB, MSGBOX_NPC
 end

@ Shared facilities use original shop, storage and healing commands.
SpaceFacility_Shop::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_Shop
 pokemart SpaceFacility_ShopStock
 msgbox Text_PleaseComeAgain
 release
 end
 .align 2
SpaceFacility_ShopStock::
 .2byte ITEM_ULTRA_BALL
 .2byte ITEM_FULL_RESTORE
 .2byte ITEM_MAX_POTION
 .2byte ITEM_REVIVE
 .2byte ITEM_ESCAPE_ROPE
 .2byte ITEM_NONE

SpaceFacility_FoodShop::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_FoodShop
 pokemart SpaceFacility_FoodStock
 msgbox Text_PleaseComeAgain
 release
 end
 .align 2
SpaceFacility_FoodStock::
 .2byte ITEM_FRESH_WATER
 .2byte ITEM_SODA_POP
 .2byte ITEM_LEMONADE
 .2byte ITEM_NONE

SpaceFacility_DrinkShop::
 lock
 faceplayer
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 msgbox SpaceFacility_Text_DrinkShop
 pokemart SpaceFacility_FoodStock
 msgbox Text_PleaseComeAgain
 release
 end

SpaceFacility_PC::
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, EventScript_ReleaseEnd
 goto EventScript_PC

SpaceFacility_Rest::
 lockall
 call Space_Guard
 goto_if_eq VAR_RESULT, 0xFFFF, Space_ReleaseAllEnd
 msgbox SpaceFacility_Text_Rest, MSGBOX_YESNO
 goto_if_eq VAR_RESULT, NO, Space_ReleaseAllEnd
 closemessage
 fadescreen FADE_TO_BLACK
 special HealPlayerParty
 playfanfare MUS_HEAL
 waitfanfare
 fadescreen FADE_FROM_BLACK
 msgbox SpaceFacility_Text_Rested
 releaseall
 end

SpaceFacility_DeckSign::
 msgbox SpaceFacility_Text_Decks, MSGBOX_SIGN
 end
@ END PATCH
