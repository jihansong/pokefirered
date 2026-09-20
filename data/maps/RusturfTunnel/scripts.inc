RusturfTunnel_MapScripts::
	.byte 0

RusturfTunnel_EventScript_HItem88::
	finditem ITEM_POKE_BALL
	end

RusturfTunnel_EventScript_HItem89::
	finditem ITEM_MAX_ETHER
	end

RusturfTunnel_EventScript_H0::
	trainerbattle_single TRAINER_HOENN_MIKE_2, RusturfTunnel_Text_H0_0, RusturfTunnel_Text_H0_1
	msgbox RusturfTunnel_Text_H0_2, MSGBOX_AUTOCLOSE
	end

