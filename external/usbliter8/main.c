#include <pico/stdio.h>
#include <pico/time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hardware/clocks.h"
#include "hardware/watchdog.h"
#include "led.h"
#include "pico/stdlib.h"
#include "pico/bootrom.h"

#include "bus.h"
#include "exploit.h"
#include "usb.h"
#include "log.h"

#if WITH_AUTO_MODE

#define WITH_AUTO_REBOOT            (0)
#define FAILURE_REBOOT_DELAY_SEC    (3)
#define SUCCESS_REBOOT_DELAY_SEC    (5)

#define CONNECTION_FAIL_SLEEP_MS    (500)

__attribute__((noreturn))
void fatal_failure(void) {
    led_set_state(LED_STATE_ERROR);

#if WITH_AUTO_REBOOT
    printf("\nfatal failure, rebooting in %d seconds\n", FAILURE_REBOOT_DELAY_SEC);

    sleep_ms(FAILURE_REBOOT_DELAY_SEC * 1000);

    watchdog_reboot(0, SRAM_END, 1);
    while (1) {}

#else
    printf("\nfatal failure, spinning forever\n");

    while (1) {
        sleep_ms(100);
    }
#endif
}

__attribute__((noreturn))
void do_auto(void) {
    while (true) {
        int ret = exploit_run();

        /*
         * This case means not even device descriptor
         * could be queried
         *
         * On those boards with redundant resistor
         * it could mean that device was not even
         * connected yet
         *
         * So we sleep a bit, reset the bus and try again
         *
         * UPDATE: same behavior for already PWNED devices
         */
        if (ret == -2) {
            sleep_ms(CONNECTION_FAIL_SLEEP_MS);
            usb_bus_reset_open_ep0();
            continue;
        }

        /* no-go failure, bailing */
        if (ret != 0) {
            fatal_failure();
        }

        /* it all went well then */
        break;
    }

#if WITH_AUTO_REBOOT
    printf("\nsuccess, rebooting in %d seconds\n", SUCCESS_REBOOT_DELAY_SEC);

    sleep_ms(SUCCESS_REBOOT_DELAY_SEC * 1000);

    watchdog_reboot(0, SRAM_END, 1);
    while (1) {}
#else
    printf("\nsuccess, spinning forever\n");

    while (1) {
        sleep_ms(100);
    }
#endif
}

#else

static void help(void) {
    printf("'e'\texploit\n");
    printf("'r'\tbus reset\n");
    printf("'p'\treboot\n");
    printf("'h'\thelp\n");
}

void do_shell(void) {
    char buf[2] = { 0 };

    printf("\nDEBUG build, starting command prompt\n");

    printf("\n");
    help();
    printf("\n");

    while (1) {
        printf("> ");

        char c = stdio_getchar();

        printf("%c\n", c);

        switch (c) {
            case 'r': {
                printf("Resetting the bus...\n");
                usb_bus_reset_open_ep0();
                break;
            }

            case 'e': {
                usb_bus_reset_open_ep0();
                int ret = exploit_run();

                if (ret == -2) {
                    printf("failed to discover a device\n");
                }

                break;
            }

            case 'p': {
                printf("Rebooting the Pico...\n");

                sleep_ms(100);
                watchdog_reboot(0, SRAM_END, 1);
                while (1) {}
            }

            case 'h': {
                help();
                break;
            }

            default: {
                printf("Unknown command '%s'\n", buf);
                break;
            }
        }
    }
}

#endif

int main(void) {
    // PIO USB needs sys_clk to be a multiple of 12 MHz
#if PICO_RP2350
    set_sys_clock_khz(156000, true);
#elif PICO_RP2040
    set_sys_clock_khz(120000, true);
#else
#error What is this MCU even?
#endif

    led_init();
    led_set_state(LED_STATE_BOOTING);

    stdio_init_all();

    // this delay being long enough, seems to have
    // a HUGE impact on the exploit reliability
    sleep_ms(2000);

    led_set_state(LED_STATE_IDLE);

    printf("\n============ %s v%s ============\n", PICO_PROGRAM_NAME, PICO_PROGRAM_VERSION_STRING);
    printf("built for %s, PIO USB @ GP%d/%d (D+/D-)\n\n", BOARD_NAME, PIO_USB_DP_PIN_DEFAULT, PIO_USB_DP_PIN_DEFAULT + 1);

#if PICO_RP2040
    printf("==========================================================\n");
    printf("WARNING: RP2040 reliability is not the best in many cases,\n");
    printf("you shall better switch to RP2350\n");
    printf("==========================================================\n");
    printf("\n");
#endif

    usb_start();
    usb_bus_init();
    usb_bus_wait_for_device();
    usb_bus_reset_open_ep0();

#if WITH_AUTO_MODE
    do_auto();
#else
    do_shell();
#endif
}
