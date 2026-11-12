// NEORV32 regression - lets the watchdog reset the processor, then ends after the reset.
#include <neorv32.h>

int main(void) {

  neorv32_uart0_setup(19200, 0, 0);
  uint32_t cause = neorv32_wdt_get_cause();
  neorv32_uart0_printf("wdt reset cause %u\n", cause);
  if (cause == 2) { // second run: this reset came from the watchdog
    return 0;
  }
  neorv32_wdt_setup(1, 0); // 1 tick timeout, not locked, no debug-mode pause
  while (1) {
    asm volatile ("nop");
  }
  return 0;
}
