@ Actual HnS pre-unlock tree interaction; unlocked mechanics pending.
TYHns_EventScript_Headbutt::
	lockall
	msgbox TYHns_Text_CantHeadbutt, MSGBOX_DEFAULT
	releaseall
	end

TYHns_Text_CantHeadbutt:
	.string "It's a small tree, but a wild\n"
		.string "POKéMON may be living within.$"
