@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennOrbitalObservatory/map.json
@

	.align 2

HoennOrbitalObservatory_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SCIENTIST, 14, 11, 3, MOVEMENT_TYPE_FACE_LEFT, 0, 0, TRAINER_TYPE_NONE, 0, Space_ObservatoryCrew, 0
	object_event 2, OBJ_EVENT_GFX_MOON_STONE, 12, 6, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_JirachiEncounter, FLAG_HIDE_HOENN_ORBITAL_JIRACHI

HoennOrbitalObservatory_MapWarps:
	warp_def 1, 9, 0, 1, MAP_HOENN_SPACECRAFT_ENGINEERING

HoennOrbitalObservatory_MapBGEvents:
	bg_sign_event 10, 8, 0, BG_EVENT_PLAYER_FACING_ANY, Space_RecordsConsole

HoennOrbitalObservatory_MapEvents::
	map_events HoennOrbitalObservatory_ObjectEvents, HoennOrbitalObservatory_MapWarps, NULL, HoennOrbitalObservatory_MapBGEvents

