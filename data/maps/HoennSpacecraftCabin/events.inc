@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftCabin/map.json
@

	.align 2

HoennSpacecraftCabin_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST, 10, 5, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_CabinCaptain, 0
	object_event 2, OBJ_EVENT_GFX_MAN, 6, 8, 3, MOVEMENT_TYPE_FACE_RIGHT, 0, 0, TRAINER_TYPE_NONE, 0, Space_FlightCheck, 0
	object_event 3, OBJ_EVENT_GFX_NURSE, 14, 8, 3, MOVEMENT_TYPE_FACE_LEFT, 0, 0, TRAINER_TYPE_NONE, 0, Space_Heal, 0
	object_event 4, OBJ_EVENT_GFX_SAILOR, 12, 5, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_CabinPilot, 0
	object_event 5, OBJ_EVENT_GFX_CABLE_CLUB_RECEPTIONIST, 7, 10, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_CabinAttendant, 0
	object_event 6, OBJ_EVENT_GFX_MAN, 4, 9, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_CabinPassengerA, 0
	object_event 7, OBJ_EVENT_GFX_WOMAN_1, 14, 12, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_CabinPassengerB, 0
	object_event 8, OBJ_EVENT_GFX_CLERK, 5, 4, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_Shop, 0

HoennSpacecraftCabin_MapWarps:
	warp_def 18, 7, 0, 0, MAP_HOENN_SPACECRAFT_ENGINEERING
	warp_def 10, 1, 0, 0, MAP_HOENN_SPACECRAFT_NAVIGATION
	warp_def 1, 6, 0, 0, MAP_HOENN_SPACECRAFT_FOOD_COURT
	warp_def 18, 4, 0, 0, MAP_HOENN_SPACECRAFT_LOUNGE
	warp_def 1, 10, 0, 0, MAP_HOENN_SPACECRAFT_GAME_ROOM
	warp_def 18, 11, 0, 0, MAP_HOENN_SPACECRAFT_BATTLE_DECK
	warp_def 4, 14, 0, 0, MAP_HOENN_SPACECRAFT_CABIN_CORRIDOR

HoennSpacecraftCabin_MapCoordEvents:
	coord_event 10, 14, 0, VAR_TEMP_0, 0, Space_CabinExit

HoennSpacecraftCabin_MapBGEvents:
	bg_sign_event 3, 4, 0, BG_EVENT_PLAYER_FACING_NORTH, SpaceFacility_PC

HoennSpacecraftCabin_MapEvents::
	map_events HoennSpacecraftCabin_ObjectEvents, HoennSpacecraftCabin_MapWarps, HoennSpacecraftCabin_MapCoordEvents, HoennSpacecraftCabin_MapBGEvents

