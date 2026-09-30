@ v0.11.0 E12: the youngest sister's BERRY, one a game clock day (the WATTSON
@ rematch day, VAR_HOENN_FLOWER_BERRY_DAY), one of Emerald's eight at random.
@ No WAILMER PAIL: FR/LG has no BERRY planting. A full BAG leaves today's BERRY
@ for later the same day.
Route104_PrettyPetalFlowerShop_EventScript_H2::
	lock
	faceplayer
	special FlowerShop_CanGiveBerry
	goto_if_eq VAR_RESULT, FALSE, Route104_PrettyPetalFlowerShop_EventScript_BerryTomorrow
	msgbox Route104_PrettyPetalFlowerShop_Text_H2
	random 8
	addvar VAR_RESULT, ITEM_CHERI_BERRY
	copyvar VAR_0x8008, VAR_RESULT
	giveitem VAR_0x8008
	goto_if_eq VAR_RESULT, FALSE, Route104_PrettyPetalFlowerShop_EventScript_BerryBagFull
	special FlowerShop_RecordBerry
	release
	end

Route104_PrettyPetalFlowerShop_EventScript_BerryTomorrow::
	msgbox Route104_PrettyPetalFlowerShop_Text_BerryTomorrow
	release
	end

Route104_PrettyPetalFlowerShop_EventScript_BerryBagFull::
	msgbox Route104_PrettyPetalFlowerShop_Text_BerryBagFull
	release
	end
