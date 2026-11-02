add_compile_definitions(
    BOARD_NAME="Raspberry Pi Pico"
    PIO_USB_DP_PIN_DEFAULT=12
    # Seems to break reliability even further, IDK
    # LED_SINGLE_COLOR=1
    # LED_PIN=PICO_DEFAULT_LED_PIN
)

# MinSizeRel breaks usb_task() on RP2040...
set(CMAKE_BUILD_TYPE Release)
