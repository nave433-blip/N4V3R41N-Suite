// t8006 pre-return cleanup code
    mov x0, sp          // old stack
    sub sp, sp, 0xA0    // SP as it has to be inside the task routine
    mov x1, sp          // new stack

stack_clear_loop:
    stp xzr, xzr, [x1], #0x10
    cmp x0, x1
    bne stack_clear_loop

    // stack canary
    ldr x1, =0x1801B84B8
    ldr x1, [x1]
    str x1, [sp, #0x18]

    // set LR to expected place in task tramp
    ldr x1, =0x10000AC38
    str x1, [sp, #0x78]

    ldr x1, =0x230100BA8
    str x1, [sp, #0x8]

    ldr x20, =0x230100000
    ldr x21, =0x1801BFE00
    mov w24, #1
    mov w25, #0x40
    mov w28, #0x1F
    mov w26, #0xF
