// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __usb_comm_h__
#define __usb_comm_h__

#include <stdint.h>

// Managing of the buffer for received USB messages

// Every message we accept from the host has to be 18 bytes long.
// First byte is the config byte, second byte is the maximum password
// length. The 16 bytes after that are the password request.
#define USB_MESSAGE_LENGTH 18

// Flags to be used in the message's config byte
// These flags are not combinable and override each other from MSB to LSB

// Automatically send "Enter" keycode after typing in the password
#define PW_HIT_ENTER 1

// Change the keyboards delay between keypresses
#define KB_DELAY_CHANGE_FLAG 1 << 6

// Start a secret changing routine
#define SECRET_CHANGE_FLAG 1 << 7

// Buffer for the received message from the host
struct {
    // Config byte, possible flags are defined above
    uint8_t config;
    // Maximum password length. If this is set to 0, we send the full 40
    // character password. The maximum password length must be at least 4
    // if it's not set to zero (one capital letter, one lower letter, one
    // number, one special character == 4 characters)
    uint8_t pw_length;
    // First 16 bytes of the SHA256 hash of the website etc. we want to login
    // into plus a personal pin.
    // Example:
    // request = SHA256("reddit.com"+"1234")[:16]
    uint8_t request[16];
} __attribute__((packed)) volatile usb_recv_message;


// Length of received data in bytes
// This variable is also used as a flag for newly received data and a lock.
// As long as usb_recv_bytes == USB_MESSAGE_LENGTH,
// no new messages will be processed.
// usb_recv_bytes has to be set to zero everytime we are done with
// processing a message if we want to read new data.
extern volatile uint8_t usb_recv_bytes;

#endif
