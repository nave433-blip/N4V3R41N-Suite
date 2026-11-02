cmake_minimum_required(VERSION 3.13)

# ====================================================================================

include(pico_sdk_import.cmake)

project(usbliter8 C CXX ASM)

set(CMAKE_BUILD_TYPE MinSizeRel)

SET(BOARD_DEFINITION ${CMAKE_SOURCE_DIR}/boards/${PICO_BOARD}.cmake)

if (NOT EXISTS ${BOARD_DEFINITION})
    SET(BOARD_DEFINITION ${CMAKE_SOURCE_DIR}/boards/unknown.cmake)
endif()

include(${BOARD_DEFINITION} OPTIONAL)

if (NOT DEFINED USBLITER8_ENABLE_SHELL)
    add_compile_definitions(
        WITH_AUTO_MODE=1
    )
endif()

pico_sdk_init()

add_executable(usbliter8
    main.c
    led.c
    bus.c
    usb.c
    exploit.c
)

pico_set_program_name(usbliter8 "usbliter8")
pico_set_program_version(usbliter8 "1.0")

target_compile_definitions(usbliter8 PRIVATE
    PICO_STACK_SIZE=0x1000
    PICO_PRINTF_SUPPORT_EXPONENTIAL=0
    PICO_PRINTF_SUPPORT_FLOAT=0
    PICO_PRINTF_SUPPORT_PTRDIFF_T=0
)

pico_enable_stdio_uart(usbliter8 0)
pico_enable_stdio_usb(usbliter8 1)

add_subdirectory(pio_usb)

target_link_libraries(usbliter8
    pico_stdlib
    pico_status_led
    hardware_pwm
    pio_usb
)

pico_add_extra_outputs(usbliter8)
