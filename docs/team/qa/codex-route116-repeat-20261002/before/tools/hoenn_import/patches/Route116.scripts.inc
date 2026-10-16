@ MR. BRINEY waits beside the entrance while PEEKO is missing. His existing
@ shared hide flag moves him back to his cottage and boat after the rescue.
Route116_OnTransition::
	special HoennZ3_SetupObjects
	end

Route116_EventScript_BrineyPeekoMissing::
	lock
	faceplayer
	msgbox Route116_Text_BrineyPeekoMissing
	release
	end
