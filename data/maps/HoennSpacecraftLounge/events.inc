@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftLounge/map.json
@

	.align 2

HoennSpacecraftLounge_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_GENTLEMAN, 9, 3, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_DrinkShop, 0
	object_event 2, OBJ_EVENT_GFX_MAN, 14, 9, 3, MOVEMENT_TYPE_FACE_UP, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_LoungeGuest, 0

HoennSpacecraftLounge_MapWarps:
	warp_def 1, 4, 0, 3, MAP_HOENN_SPACECRAFT_CABIN

HoennSpacecraftLounge_MapEvents::
	map_events HoennSpacecraftLounge_ObjectEvents, HoennSpacecraftLounge_MapWarps, NULL, NULL

