@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftFoodCourt/map.json
@

	.align 2

HoennSpacecraftFoodCourt_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_CLERK, 5, 4, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_FoodShop, 0
	object_event 2, OBJ_EVENT_GFX_WOMAN_1, 14, 10, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_FoodGuest, 0

HoennSpacecraftFoodCourt_MapWarps:
	warp_def 18, 6, 0, 2, MAP_HOENN_SPACECRAFT_CABIN

HoennSpacecraftFoodCourt_MapEvents::
	map_events HoennSpacecraftFoodCourt_ObjectEvents, HoennSpacecraftFoodCourt_MapWarps, NULL, NULL

