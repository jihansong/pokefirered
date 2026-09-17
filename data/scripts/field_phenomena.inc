@ Stepping into a cloud of cave dust from a field phenomenon
EventScript_FieldPhenomenonDustItem::
	lockall
	msgbox Text_FieldPhenomenonDust
	finditem ITEM_RARE_CANDY
	releaseall
	end

Text_FieldPhenomenonDust::
	.string "Something was glinting in the\n"
	.string "swirling dust!$"
