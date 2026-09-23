@ Event 4: STERN's survey, carried down to the man who reads rock. Emerald had
@ a letter delivered here; the errand is STERN's now, and what comes back is a
@ promise to sail rather than a reply.
GraniteCave_StevensRoom_EventScript_Steven::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_SURVEY_LETTER_DONE, GraniteCave_StevensRoom_EventScript_StevenAfter
	goto_if_unset FLAG_HOENN_SURVEY_LETTER_GOT, GraniteCave_StevensRoom_EventScript_StevenBefore
	msgbox GraniteCave_StevensRoom_Text_StevenErrand
	setflag FLAG_HOENN_SURVEY_LETTER_DONE
	setvar VAR_HOENN_SCENE_GRANITE_CAVE, 1
	setvar VAR_HOENN_STERN_REQUEST, 2
	goto_if_ge VAR_HOENN_STAGE1_PROGRESS, 4, GraniteCave_StevensRoom_EventScript_GiveTM47
	setvar VAR_HOENN_STAGE1_PROGRESS, 4
	goto GraniteCave_StevensRoom_EventScript_GiveTM47
	end

GraniteCave_StevensRoom_EventScript_GiveTM47::
	msgbox GraniteCave_StevensRoom_Text_StevenTakeThis
	checkitemspace ITEM_TM47
	goto_if_eq VAR_RESULT, FALSE, GraniteCave_StevensRoom_EventScript_NoRoomForTM47
	giveitem_msg GraniteCave_StevensRoom_Text_ReceivedTM47, ITEM_TM47
	setflag FLAG_HOENN_GOT_TM47_IN_CAVE
	msgbox GraniteCave_StevensRoom_Text_ExplainTM47
	release
	end

GraniteCave_StevensRoom_EventScript_NoRoomForTM47::
	msgbox GraniteCave_StevensRoom_Text_NoRoomForTM47
	release
	end

GraniteCave_StevensRoom_EventScript_StevenBefore::
	msgbox GraniteCave_StevensRoom_Text_StevenBefore
	release
	end

GraniteCave_StevensRoom_EventScript_StevenAfter::
	goto_if_unset FLAG_HOENN_GOT_TM47_IN_CAVE, GraniteCave_StevensRoom_EventScript_GiveTM47
	msgbox GraniteCave_StevensRoom_Text_StevenAfter
	release
	end
