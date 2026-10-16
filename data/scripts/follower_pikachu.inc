EventScript_TalkToFollowerPikachu::
	lock
	faceplayer
	special DoStarterPikachuEmotion
	waitstate
	specialvar VAR_RESULT, CanTalkToMistyFromPikachu
	goto_if_eq VAR_RESULT, FALSE, FollowerPikachu_EventScript_FinishTalk
	msgbox FollowerPikachu_Text_TalkToMisty, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, FollowerPikachu_EventScript_FinishTalk
	specialvar VAR_RESULT, SelectMistyCompanionForTalk
	goto_if_eq VAR_RESULT, FALSE, FollowerPikachu_EventScript_FinishTalk
	goto EventScript_TalkToMistyCompanion

FollowerPikachu_EventScript_FinishTalk::
	release
	end

FollowerPikachu_Text_TalkToMisty::
	.string "Talk to MISTY, too?$"
