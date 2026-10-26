JohtoRoute29_MapScripts::
	.byte 0

JohtoRoute29_Hiker::
    lock
    faceplayer
    msgbox JohtoRoute29_Text_Hiker, MSGBOX_DEFAULT
    msgbox JohtoRoute29_Hns_Text_Youngster, MSGBOX_DEFAULT
    release
    end

JohtoRoute29_Sign::
	msgbox JohtoRoute29_Text_Sign, MSGBOX_NPC
	end

JohtoRoute29_EventScript_NorthGateClosed::
	msgbox JohtoRoute29_Text_NorthGateClosed, MSGBOX_SIGN
	end

