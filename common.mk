LDSCRIPT := mod.ld
ARCHFLAGS := -target mips -mips2 -mabi=32 -O2 -G0 -mno-abicalls -mno-odd-spreg -mno-check-zero-division \
			 -fomit-frame-pointer -ffast-math -fno-unsafe-math-optimizations -fno-builtin-memset
WARNFLAGS := -Wall -Wextra -Wno-incompatible-library-redeclaration -Wno-unused-parameter -Wno-unknown-pragmas -Wno-unused-variable \
			 -Wno-missing-braces -Wno-unsupported-floating-point-opt -Werror=section
CFLAGS   := $(ARCHFLAGS) $(WARNFLAGS) -D_LANGUAGE_C -nostdinc -ffunction-sections
CPPFLAGS := -DMIPS -DF3DEX_GBI_2 -DF3DEX_GBI_PL -DGBI_DOWHILE \
			-I include -I include/mod -I include/mod/dummy_headers \
			-I include/shared -I mm-decomp/include -I mm-decomp/src -I mm-decomp/extracted/n64-us \
			-I include_in_dependents -I assets_extracted -I assets_extracted/assets -I assets_extracted/assets/assets \
			-idirafter include/libc -idirafter mm-decomp/include/libc
LDFLAGS  := -nostdlib -T $(LDSCRIPT) --unresolved-symbols=ignore-all --emit-relocs -e 0 --no-nmagic -gc-sections \

rwildcard = $(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))
getdirs = $(sort $(dir $(1)))