@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftCockpit/map.json
@

	.align 2

HoennSpacecraftCockpit_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SAILOR, 8, 5, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_CockpitPilot, 0
	object_event 2, OBJ_EVENT_GFX_SAILOR, 12, 5, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_CockpitPilot, 0

HoennSpacecraftCockpit_MapWarps:
	warp_def 10, 14, 0, 1, MAP_HOENN_SPACECRAFT_NAVIGATION

HoennSpacecraftCockpit_MapEvents::
	map_events HoennSpacecraftCockpit_ObjectEvents, HoennSpacecraftCockpit_MapWarps, NULL, NULL

