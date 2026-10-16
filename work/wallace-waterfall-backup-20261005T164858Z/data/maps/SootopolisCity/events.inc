@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/SootopolisCity/map.json
@

	.align 2

SootopolisCity_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_OLD_MAN_2, 31, 18, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_H0, 0
	object_event 2, OBJ_EVENT_GFX_LASS, 9, 43, 3, MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT, 1, 0, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_H1, 0
	object_event 3, OBJ_EVENT_GFX_NINJA_BOY, 51, 14, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_H2, 0
	object_event 4, OBJ_EVENT_GFX_LITTLE_BOY, 43, 26, 3, MOVEMENT_TYPE_LOOK_AROUND, 0, 0, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_H3, 0
	object_event 5, OBJ_EVENT_GFX_WOMAN_3, 49, 34, 3, MOVEMENT_TYPE_WANDER_UP_AND_DOWN, 1, 1, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_H4, 0
	object_event 6, OBJ_EVENT_GFX_WALLACE, 28, 33, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SootopolisCity_EventScript_TY_Wallace, 0

SootopolisCity_MapWarps:
	warp_def 43, 31, 0, 0, MAP_SOOTOPOLIS_CITY_POKEMON_CENTER_1F
	warp_def 17, 29, 0, 0, MAP_SOOTOPOLIS_CITY_MART
	warp_def 31, 32, 0, 0, MAP_SOOTOPOLIS_CITY_GYM_1F
	warp_def 31, 16, 3, 0, MAP_CAVE_OF_ORIGIN_ENTRANCE
	warp_def 9, 6, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE1
	warp_def 45, 6, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE2
	warp_def 9, 17, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE3
	warp_def 44, 17, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE4
	warp_def 9, 26, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE5
	warp_def 53, 28, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE6
	warp_def 8, 35, 0, 0, MAP_SOOTOPOLIS_CITY_HOUSE7
	warp_def 48, 25, 0, 0, MAP_SOOTOPOLIS_CITY_LOTAD_AND_SEEDOT_HOUSE
	warp_def 51, 36, 0, 0, MAP_SOOTOPOLIS_CITY_MYSTERY_EVENTS_HOUSE_1F

SootopolisCity_MapBGEvents:
	bg_sign_event 33, 34, 3, BG_EVENT_PLAYER_FACING_ANY, SootopolisCity_EventScript_H5
	bg_sign_event 41, 37, 0, BG_EVENT_PLAYER_FACING_ANY, SootopolisCity_EventScript_H6

SootopolisCity_MapEvents::
	map_events SootopolisCity_ObjectEvents, SootopolisCity_MapWarps, NULL, SootopolisCity_MapBGEvents

