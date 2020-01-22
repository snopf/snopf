// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usb_comm.h"
#include "usb_keyboard.h"
#include "usbdrv.h"
#include "io_stuff.h"
#include <string.h>

volatile uint8_t usb_recv_bytes = 0;

// Processes all request from the USB host
usbMsgLen_t usbFunctionSetup(uint8_t data[8])
{
    usbRequest_t *rq = (void*)data;

    if ((rq->bmRequestType & USBRQ_TYPE_MASK) == USBRQ_TYPE_CLASS) {
        // HID class request
        switch (rq->bRequest) {
        case USBRQ_HID_GET_REPORT:
            // Should never happen, but just in case and b/c it's required
            // by the USB HID specs
            usbMsgPtr = (void*)&kb_report;
            return sizeof(kb_report);
        case USBRQ_HID_SET_REPORT:
            // We ignore any LED settings etc.
            return 0;
        case USBRQ_HID_GET_IDLE:
            // Unused, but required by USB HID spec
            usbMsgPtr = (uint8_t*)&kb_idle_rate;
            return 1;
        case USBRQ_HID_SET_IDLE:
            // Unused, but required by USB HID spec
            kb_idle_rate = rq->wValue.bytes[1];
            return 0;
        default:
            return 0;
        }
    }

    else {
        if (rq->wLength.word != USB_MESSAGE_LENGTH) {
            io_failure_shutdown();
        }
        // Vendor specific request, tell host to use usbFunctionWrite to
        // send data by returning USB_NO_MSG
        return USB_NO_MSG;
    }

    // Ignore all other requests
    return 0;
}

// Processes the data sent to us by the host
usbMsgLen_t usbFunctionWrite(uint8_t* data, uint8_t len)
{
    // If the host sends more than 18 bytes something is fishy and we better
    // do nothing at all anymore.
    // Also, if usb_recv_bytes haven't been cleared after the last received
    // message we will shutdown to avoid confusion about password
    // requests and to avoid buffer overflows.
    if ((usb_recv_bytes + len) > USB_MESSAGE_LENGTH) {
        io_failure_shutdown();
    }
    
    // Write all received data from the host to our buffer
    uint8_t* usb_recv_message_p = (uint8_t*)&usb_recv_message;
    memcpy(usb_recv_message_p + usb_recv_bytes, data, len);
    
    usb_recv_bytes += len;

    // Return 1 if we have read all data
    return usb_recv_bytes == USB_MESSAGE_LENGTH;
}
