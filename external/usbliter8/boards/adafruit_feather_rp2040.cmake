add_compile_definitions(
    BOARD_NAME="Adafruit Feather RP2040"
    PIO_USB_DP_PIN_DEFAULT=12
    LED_NEOPIXEL=1
)

# MinSizeRel breaks usb_task() on RP2040...
set(CMAKE_BUILD_TYPE Release)
