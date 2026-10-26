@ Nothing in HOENN is walled off, but the parts the story has not opened yet
@ say so in their own words rather than turning the player around.
SlateportCity_EventScript_NorthRoadNotice::
	msgbox SlateportCity_Text_NorthRoadNotice, MSGBOX_SIGN
	end

SlateportCity_EventScript_BattleTentNotice::
	msgbox SlateportCity_Text_BattleTentNotice, MSGBOX_SIGN
	end

@ The original interview leads into the existing harbor, not a new map.
SlateportCity_VS_Stern::
	lockall
	goto_if_set FLAG_HIDE_HOENN_SLATEPORT_INTERVIEW, SlateportCity_VS_End
	setflag FLAG_HOENN_VILLAIN_CHAPTER_STARTED
	msgbox SlateportCity_VS_Text_Interview
	closemessage
	applymovement 21, SlateportCity_VS_Movement_CrewExit
	applymovement 22, SlateportCity_VS_Movement_CrewExit
	waitmovement 0
	removeobject 21
	removeobject 22
	msgbox SlateportCity_VS_Text_Discovery
	playbgm MUS_ENCOUNTER_AQUA, FALSE
	msgbox SlateportCity_VS_Text_AquaBroadcast
	playse SE_PIN
	applymovement 20, SlateportCity_VS_Movement_Notice
	waitmovement 0
	msgbox SlateportCity_VS_Text_FollowStern
	closemessage
	setflag FLAG_HOENN_HARBOR_INTERVIEW_DONE
	setflag FLAG_HIDE_HOENN_SLATEPORT_INTERVIEW
	removeobject 20
	warp MAP_SLATEPORT_CITY_HARBOR, WARP_ID_NONE, 11, 13
	waitstate
SlateportCity_VS_End::
	releaseall
	end
SlateportCity_VS_Reporter::
	msgbox SlateportCity_VS_Text_Reporter, MSGBOX_NPC
	end
SlateportCity_VS_Cameraman::
	msgbox SlateportCity_VS_Text_Cameraman, MSGBOX_NPC
	end

SlateportCity_VS_Movement_CrewExit:
	walk_down
	walk_down
	step_end

SlateportCity_VS_Movement_Notice:
	emote_exclamation_mark
	delay_16
	face_up
	step_end

@ Preserve the existing visit flag and initialize only this chapter.
SlateportCity_OnTransition::
	setflag FLAG_HOENN_WORLD_MAP_SLATEPORT_CITY
	special HoennVillain_SetupObjects
	end
