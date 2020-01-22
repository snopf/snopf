// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "secret_change.h"
#include "secret.h"
#include "poll_delay.h"
#include "io_stuff.h"
#include "usb_keyboard.h"
#include "usb_comm.h"
#include "pw_generator.h"
#include "usbdrv.h"

#include <avr/pgmspace.h>

// Secret changing routines

/* Every password change happens in the following order:
 * 1) USB message with config_byte = SECRET_CHANGE_FLAG and a new secret in the
 *      request field
 * 2) The led blinks fast, indicating a secret change to the user
 * 3) The user has 20 seconds to hold the button down for at least 5
 * seconds.
 * If the button wasn't held down, the secret change request is aborted.
 * 4) If the button was successfully pressed, the device types "ready"
 * into the host machine.
 * 5) The host then sends a standard request for a password.
 * 6) The device enters the password using the new secret.
 * 7) If the result is as expected by the host, the host sends an empty
 * Message (every field is zero).
 * 8) The new secret is now the device's secret.
 * 9) If the result was wrong, the host sends a USB message with every
 * bit set. The device now keeps the old secret.
 */

#define CSECRET_STATE_IDLE                              0
#define CSECRET_STATE_WAIT_FOR_USER_RESPONSE            1
#define CSECRET_STATE_WAIT_FOR_CHALLENGE                2
#define CSECRET_STATE_WAIT_FOR_CHALLENGE_RESULT         3

// Current status of the secret changing routine
static uint8_t csecret_state = CSECRET_STATE_IDLE;

// Wait 10 seconds for the user to press the button for five
// seconds and store the new secret in the temporary space if the user
// wants to change the secret
static void inline csecret_wait_for_user(void)
{
    static const PROGMEM char str_ready[] = "ready\n";
    uint8_t num_btt_pressed = 0;
    for (uint8_t i = 0; i < 100; i++) {
        io_bttn_deactivate();
        poll_delay_ms(100);

        io_bttn_activate();
        poll_delay_ms(100);
        
        if (IO_BUTTON_PRESSED) {
            num_btt_pressed += 1;
        }
        else {
            num_btt_pressed = 0;
        }
        
        // we wait 2 * 100 ms, so for 5 seconds we have to have 25 * 2 loop
        // iterations where the button was pressed
        if (num_btt_pressed >= 25) {
            io_bttn_deactivate();
            // Store the sent secret in the temporary eeprom array first
            // and advance one step in the secret changing routine
            for (i = 0; i < SECRET_LENGTH; i++) {
                usbPoll();
                eeprom_update_byte(&ee_tmp_secret[i],
                                   usb_recv_message.request[i]);
            }

            csecret_state = CSECRET_STATE_WAIT_FOR_CHALLENGE;

            kb_send_ascii_string_pgm(str_ready);
            return;
        }
    }

    // User failed to press the button so we will abort the secret changing
    // routine
    io_bttn_deactivate();
    csecret_state = CSECRET_STATE_IDLE;
}

// Check if the host sent us a message full of zeros, indicating that
// the challenge response worked fine. In this case we change our secret
// to the new secret. Else we will abort and indicate a failure.
static void inline csecret_process_challenge_result(void)
{
    uint8_t *p_usb_recv_message = (uint8_t *)&usb_recv_message;
    // Check the answer from the host. If our challenge response was
    // correct, this is indicated by an empty message
    for (uint8_t i = 0; i < USB_MESSAGE_LENGTH; i++) {
        if (p_usb_recv_message[i] != 0) {
            // Something went wrong
            io_failure_shutdown();
        }
    }

    // Everything went well, we write the new secret to the eeprom
    for (uint8_t i = 0; i < SECRET_LENGTH; i++) {
        usbPoll();
        eeprom_update_byte(&ee_secret[i], eeprom_read_byte(&ee_tmp_secret[i]));
    }
    csecret_state = CSECRET_STATE_IDLE;

    // Blink LED four times to indicate success
    for (uint8_t i = 0; i < 4; i++) {
        io_bttn_activate();
        poll_delay_ms(200);
        io_bttn_deactivate();
        poll_delay_ms(200);
    }
}

uint8_t csecret_check_state(void)
{
    if (usb_recv_message.config & SECRET_CHANGE_FLAG) {
        // The host wants to change the secret
        csecret_state = CSECRET_STATE_WAIT_FOR_USER_RESPONSE;
    }

    // Check if we are in the middle of changing the secret
    if (csecret_state > CSECRET_STATE_IDLE) {
        switch (csecret_state) {
        case CSECRET_STATE_WAIT_FOR_USER_RESPONSE:
            csecret_wait_for_user();
            break;
        case CSECRET_STATE_WAIT_FOR_CHALLENGE:
            pw_process_request(ee_tmp_secret);
            csecret_state = CSECRET_STATE_WAIT_FOR_CHALLENGE_RESULT;
            break;
        case CSECRET_STATE_WAIT_FOR_CHALLENGE_RESULT:
            csecret_process_challenge_result();
            break;
        }
        // Return 1 to indicate that we are in the process of changing the
        // secret
        return 1;
    }
    // Return 0 to indicate that we are not in the process of changing the
    // secret
    return 0;
}
