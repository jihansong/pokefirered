@ v0.11.0 E12: the MART clerk's sample, a HYPER POTION (Emerald's was a POTION).
@ A full BAG leaves the flag off and the offer open.
OldaleTown_EventScript_H1::
	lock
	faceplayer
	goto_if_set FLAG_HOENN_GOT_OLDALE_POTION, OldaleTown_EventScript_ClerkLater
	msgbox OldaleTown_Text_H1
	giveitem ITEM_HYPER_POTION
	goto_if_eq VAR_RESULT, FALSE, OldaleTown_EventScript_ClerkBagFull
	setflag FLAG_HOENN_GOT_OLDALE_POTION
	msgbox OldaleTown_Text_ClerkAfterGift
	release
	end

OldaleTown_EventScript_ClerkLater::
	msgbox OldaleTown_Text_ClerkLater
	release
	end

OldaleTown_EventScript_ClerkBagFull::
	msgbox OldaleTown_Text_ClerkBagFull
	release
	end
