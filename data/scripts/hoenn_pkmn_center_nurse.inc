@ Object entrypoint; the common nurse routine returns to its caller.
EventScript_HoennPkmnCenterNurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse
	release
	end
