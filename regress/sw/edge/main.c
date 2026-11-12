// NEORV32 regression - instruction encodings and CSR paths that processor_check does not reach.
// Runs on the full ISA. Every undefined encoding traps and the handler skips it.
#include <neorv32.h>

static volatile uint32_t traps;

static void skip_handler(void) {
  traps++;
  uint32_t pc = neorv32_cpu_csr_read(CSR_MEPC);
  uint32_t insn = neorv32_cpu_csr_read(CSR_MTVAL);
  neorv32_cpu_csr_write(CSR_MEPC, pc + (((insn & 3) == 3) ? 4 : 2));
}

#define WORD(x) asm volatile (".word " #x)

int main(void) {

  neorv32_rte_setup();
  neorv32_rte_handler_install(TRAP_CODE_I_ILLEGAL, skip_handler);
  neorv32_uart0_setup(19200, 0, 0);

  // custom function unit: all four opcodes
  WORD(0x0000000b);
  WORD(0x0000200b);
  WORD(0x0000002b);
  WORD(0x0000102b);
  WORD(0x0000003b);
  WORD(0x0000001b);

  // undefined loads
  WORD(0x00006003);
  WORD(0x00007003);

  // undefined atomic operation
  WORD(0xf800202f);

  // undefined environment instructions
  WORD(0x00300073);
  WORD(0x00400073);
  WORD(0x00600073);
  WORD(0x00700073);

  // may-be-operations, and an encoding next to them that is not one
  WORD(0x81c04073);
  WORD(0x82004073);
  WORD(0xc1c04073);
  WORD(0x00004073);
  WORD(0x80004073);

  // writable mtval
  neorv32_cpu_csr_write(CSR_MTVAL, 0x12345678);
  uint32_t mtval = neorv32_cpu_csr_read(CSR_MTVAL);

  neorv32_uart0_printf("edge end %x %u\n", mtval, traps);
  return 0;
}
