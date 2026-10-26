@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftGuestRoom1/map.json
@

	.align 2

HoennSpacecraftGuestRoom1_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_MAN, 5, 6, 3, MOVEMENT_TYPE_FACE_RIGHT, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_Guest1, 0

HoennSpacecraftGuestRoom1_MapWarps:
	warp_def 6, 10, 0, 1, MAP_HOENN_SPACECRAFT_CABIN_CORRIDOR

HoennSpacecraftGuestRoom1_MapBGEvents:
	bg_sign_event 4, 3, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_Rest

HoennSpacecraftGuestRoom1_MapEvents::
	map_events HoennSpacecraftGuestRoom1_ObjectEvents, HoennSpacecraftGuestRoom1_MapWarps, NULL, HoennSpacecraftGuestRoom1_MapBGEvents

