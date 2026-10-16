JohtoCherrygroveAirstrip_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, JohtoCherrygroveAirstrip_OnFrame
	.byte 0

JohtoCherrygroveAirstrip_ReturnClerk::
	lock
	faceplayer
	goto_if_unset FLAG_JOHTO_LEAGUE_CLEARED, JohtoCherrygroveAirstrip_ReturnPrompt
	msgbox JohtoCherrygroveAirstrip_Text_PostLeagueResearch, MSGBOX_DEFAULT
JohtoCherrygroveAirstrip_ReturnPrompt::
msgbox JohtoCherrygroveAirstrip_Text_Return, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, JohtoCherrygroveAirstrip_Cancel
	closemessage
	setvar VAR_0x8004, AIRPLANE_DEST_KANTO
	goto EventScript_TakeAirplane
	end

JohtoCherrygroveAirstrip_Cancel::
	msgbox JohtoCherrygroveAirstrip_Text_Cancel
	release
	end

JohtoCherrygroveAirstrip_Guide::
	msgbox JohtoCherrygroveAirstrip_Text_Guide, MSGBOX_NPC
	end

JohtoCherrygroveAirstrip_Sign::
	msgbox JohtoCherrygroveAirstrip_Text_Sign, MSGBOX_NPC
	end


@ A first-visit research referral. This is not a regional clear condition.
JohtoCherrygroveAirstrip_OnFrame::
	map_script_2 VAR_TEMP_0, 0, JohtoCherrygroveAirstrip_ResearchArrival
	.2byte 0

JohtoCherrygroveAirstrip_ResearchArrival::
	setvar VAR_TEMP_0, 1
	goto_if_set FLAG_JOHTO_ARRIVAL_BRIEFED, JohtoCherrygroveAirstrip_ResearchArrivalDone
	goto_if_set FLAG_JOHTO_MET_LAB_ASSISTANT, JohtoCherrygroveAirstrip_ResearchArrivalRecord
	lockall
	msgbox JohtoCherrygroveAirstrip_Text_ResearchArrival
	releaseall
JohtoCherrygroveAirstrip_ResearchArrivalRecord::
	setflag FLAG_JOHTO_ARRIVAL_BRIEFED
JohtoCherrygroveAirstrip_ResearchArrivalDone::
	end
