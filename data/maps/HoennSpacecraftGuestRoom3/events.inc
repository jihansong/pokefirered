@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftGuestRoom3/map.json
@

	.align 2

HoennSpacecraftGuestRoom3_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_OLD_MAN_1, 8, 7, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_Guest3, 0

HoennSpacecraftGuestRoom3_MapWarps:
	warp_def 6, 10, 0, 3, MAP_HOENN_SPACECRAFT_CABIN_CORRIDOR

HoennSpacecraftGuestRoom3_MapBGEvents:
	bg_sign_event 4, 4, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_Rest

HoennSpacecraftGuestRoom3_MapEvents::
	map_events HoennSpacecraftGuestRoom3_ObjectEvents, HoennSpacecraftGuestRoom3_MapWarps, NULL, HoennSpacecraftGuestRoom3_MapBGEvents

