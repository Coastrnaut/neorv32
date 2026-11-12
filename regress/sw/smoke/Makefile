# NEORV32 regression - smallest program, built for the ISA of each configuration
MARCH ?= rv32i_zicsr_zifencei
EFFORT = -O2
override USER_FLAGS += -Wl,--defsym,__neorv32_rom_size=32k -Wl,--defsym,__neorv32_rom_base=0x00000000
override USER_FLAGS += -Wl,--defsym,__neorv32_ram_size=8k -Wl,--defsym,__neorv32_ram_base=0x80000000
NEORV32_HOME ?= ../../..
include $(NEORV32_HOME)/sw/common/common.mk
