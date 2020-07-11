// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usbdrv.h"
#include "usb_comm.h"
#include "io_stuff.h"
#include <avr/interrupt.h>
#include <util/delay.h>
#include <string.h>
#include "io_stuff.h"

int main(void)
{
    usbInit();
    io_init();
    // enforce re-enumeration
    usbDeviceDisconnect();
    _delay_ms(500);
    usbDeviceConnect();

    sei();

    while (1) {
        usbPoll();
        // Wait for a completed USB message
        if (usb_recv_bytes == USB_MSG_LENGTH) {
            if (!(usb_comm_process_message())) {
                // Clear buffer and go into shutdown mode
                memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
                io_failure_shutdown();
            }
            // Get ready for accepting new messages
            usb_recv_bytes = 0;
        }
    }
    return 0;
}
