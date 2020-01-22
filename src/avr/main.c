// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usbdrv.h"
#include "usb_comm.h"
#include "secret_change.h"
#include "secret.h"
#include "io_stuff.h"
#include "pw_generator.h"
#include "usb_keyboard.h"

#include <avr/interrupt.h>
#include <util/delay.h>


int main(void)
{
    usbInit();
    io_bttn_deactivate();
    // enforce re-enumeration
    usbDeviceDisconnect();
    _delay_ms(500);
    usbDeviceConnect();

    sei();

    while (1) {
        usbPoll();
        // We check for a new usb message of defined length in each
        // iteration
        // If we have received a new message we check first, whether it's
        // a special message for secret changing or a system setting message
        // Only if that's not the case we assume the message to be a standard
        // password request
        if (usb_recv_bytes == USB_MESSAGE_LENGTH) {
            // First check if we are currently in the process of changing the
            // tokens secret
            if (!csecret_check_state()){
                // If not, check if the host wants to change the keyboard press
                // delay setting
                if (!kb_check_delay_change()) {
                    // If that's not the case we can continue with processing
                    // a regular password request
                    pw_process_request(ee_secret);
                }
            }
            // Clear the received bytes to allow the start of a new transmission
            usb_recv_bytes = 0;
        }
    }
    return 0;
}
