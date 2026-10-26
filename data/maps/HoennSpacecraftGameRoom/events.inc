@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftGameRoom/map.json
@

	.align 2

HoennSpacecraftGameRoom_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_CLERK, 5, 4, 3, MOVEMENT_TYPE_FACE_LEFT, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_GameAttendant, 0

HoennSpacecraftGameRoom_MapWarps:
	warp_def 18, 10, 0, 4, MAP_HOENN_SPACECRAFT_CABIN

HoennSpacecraftGameRoom_MapBGEvents:
	bg_sign_event 10, 4, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_GameMachine

HoennSpacecraftGameRoom_MapEvents::
	map_events HoennSpacecraftGameRoom_ObjectEvents, HoennSpacecraftGameRoom_MapWarps, NULL, HoennSpacecraftGameRoom_MapBGEvents

