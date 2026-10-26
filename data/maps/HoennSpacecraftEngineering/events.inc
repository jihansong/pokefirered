@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftEngineering/map.json
@

	.align 2

HoennSpacecraftEngineering_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SCIENTIST, 10, 7, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_SystemsCheck, FLAG_HOENN_SPACE_ENGINEERING_CLEARED
	object_event 2, OBJ_EVENT_GFX_SCIENTIST, 5, 4, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_EngineeringCrew, 0

HoennSpacecraftEngineering_MapWarps:
	warp_def 1, 7, 0, 0, MAP_HOENN_SPACECRAFT_CABIN
	warp_def 18, 7, 0, 0, MAP_HOENN_ORBITAL_OBSERVATORY
	warp_def 10, 1, 0, 0, MAP_HOENN_SPACECRAFT_CARGO_HOLD

HoennSpacecraftEngineering_MapBGEvents:
	bg_sign_event 12, 4, 0, BG_EVENT_PLAYER_FACING_ANY, Space_EngineeringConsole

HoennSpacecraftEngineering_MapEvents::
	map_events HoennSpacecraftEngineering_ObjectEvents, HoennSpacecraftEngineering_MapWarps, NULL, HoennSpacecraftEngineering_MapBGEvents

