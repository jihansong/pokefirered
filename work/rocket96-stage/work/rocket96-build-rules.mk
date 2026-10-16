# Native 96x96 Rocket candidate uses four-OAM order, not generic PNG tile order.
ROCKET96_PYTHON ?= python3
ROCKET96_SOURCE := graphics/trainers/front_pics/jessie_james_hires.png
ROCKET96_ENCODER := tools/rocket96_encode.py

graphics/trainers/front_pics/jessie_james_hires.4bpp: $(ROCKET96_SOURCE) $(ROCKET96_ENCODER)
	$(ROCKET96_PYTHON) $(ROCKET96_ENCODER) $< --kind tiles --output $@

graphics/trainers/palettes/jessie_james_hires.gbapal: $(ROCKET96_SOURCE) $(ROCKET96_ENCODER)
	$(ROCKET96_PYTHON) $(ROCKET96_ENCODER) $< --kind palette --output $@
