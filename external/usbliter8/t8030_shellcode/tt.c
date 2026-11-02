#include <stdint.h>
#include "offsets.h"

static inline
uint64_t l3_pte_make_exec(uint64_t p) {
    return (0x6E7) | (p & ~0x3FFF);
}

static inline
uint64_t l3_pte_make_data(uint64_t p) {
    return (0x60000000000667) | (p & ~0x3FFF);
}

static inline
uint64_t l3_pte_make_io(uint64_t p) {
    return (0x60000000000469) | (p & ~0x3FFF);
}

static inline
uint64_t l3_tte_make(uint64_t p) {
    return (p & ~0x3FFF) | 0b11;
}

static inline
uint64_t l1_off(uint64_t p) {
    return p / L1_PAGE_SIZE;
}

__attribute__((section("__TEXT,__tramp")))
void tt_make(void) {
    uint64_t *ttbr = (void *)TTBR_BASE;

    uint64_t t;

    /* ROM */
    t = ROM_PTE_BASE;
    for (int p = 0; p < ROM_SIZE / PAGE_SIZE; p++) {
        uint64_t *ptep = (uint64_t *)t + p;
        *ptep = l3_pte_make_exec(ROM_NEW_PA + p * PAGE_SIZE);
    }

    *(ttbr + l1_off(ROM_BASE)) = l3_tte_make(t);

    /* SRAM */
    *(ttbr + l1_off(SRAM_BASE)) = l3_pte_make_io(SRAM_BASE);

    /* IO */
    t = IO_BASE;
    for (int p = 0; p < 62; p++) {
        *(ttbr + l1_off(IO_BASE) + p) = l3_pte_make_io(t + p * L1_PAGE_SIZE);
    }
}
