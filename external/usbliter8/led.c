#include <stdio.h>
#include "pico/time.h"
#include "led.h"

#if LED_NEOPIXEL

#include "pico/status_led.h"

#if LED_RED_GREEN_SWAPPED
#define NEOPIXEL_RGB(r, g, b) \
    ((g << 16) | (r << 8) | (b))

#else
#define NEOPIXEL_RGB(r, g, b) \
    ((g << 8) | (r << 16) | (b))
#endif

#define DISABLED    NEOPIXEL_RGB(0, 0, 0)
#define GREEN       NEOPIXEL_RGB(1, 18, 2)
#define BLUE        NEOPIXEL_RGB(0, 10, 18)
#define AMBER       NEOPIXEL_RGB(18, 2, 0)
#define RED         NEOPIXEL_RGB(24, 0, 0)

extern void set_ws2812(uint32_t value);

void led_switch_color(uint32_t color) {
    set_ws2812(color);
}

void led_init(void) {
    status_led_init();
}

#elif LED_RGB_PWM

#include "hardware/gpio.h"
#include "hardware/pwm.h"

#define PWM_WRAP    (256)
#define PWM_RGB(r, g, b) \
    ((r << 16) | (g << 8) | b)

#define DISABLED    PWM_RGB(0, 0, 0)
#define GREEN       PWM_RGB(10, 150, 50)
#define BLUE        PWM_RGB(0, 30, 120)
#define AMBER       PWM_RGB(170, 24, 0)
#define RED         PWM_RGB(120, 0, 0)

static struct {
    uint r_slice;
    uint r_chan;
    uint g_slice;
    uint g_chan;
    uint b_slice;
    uint b_chan;
} pwm_ctx = { 0 };

void led_switch_color(uint32_t color) {
    pwm_set_chan_level(pwm_ctx.r_slice, pwm_ctx.r_chan, (color >> 16) & 0xFF);
    pwm_set_chan_level(pwm_ctx.g_slice, pwm_ctx.g_chan, (color >> 8)  & 0xFF);
    pwm_set_chan_level(pwm_ctx.b_slice, pwm_ctx.b_chan, (color >> 0)  & 0xFF);
}

void led_init(void) {
    int r_pin = LED_RGB_RED_PIN, g_pin = LED_RGB_GREEN_PIN, b_pin = LED_RGB_BLUE_PIN;

    gpio_set_function(r_pin, GPIO_FUNC_PWM);
    gpio_set_function(g_pin, GPIO_FUNC_PWM);
    gpio_set_function(b_pin, GPIO_FUNC_PWM);

    pwm_ctx.r_slice = pwm_gpio_to_slice_num(r_pin);
    pwm_ctx.r_chan = pwm_gpio_to_channel(r_pin);

    pwm_ctx.g_slice = pwm_gpio_to_slice_num(g_pin);
    pwm_ctx.g_chan = pwm_gpio_to_channel(g_pin);

    pwm_ctx.b_slice = pwm_gpio_to_slice_num(b_pin);
    pwm_ctx.b_chan = pwm_gpio_to_channel(b_pin);

    pwm_set_wrap(pwm_ctx.r_slice, PWM_WRAP);
    pwm_set_wrap(pwm_ctx.g_slice, PWM_WRAP);
    pwm_set_wrap(pwm_ctx.b_slice, PWM_WRAP);

    pwm_set_chan_level(pwm_ctx.r_slice, pwm_ctx.r_chan, PWM_WRAP);
    pwm_set_chan_level(pwm_ctx.g_slice, pwm_ctx.g_chan, PWM_WRAP);
    pwm_set_chan_level(pwm_ctx.b_slice, pwm_ctx.b_chan, PWM_WRAP);

#if LED_RGB_ACTIVE_LOW
    // I hate this API
    pwm_set_output_polarity(pwm_ctx.r_slice, true, true);
    pwm_set_output_polarity(pwm_ctx.g_slice, true, true);
    pwm_set_output_polarity(pwm_ctx.b_slice, true, true);
#endif

    pwm_set_enabled(pwm_ctx.r_slice, true);
    pwm_set_enabled(pwm_ctx.g_slice, true);
    pwm_set_enabled(pwm_ctx.b_slice, true);
}

#elif LED_SINGLE_COLOR

#include "hardware/pwm.h"
#include "hardware/gpio.h"

#define PWM_WRAP    (768)

static struct {
    uint slice;
    uint chan;

    repeating_timer_t timer;
    bool blink_en;
    bool blink_curr_state;

    repeating_timer_t breathing_timer;
    uint breathing_level;
    bool breathing_falling;
} led_ctx = { 0 };

void led_init(void) {
    gpio_set_function(LED_PIN, GPIO_FUNC_PWM);

    led_ctx.slice = pwm_gpio_to_slice_num(LED_PIN);
    led_ctx.chan = pwm_gpio_to_channel(LED_PIN);

    pwm_set_wrap(led_ctx.slice, PWM_WRAP);
    pwm_set_chan_level(led_ctx.slice, led_ctx.chan, PWM_WRAP);
    pwm_set_enabled(led_ctx.slice, true);
}

#define ENABLED     (PWM_WRAP - 1)
#define DISABLED    (0)

void led_toggle(uint on) {
    pwm_set_chan_level(led_ctx.slice, led_ctx.chan, on);
}

bool _led_timer_cb(__unused repeating_timer_t *rt) {
    led_toggle(led_ctx.blink_curr_state ? ENABLED : DISABLED);
    led_ctx.blink_curr_state = !led_ctx.blink_curr_state;

    return true;
}

void led_set_blinking(uint64_t period_ms) {
    if (led_ctx.blink_en) {
        cancel_repeating_timer(&led_ctx.timer);
    }

    if (period_ms) {
        add_repeating_timer_ms(period_ms, _led_timer_cb, NULL, &led_ctx.timer);
        led_ctx.blink_en = true;
    } else {
        led_toggle(false);
        led_ctx.blink_en = false;
    }
}

bool _led_breathing_timer_cb(__unused repeating_timer_t *rt) {
    if (!led_ctx.breathing_falling) {
        led_ctx.breathing_level++;

        if (led_ctx.breathing_level == ENABLED) {
            led_ctx.breathing_falling = true;
        }
    } else {
        led_ctx.breathing_level--;

        if (led_ctx.breathing_level == 0) {
            led_ctx.breathing_falling = false;
        }
    }

    pwm_set_chan_level(led_ctx.slice, led_ctx.chan, led_ctx.breathing_level);

    return true;
}

void led_set_breathing(bool on) {
    if (on) {
        led_set_blinking(0);
        add_repeating_timer_ms(2, _led_breathing_timer_cb, NULL, &led_ctx.breathing_timer);
    } else {
        cancel_repeating_timer(&led_ctx.breathing_timer);
        led_toggle(DISABLED);
    }
}

#endif

#if LED_NEOPIXEL || LED_RGB_PWM

static struct {
    uint32_t color;
    repeating_timer_t timer;
    bool blink_en;
    bool blink_curr_state;
} led_ctx = { 0 };

void led_set_color(uint32_t color) {
    led_ctx.color = color;
    led_switch_color(color);
}

bool _led_timer_cb(__unused repeating_timer_t *rt) {
    uint32_t color = 0;

    if (led_ctx.blink_curr_state) {
        color = led_ctx.color;
    } else {
        color = DISABLED;
    }

    led_switch_color(color);

    led_ctx.blink_curr_state = !led_ctx.blink_curr_state;

    return true;
}

void led_set_blinking(uint64_t period_ms) {
    if (led_ctx.blink_en) {
        cancel_repeating_timer(&led_ctx.timer);
    }

    if (period_ms) {
        add_repeating_timer_ms(period_ms, _led_timer_cb, NULL, &led_ctx.timer);
        led_ctx.blink_en = true;
    } else {
        led_switch_color(led_ctx.color);
        led_ctx.blink_en = false;
    }
}

void led_set_state(int state) {
    switch (state) {
        case LED_STATE_BOOTING: {
            led_set_color(AMBER);
            led_set_blinking(200);
            break;
        }

        case LED_STATE_IDLE: {
            led_set_color(AMBER);
            led_set_blinking(0);
            break;
        }

        case LED_STATE_RUNNING: {
            led_set_color(BLUE);
            // blinking here breaks reliability, IDK
            led_set_blinking(0);
            break;
        }

        case LED_STATE_SUCCESS: {
            led_set_color(GREEN);
            led_set_blinking(0);
            break;
        }

        case LED_STATE_ERROR: {
            led_set_color(RED);
            led_set_blinking(0);
            break;
        }
    }
}

#elif LED_SINGLE_COLOR

void led_set_state(int state) {
    switch (state) {
        case LED_STATE_BOOTING: {
            led_set_blinking(200);
            break;
        }

        case LED_STATE_IDLE: {
            led_set_breathing(true);
            break;
        }

        case LED_STATE_RUNNING: {
            led_set_breathing(false);
            led_set_blinking(100);
            break;
        }

        case LED_STATE_SUCCESS: {
            led_set_blinking(0);
            led_toggle(ENABLED);
            break;
        }

        case LED_STATE_ERROR: {
            led_set_blinking(0);
            led_toggle(DISABLED);
            break;
        }
    }
}

#else

void led_init(void) {
}

void led_set_state(int state) {
}

#endif
