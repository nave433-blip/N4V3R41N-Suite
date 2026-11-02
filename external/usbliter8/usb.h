#pragma once

#include "bus.h"

void usb_start(void);
int  usb_bus_init(void);
int  usb_bus_wait_for_device(void);
int  usb_bus_reset_open_ep0(void);

typedef int (*usb_executee_t)(bus_t *b, void *ctx);

int usb_bus_execute(usb_executee_t func, void *ctx, uint64_t timeout);
