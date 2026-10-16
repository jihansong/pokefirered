# Review-only compiler switch; normal Makefile/header default stays disabled.
include Makefile
ROCKET_TRAINER_HIRES ?= 0
ifneq ($(ROCKET_TRAINER_HIRES),0)
ifneq ($(ROCKET_TRAINER_HIRES),1)
$(error ROCKET_TRAINER_HIRES must be 0 or 1)
endif
endif
$(C_BUILDDIR)/rocket_trainer_portrait.o: CPPFLAGS += -DROCKET_TRAINER_HIRES_ENABLED=$(ROCKET_TRAINER_HIRES)
