@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftBattleDeck/map.json
@

	.align 2

HoennSpacecraftBattleDeck_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_COOLTRAINER_M, 12, 7, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, Space_BattleDeckOrbit, FLAG_HOENN_SPACE_CABIN_CLEARED
	object_event 2, OBJ_EVENT_GFX_YOUNGSTER, 18, 8, 3, MOVEMENT_TYPE_FACE_LEFT, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_ArenaSpectator, 0

HoennSpacecraftBattleDeck_MapWarps:
	warp_def 1, 9, 0, 5, MAP_HOENN_SPACECRAFT_CABIN

HoennSpacecraftBattleDeck_MapEvents::
	map_events HoennSpacecraftBattleDeck_ObjectEvents, HoennSpacecraftBattleDeck_MapWarps, NULL, NULL

