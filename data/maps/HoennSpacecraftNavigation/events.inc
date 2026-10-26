@
@ DO NOT MODIFY THIS FILE! It is auto-generated from data/maps/HoennSpacecraftNavigation/map.json
@

	.align 2

HoennSpacecraftNavigation_ObjectEvents:
	object_event 1, OBJ_EVENT_GFX_SCIENTIST, 10, 5, 3, MOVEMENT_TYPE_FACE_DOWN, 0, 0, TRAINER_TYPE_NONE, 0, SpaceFacility_NavigationOfficer, 0

HoennSpacecraftNavigation_MapWarps:
	warp_def 10, 16, 0, 1, MAP_HOENN_SPACECRAFT_CABIN
	warp_def 10, 1, 0, 0, MAP_HOENN_SPACECRAFT_COCKPIT
	warp_def 18, 6, 0, 0, MAP_HOENN_SPACECRAFT_CAPTAINS_OFFICE
	warp_def 1, 6, 0, 0, MAP_HOENN_SPACECRAFT_CREW_QUARTERS
	warp_def 1, 12, 0, 0, MAP_HOENN_SPACECRAFT_CREW_MESS

HoennSpacecraftNavigation_MapBGEvents:
	bg_sign_event 12, 4, 0, BG_EVENT_PLAYER_FACING_ANY, SpaceFacility_NavigationConsole

HoennSpacecraftNavigation_MapEvents::
	map_events HoennSpacecraftNavigation_ObjectEvents, HoennSpacecraftNavigation_MapWarps, NULL, HoennSpacecraftNavigation_MapBGEvents

