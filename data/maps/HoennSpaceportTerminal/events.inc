@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpaceportTerminal/map.json
@

	.align 2

HoennSpaceportTerminal_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SCIENTIST, 8, 6, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_TerminalClerk, 0
	object_event 2, OBJ_EVENT_GFX_WOMAN_2, 16, 7, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_TerminalSafety, 0
	object_event 3, OBJ_EVENT_GFX_SAILOR, 8, 12, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_TerminalCrew, 0

HoennSpaceportTerminal_MapWarps:
	warp_def 12, 16, 0, 3, MAP_MOSSDEEP_CITY_SPACE_CENTER_1F
	warp_def 12, 1, 0, 0, MAP_HOENN_SPACEPORT_LAUNCH_PAD

HoennSpaceportTerminal_MapEvents::
	map_events HoennSpaceportTerminal_ObjectEvents, HoennSpaceportTerminal_MapWarps, NULL, NULL

