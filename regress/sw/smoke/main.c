// NEORV32 regression - small program for processor configurations with few features.
// It uses no extension beyond what the configuration has and ends by returning from main.
#include <neorv32.h>
#include <string.h>

static volatile uint32_t trap_count;
static uint32_t buffer[16];

static void trap_handler(void) {
  trap_count++;
  neorv32_cpu_csr_write(CSR_MEPC, neorv32_cpu_csr_read(CSR_MEPC) + 4);
}

// jump to an unaligned address: go back to the return address
static void misaligned_handler(void) {
  trap_count++;
  neorv32_cpu_csr_write(CSR_MEPC, neorv32_rte_context_get(1));
}

int main(void) {

  neorv32_rte_setup();
  neorv32_rte_handler_install(TRAP_CODE_MENV_CALL, trap_handler);
  neorv32_rte_handler_install(TRAP_CODE_BREAKPOINT, trap_handler);
  neorv32_rte_handler_install(TRAP_CODE_I_ILLEGAL, trap_handler);
  neorv32_rte_handler_install(TRAP_CODE_I_MISALIGNED, misaligned_handler);

  if (neorv32_uart0_available()) {
    neorv32_uart0_setup(19200, 0, 0);
    neorv32_uart0_printf("smoke start\n");
  }

  // memory: all access sizes
  volatile uint8_t *b = (volatile uint8_t *)buffer;
  volatile uint16_t *h = (volatile uint16_t *)buffer;
  uint32_t sum = 0;
  for (int i = 0; i < 16; i++) {
    buffer[i] = 0x01010101u * (uint32_t)i;
  }
  for (int i = 0; i < 64; i++) {
    sum += b[i];
  }
  for (int i = 0; i < 32; i++) {
    h[i] = (uint16_t)(h[i] ^ 0xa5a5);
    sum ^= h[i];
  }

  // traps
  asm volatile ("ecall");
  asm volatile (".word 0x00000000"); // illegal instruction

  // without compressed instructions, a target at offset 2 traps
  if ((neorv32_cpu_csr_read(CSR_MISA) & (1 << CSR_MISA_C)) == 0) {
    asm volatile ("la   t0, 1f   ;"
                  "addi t0, t0, 2;"
                  "jalr ra, t0, 0;"
                  "1: nop        ;" : : : "t0", "ra");
  }

  // counters and interrupts, when present
  if (neorv32_cpu_csr_read(CSR_MXISA) & (1 << CSR_MXISA_ZICNTR)) {
    sum += neorv32_cpu_csr_read(CSR_CYCLE);
  }
  if (neorv32_gpio_available()) {
    neorv32_gpio_port_set(sum);
  }
  if (neorv32_clint_available()) {
    neorv32_clint_time_set(0);
  }

  if (neorv32_uart0_available()) {
    neorv32_uart0_printf("smoke end %x %u\n", sum, trap_count);
  }
  return 0;
}
