SilverMountain_Summit_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SilverMountain_Summit_OnTransition
	.byte 0

SilverMountain_Summit_OnTransition::
	special SummitTrainer_Setup
	end

@ Thunder Yellow v0.6.0: the strongest TRAINER stands on the summit and says
@ nothing. After a loss he quietly leaves; he's back the next day. The first
@ win leaves a memorial on the peak.
SilverMountain_Summit_EventScript_Trainer::
	lock
	faceplayer
	msgbox SilverMountain_Summit_Text_Silence
	closemessage
	cleartrainerflag TRAINER_SUMMIT_TRAINER
	trainerbattle_no_intro TRAINER_SUMMIT_TRAINER, SilverMountain_Summit_Text_Silence
	special SummitTrainer_RecordWin
	msgbox SilverMountain_Summit_Text_Silence
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_SUMMIT_TRAINER
	fadescreen FADE_FROM_BLACK
	goto_if_set FLAG_BEAT_SUMMIT_TRAINER, SilverMountain_Summit_EventScript_End
	setflag FLAG_BEAT_SUMMIT_TRAINER
	msgbox SilverMountain_Summit_Text_Footprints
SilverMountain_Summit_EventScript_End::
	release
	end

SilverMountain_Summit_EventScript_Memorial::
	lockall
	goto_if_unset FLAG_BEAT_SUMMIT_TRAINER, SilverMountain_Summit_EventScript_Snow
	msgbox SilverMountain_Summit_Text_Memorial
	releaseall
	end

SilverMountain_Summit_EventScript_Snow::
	msgbox SilverMountain_Summit_Text_JustSnow
	releaseall
	end
