@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftCargoHold/map.json
@

	.align 2

HoennSpacecraftCargoHold_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SCIENTIST, 12, 5, 3, MOVEMENT_TYPE_FACE_UP, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_CargoResearcher, 0

HoennSpacecraftCargoHold_MapWarps:
	warp_def 12, 16, 0, 2, MAP_HOENN_SPACECRAFT_ENGINEERING

HoennSpacecraftCargoHold_MapBGEvents:
	bg_sign_event 6, 5, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_CargoClue

HoennSpacecraftCargoHold_MapEvents::
	map_events HoennSpacecraftCargoHold_ObjectEvents, HoennSpacecraftCargoHold_MapWarps, NULL, HoennSpacecraftCargoHold_MapBGEvents

