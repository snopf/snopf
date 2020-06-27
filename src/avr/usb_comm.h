// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __usb_comm_h__
#define __usb_comm_h__

#include <stdint.h>
#include "usbdrv.h"

// Length of every USB message
// Messages that are shorter must be padded
#define USB_MSG_LENGTH 86

// Buffer for all incoming USB messages
extern volatile uint8_t usb_msg_buffer[USB_MSG_LENGTH];

// Number of bytes we have received so far
extern volatile uint8_t usb_recv_bytes;

// None Request, for resetting USB processing status
#define USB_MSG_FLAG_NONE   0x00

// Regular password request
#define USB_MSG_FLAG_REQUEST    (1 << 0)
struct USB_REQUEST{
    uint8_t msg_type;
    // Actual 16 byte request message
    uint8_t request_msg[16];
    // Requested Password length
    uint8_t length;
    // Password rules
    uint8_t rules;
    // Up to three keycodes to append to the password
    // Values above 63 are ignored
    uint8_t appendix[3];
    // Keymap for mapping the base 64 password to actual keycodes
    uint8_t keymap[64];
} __attribute__((packed));

// Read existing keyboard keys from eeprom request
#define USB_MSG_FLAG_KEYBOARD_READ    (1 << 1)
struct UBS_READ_KEYBOARD{
    uint8_t msg_type;
    // Index of first key to read
    uint8_t begin;
    // Number of keycodes to read, maximum number is 43 (USB_MSG_LENGTH / 2)
    // because we have two bytes for each key (modifier + keycode) and we
    // store the data in the usb_msg_buffer
    uint8_t num;
} __attribute__((packed));

// Read keyboard idle rate from eeprom request
#define USB_MSG_FLAG_KB_DELAY_READ  (1 << 2)

// Write to EEPROM
#define USB_MSG_FLAG_WRITE_EEPROM_UNPROTECTED   (1 << 3)
#define USB_MSG_FLAG_WRITE_EEPROM_PROTECTED     (1 << 4)

#define USB_EEPROM_PAYLOAD_SIZE 82
struct USB_WRITE_EEPROM{
    uint8_t msg_type;
    // EEPROM start address
    uint16_t begin;
    // Number of bytes of payload that are actually used
    uint8_t len;
    // Up to 82 bytes of data
    uint8_t payload[USB_EEPROM_PAYLOAD_SIZE];
} __attribute__((packed));

// Process a completed USB message
// Return 1 if the message could be processed, else 0
int8_t usb_comm_process_message(void);

#endif  //__usb_comm_h__
