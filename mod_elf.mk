# Arguments from environment (set in project.py):
_BUILD_DIR ?= 
_MIPS_CC ?= 
_MIPS_LD ?= 
_ELF_PATH ?= 
_SRC_DIR ?= 
_PY_BUILD_FLAGS ?= 

include ./common.mk

$(info    _BUILD_DIR = $(_BUILD_DIR))
$(info    _MIPS_CC = $(_MIPS_CC))
$(info    _MIPS_LD = $(_MIPS_LD))
$(info    _ELF_PATH = $(_ELF_PATH))
$(info    _SRC_DIR = $(_SRC_DIR))
$(info    _PY_BUILD_FLAGS = $(_PY_BUILD_FLAGS))

C_SRCS := $(call rwildcard,$(_SRC_DIR),*.c)
C_OBJS := $(addprefix $(_BUILD_DIR)/, $(C_SRCS:.c=.o))
C_DEPS := $(addprefix $(_BUILD_DIR)/, $(C_SRCS:.c=.d))

ALL_OBJS := $(C_OBJS)
ALL_DEPS := $(C_DEPS)
BUILD_DIRS := $(call getdirs,$(ALL_OBJS))

$(info    BUILD_DIRS = $(BUILD_DIRS))

all: $(BUILD_DIRS) $(_ELF_PATH)

$(_ELF_PATH): $(ALL_OBJS) $(LDSCRIPT) | $(_BUILD_DIR)
	$(_MIPS_LD) $(ALL_OBJS) $(LDFLAGS) -Map $(_BUILD_DIR)/mod.map -o $@

$(BUILD_DIRS) $(_BUILD_DIR):
ifeq ($(OS),Windows_NT)
	mkdir "$(subst /,\,$@)"
else
	mkdir -p $@
endif

$(C_OBJS): $(_BUILD_DIR)/%.o : %.c | $(BUILD_DIRS)
	$(_MIPS_CC) $(CFLAGS) $(CPPFLAGS) $< -MMD -MF $(@:.o=.d) -c -o $@

clean:
ifeq ($(OS),Windows_NT)
	if exist $(_BUILD_DIR) rmdir /S /Q $(_BUILD_DIR)
else
	rm -rf $(_BUILD_DIR)
endif

-include $(ALL_DEPS)

.PHONY: clean all

# Print target for debugging
print-% : ; $(info $* is a $(flavor $*) variable set to [$($*)]) @true
