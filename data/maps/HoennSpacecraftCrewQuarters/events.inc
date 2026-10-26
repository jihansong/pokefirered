@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftCrewQuarters/map.json
@

	.align 2

HoennSpacecraftCrewQuarters_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SAILOR, 8, 4, 3, MOVEMENT_TYPE_FACE_LEFT, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_CrewSleeper, 0

HoennSpacecraftCrewQuarters_MapWarps:
	warp_def 18, 6, 0, 3, MAP_HOENN_SPACECRAFT_NAVIGATION

HoennSpacecraftCrewQuarters_MapBGEvents:
	bg_sign_event 4, 4, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_Rest

HoennSpacecraftCrewQuarters_MapEvents::
	map_events HoennSpacecraftCrewQuarters_ObjectEvents, HoennSpacecraftCrewQuarters_MapWarps, NULL, HoennSpacecraftCrewQuarters_MapBGEvents

