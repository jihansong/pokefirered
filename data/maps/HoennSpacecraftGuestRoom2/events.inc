@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftGuestRoom2/map.json
@

	.align 2

HoennSpacecraftGuestRoom2_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_WOMAN_1, 8, 7, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_Guest2, 0

HoennSpacecraftGuestRoom2_MapWarps:
	warp_def 6, 10, 0, 2, MAP_HOENN_SPACECRAFT_CABIN_CORRIDOR

HoennSpacecraftGuestRoom2_MapBGEvents:
	bg_sign_event 4, 4, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_Rest

HoennSpacecraftGuestRoom2_MapEvents::
	map_events HoennSpacecraftGuestRoom2_ObjectEvents, HoennSpacecraftGuestRoom2_MapWarps, NULL, HoennSpacecraftGuestRoom2_MapBGEvents

