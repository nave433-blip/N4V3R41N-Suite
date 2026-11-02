#include <stdint.h>
#include <stdlib.h>
#include "offsets.h"

#define USB_DIRECTION_MASK  0x80
#define USB_DEVICE2HOST     0x80
#define USB_HOST2DEVICE     0x00

#define EP0_IN  0x80

struct usb_device_request {
    uint8_t  bmRequestType;
    uint8_t  bRequest;
    uint16_t wValue;
    uint16_t wIndex;
    uint16_t wLength;
} __attribute__((packed));

enum {
    DFU_DETACH = 0,
    DFU_DNLOAD,
    DFU_UPLOAD,
    DFU_GETSTATUS,
    DFU_CLR_STATUS,
    DFU_GETSTATE,
    DFU_ABORT,
    CUSTOM_DEMOTE,
    CUSTOM_BOOT
};

static int  (*orig_handle_usb_req)(struct usb_device_request *request, uint8_t **io_buffer) = (void *)HANDLE_USB_REQ;
static void (*platform_demote)() = (void *)PLATFORM_DEMOTE;
static void (*platform_set_remote_boot)() = (void *)PLATFORM_SET_REMOTE_BOOT;

#if WITH_PAC

__attribute__((naked))
uint64_t PACIB(uint64_t ptr, uint64_t ctx) {
    asm("PACIB x0, x1");
    asm("RET");
}

#endif

int custom_handle_usb_req(struct usb_device_request *request, uint8_t **io_buffer) {
    uint8_t bmRequestType = request->bmRequestType;
    uint8_t bRequest      = request->bRequest;

    if ((bmRequestType & USB_DIRECTION_MASK) == USB_HOST2DEVICE) {
        switch (bRequest) {
            case CUSTOM_DEMOTE: {
                platform_demote();
                return 0;
            }

            case CUSTOM_BOOT: {
                platform_set_remote_boot();

                uint64_t ptr = -1;
#if WITH_PAC
                ptr = PACIB(JUMP_AWAY, MAIN_TASK_STACK_LR + 8);
#else
                ptr = JUMP_AWAY;
#endif

                *(volatile uint64_t *)MAIN_TASK_STACK_LR = ptr;
                return 0;
            }
        }

    } else if ((bmRequestType & USB_DIRECTION_MASK) == USB_DEVICE2HOST) {
        /* KBAG decryption folks? */
    }

    /* everything that doesn't fall under the conditions above goes to the original handler */
    return orig_handle_usb_req(request, io_buffer);
}
