GraniteCave_1F_MapScripts::
	.byte 0

@ TY_HOENN_SHARED_HM_STORY_V1
GraniteCave_1F_EventScript_H0::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD, GraniteCave_1F_TYSharedHM_Done
	goto_if_set FLAG_GOT_HM05, GraniteCave_1F_TYSharedHM_Known
	checkitem ITEM_HM05
	goto_if_eq VAR_RESULT, TRUE, GraniteCave_1F_TYSharedHM_Known
	checkpcitem ITEM_HM05
	goto_if_eq VAR_RESULT, TRUE, GraniteCave_1F_TYSharedHM_Known
	msgbox GraniteCave_1F_TYSharedHM_FreshText
	checkitemspace ITEM_HM05
	goto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full
	giveitem ITEM_HM05
	goto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full
	setflag FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD
	msgbox GraniteCave_1F_TYSharedHM_FreshThanks
	release
	end

GraniteCave_1F_TYSharedHM_Known::
	msgbox GraniteCave_1F_TYSharedHM_KnownText
	checkitemspace ITEM_TM29
	goto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full
	giveitem ITEM_TM29
	goto_if_eq VAR_RESULT, FALSE, GraniteCave_1F_TYSharedHM_Full
	setflag FLAG_HOENN_GOT_GRANITE_SHARED_HM_REWARD
	msgbox GraniteCave_1F_TYSharedHM_TechniqueText
	release
	end

GraniteCave_1F_TYSharedHM_Full::
	msgbox GraniteCave_1F_TYSharedHM_FullText
	release
	end

GraniteCave_1F_TYSharedHM_Done::
	msgbox GraniteCave_1F_TYSharedHM_DoneText
	release
	end

GraniteCave_1F_EventScript_HItem90::
	finditem ITEM_ESCAPE_ROPE
	end
