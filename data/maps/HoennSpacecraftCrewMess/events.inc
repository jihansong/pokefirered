@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftCrewMess/map.json
@

	.align 2

HoennSpacecraftCrewMess_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_CHEF, 6, 4, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_Cook, 0

HoennSpacecraftCrewMess_MapWarps:
	warp_def 18, 10, 0, 4, MAP_HOENN_SPACECRAFT_NAVIGATION

HoennSpacecraftCrewMess_MapBGEvents:
	bg_sign_event 8, 10, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_Rest

HoennSpacecraftCrewMess_MapEvents::
	map_events HoennSpacecraftCrewMess_ObjectEvents, HoennSpacecraftCrewMess_MapWarps, NULL, HoennSpacecraftCrewMess_MapBGEvents

