// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usb_keyboard.h"
#include "usbdrv.h"
#include "usb_comm.h"
#include "poll_delay.h"
#include "io_stuff.h"
#include <avr/pgmspace.h>
#include <avr/eeprom.h>

// Required by USB HID standard
volatile uint8_t kb_idle_rate = 0;

// Value for delay between key presses to avoid bugs in some host side programs
// e.g. KDE Konsole
uint8_t EEMEM kb_delay_ms = 20;

// Simplified USB HID descriptor for a keyboard with a 2 byte report
// This descriptor is taken from the HID Test program by Christian Starkjohann
const char
    usbHidReportDescriptor[USB_CFG_HID_REPORT_DESCRIPTOR_LENGTH] PROGMEM = {
        /* USB report descriptor */
        0x05, 0x01, // USAGE_PAGE (Generic Desktop)
        0x09, 0x06, // USAGE (Keyboard)
        0xa1, 0x01, // COLLECTION (Application)
        0x05, 0x07, //   USAGE_PAGE (Keyboard)
        0x19, 0xe0, //   USAGE_MINIMUM (Keyboard LeftControl)
        0x29, 0xe7, //   USAGE_MAXIMUM (Keyboard Right GUI)
        0x15, 0x00, //   LOGICAL_MINIMUM (0)
        0x25, 0x01, //   LOGICAL_MAXIMUM (1)
        0x75, 0x01, //   REPORT_SIZE (1)
        0x95, 0x08, //   REPORT_COUNT (8)
        0x81, 0x02, //   INPUT (Data,Var,Abs)
        0x95, 0x01, //   REPORT_COUNT (1)
        0x75, 0x08, //   REPORT_SIZE (8)
        0x25, 0x65, //   LOGICAL_MAXIMUM (101)
        0x19, 0x00, //   USAGE_MINIMUM (Reserved (no event indicated))
        0x29, 0x65, //   USAGE_MAXIMUM (Keyboard Application)
        0x81, 0x00, //   INPUT (Data,Ary,Abs)
        0xc0        // END_COLLECTION
};

#define NUM_SPECIAL_CHARS 23

// Special characters used by Z85 Encoding
static const char ascii_special_chars[NUM_SPECIAL_CHARS + 1] PROGMEM = {
    ".-:+"
    "=^!/"
    "*?&<"
    ">()["
    "]{}@"
    "%$#"};

// Maps the HID keycodes to the ascii characters
static const uint8_t kb_special_chars_map[NUM_SPECIAL_CHARS] PROGMEM = {
    KB_DOT, KB_MINUS, KB_SEMICOLON,  KB_EQUAL,
    KB_EQUAL, KB_6, KB_1, KB_SLASH, 
    KB_8, KB_SLASH, KB_7, KB_COMMA,
    KB_DOT, KB_9, KB_0, KB_LEFTBRACE,
    KB_RIGHTBRACE, KB_LEFTBRACE, KB_RIGHTBRACE, KB_2,
    KB_5, KB_4, KB_3
};

// Maps the HID key modifiers to the ascii characters
static const uint8_t kb_special_chars_kmods[NUM_SPECIAL_CHARS] PROGMEM = {
    KB_MOD_NONE, KB_MOD_NONE ,KB_MOD_SHIFT, KB_MOD_SHIFT,
    KB_MOD_NONE, KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_NONE,
    KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_SHIFT,
    KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_NONE,
    KB_MOD_NONE, KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_SHIFT,
    KB_MOD_SHIFT, KB_MOD_SHIFT, KB_MOD_SHIFT
};

// We'll have to wait for the USB host to be ready to receive the next
// key press from us
static inline void wait_for_usb_interrupt_ready(void)
{
    while (!usbInterruptIsReady()) {
        usbPoll();
    }
}

// Send the current report buffer to the host and send the release key signal
// afterwards
static inline void kb_send_report(uint8_t modifier, uint8_t keycode)
{
    wait_for_usb_interrupt_ready();
    kb_report.modifier = modifier;
    kb_report.keycode = keycode;
    poll_delay_ms((uint16_t)eeprom_read_byte(&kb_delay_ms));
    usbSetInterrupt((void*)&kb_report, sizeof(kb_report));
    // Always send the release key signal
    wait_for_usb_interrupt_ready();
    kb_report.modifier = KB_MOD_NONE;
    kb_report.keycode = 0;
    poll_delay_ms((uint16_t)eeprom_read_byte(&kb_delay_ms));
    usbSetInterrupt((void*)&kb_report, sizeof(kb_report));
}

void kb_send_ascii_char(char ch)
{
    uint8_t modifier = KB_MOD_NONE;
    uint8_t keycode = 0;

    // Check character type and change value to according USB keyboard keycode
    // Numbers and letters are sorted in ascending order in both systems
    // so we normally just have to apply an offset to transform from ASCII
    // to HID keycode
    if ((ch >= 'A') && (ch <= 'Z')) {
        // Set shift modifier and modify character value to lower letter
        keycode = ch - 0x3d;
        modifier = KB_MOD_SHIFT;
    } else if ((ch >= 'a') && (ch <= 'z')) {
        keycode = ch - 0x5d;
    } else if ((ch >= '0') && (ch <= '9')) {
        if (ch == '0') {
            // ASCII sorts the numbers from 0..9, HID keycodes are sorted from
            // 9..0 so we have to give special treatment to the '0' character
            keycode = 0x27;
        } else {
            keycode = ch - 0x13;
        }
    } else if (ch == '\n') {
        keycode = KB_ENTER;
    }
    else {
        // Special character from the Z85 set, these are not in any particular
        // order
        for (uint8_t i = 0; i < NUM_SPECIAL_CHARS; i++) {
            if ((pgm_read_byte(&(ascii_special_chars[i]))) == ch) {
                modifier = pgm_read_byte(&(kb_special_chars_kmods[i]));
                keycode = pgm_read_byte(&(kb_special_chars_map[i]));
                break;
            }
        }
    }

    kb_send_report(modifier, keycode);
}

void kb_send_ascii_string_pgm(const char* str)
{
    uint8_t i = 0;
    while (pgm_read_byte(&str[i]) != '\0') {
        kb_send_ascii_char(pgm_read_byte(&str[i++]));
    }
}

uint8_t kb_check_delay_change(void)
{
    static const char msg_set[] PROGMEM = "DELAYSET";
    if (usb_recv_message.config & KB_DELAY_CHANGE_FLAG) {
        // We wait for the user to press the button to make sure that
        // the user wants to change the keyboard delay
        if (io_wait_for_user_bttn(10)) {
            // The password length field is used for setting the delay in ms
            eeprom_update_byte(&kb_delay_ms, usb_recv_message.pw_length);
            kb_send_ascii_string_pgm(msg_set);
        }

        // Return 1 if this was a delay change message
        return 1;
    }
    // Return 0 if this wasn't a delay change message
    return 0;
}
