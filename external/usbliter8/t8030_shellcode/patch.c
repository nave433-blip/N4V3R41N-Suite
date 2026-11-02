#include <stdint.h>
#include "offsets.h"

extern void *tramp;
extern void *restore_rom_table;
extern void *add_pwnd_hook;

#define SET32(_addr, _val) \
    *(volatile uint32_t *)(_addr) = _val;

#define SET64(_addr, _val) \
    *(volatile uint64_t *)(_addr) = _val;

#define NOP (0xd503201f)

static
uint32_t arm64_assemble_bl(uint64_t src, uint64_t dst) {
    return ((0b100101 << 26) | (((dst - src) / 4) & 0x3FFFFFF));
}

static
uint64_t tramp_func_off(void *func) {
    uint64_t shc_off = func - (void *)&tramp;
    return ROM_BASE + ROM_SIZE + shc_off + TRAMP_OFF;
}

void rom_patchup(void) {
    /* load area size tweak */
    SET32(ROM_NEW_PA + 0x7454, 0x10000060); // adr x0, 0xc
    SET32(ROM_NEW_PA + 0x7458, 0xb9400000); // ldr w0, [x0]
    SET32(ROM_NEW_PA + 0x745c, 0xd65f03c0); // ret
    SET32(ROM_NEW_PA + 0x7460, LOAD_AREA_SIZE);

    /* keep ROM remap */
    SET32(ROM_NEW_PA + 0x7550, arm64_assemble_bl(ROM_BASE + 0x7550, tramp_func_off(&restore_rom_table)));

    /* force DFU */
    SET32(ROM_NEW_PA + 0x79A4, 0x52800020); // mov w0, 1

    /* add PWND USB SN string */
    SET32(ROM_NEW_PA + 0x68D4, arm64_assemble_bl(ROM_BASE + 0x68D4, tramp_func_off(&add_pwnd_hook)));

    /* custom handler */
    SET64(ROM_NEW_PA + 0x29078, ROM_BASE + ROM_SIZE + HANDLER_OFF);
}
