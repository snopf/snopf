// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "pw_generator.h"
#include "secret.h"
#include "usb_comm.h"
#include "sha256/sha256.h"
#include "usb_keyboard.h"
#include "io_stuff.h"
#include "z85/z85.h"
#include "usbdrv.h"

#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))

// Absolute maximum password length is len(SHA256 Hash) / 4 * 5
// (conversion from base256 to base85)
#define MAX_PW_LENGTH 40
// We need at least 4 characters to fulfill all password requirements
#define MIN_PW_LENGTH 4

// Working variable for the SHA256 hash result
static uint8_t sha256_hash[32];

// We'll save the status for the fulfilment of the password requirements
// in a single byte, each of the following flags signals whether the current
// password is fulfilling one of the requirements (lower letter,
// capital letter, number, special character)
#define PW_HAS_LOWER 1
#define PW_HAS_CAPITAL 1 << 2
#define PW_HAS_NUMBER 1 << 3
#define PW_HAS_SPECIAL 1 << 4
#define PW_HAS_ALL                                                             \
    (PW_HAS_LOWER | PW_HAS_CAPITAL | PW_HAS_NUMBER | PW_HAS_SPECIAL)

static inline uint8_t check_pw_char(char c, uint8_t pw_ok)
{
    if (('a' <= c) && (c <= 'z')) {
        pw_ok |= PW_HAS_LOWER;
    } else if (('A' <= c) && (c <= 'Z')) {
        pw_ok |= PW_HAS_CAPITAL;
    } else if (('0' <= c) && (c <= '9')) {
        pw_ok |= PW_HAS_NUMBER;
    } else {
        pw_ok |= PW_HAS_SPECIAL;
    }
    return pw_ok;
}

// Processing of a password request, including the typing of the
// result
void pw_process_request(const uint8_t secret[SECRET_LENGTH])
{

#ifndef TEST_PASSWORD_GENERATION_DANGEROUS
    // Wait for user to press button before we do anything
    // DANGER This is currently switched off by the
    // TEST_PASSWORD_GENERATION_DANGEROUS flag to quickly test many generated
    // passwords. This prompt should __never__ be switched of in the released
    // version!
    if (!io_wait_for_user_bttn(10)) {
        return;
    }
#endif

    // We will have to check, if the password we created (Z85 encododed SHA256
    // hash) is fulfilling all password requirements (capital letter,
    // lower letter, number, special character). As soon as this is the case,
    // we will transmit the Z85-encoded SHA256 hash.
    // We'll have to do this "on the fly" since our ram is already pretty much
    // full.
    static char z85_encoded[5];
    uint8_t pw_ok = 0;
    uint8_t num_rehash = 0;
    // Password has to be at least 4 chars long, at max 40
    uint8_t pw_len =
        MIN(MAX_PW_LENGTH, MAX(MIN_PW_LENGTH, usb_recv_message.pw_length));
    if (!usb_recv_message.pw_length) {
        // If the user didn't select a password length we assume
        // the max length of 40
        pw_len = MAX_PW_LENGTH;
    }

    // Add one to the first byte of the received usb message, until the password
    // we generate by hashing the request+secret is fulfilling all requirements
    while (pw_ok != PW_HAS_ALL) {
        usbPoll();
        sha256_calculate_hash(sha256_hash, secret,
                              (uint8_t*)usb_recv_message.request);
        usb_recv_message.request[0] += 1;
        // We assume, that we'll always find a valid password in less
        // than 255 attempts
        if (++num_rehash == 0xFF) {
            io_failure_shutdown();
        }
        pw_ok = 0;

        // Check password character requirements
        uint8_t i = 0;
        while ((i < pw_len) && (pw_ok != PW_HAS_ALL)) {
            usbPoll();
            z85_encode_chunk(z85_encoded, &sha256_hash[i / 5 * 4]);
            uint8_t chunk_size = MIN(pw_len - i, 5);
            i += chunk_size;
            for (uint8_t k = 0; k < chunk_size; k++) {
                pw_ok = check_pw_char(z85_encoded[k], pw_ok);
            }
        }
    }

    // The password is ok, we can send it chunk by chunk now
    uint8_t i = 0;
    while (i < pw_len) {
        usbPoll();
        z85_encode_chunk(z85_encoded, &sha256_hash[i / 5 * 4]);
        uint8_t chunk_size = MIN(pw_len - i, 5);
        i += chunk_size;
        for (uint8_t k = 0; k < chunk_size; k++) {
            kb_send_ascii_char(z85_encoded[k]);
        }
    }

    // Automatically hit enter if requested by host
    if (usb_recv_message.config & PW_HIT_ENTER) {
        kb_send_ascii_char('\n');
    }
}
