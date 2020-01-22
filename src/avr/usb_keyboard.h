// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __usb_keyboard_h__
#define __usb_keyboard_h__

#include <stdint.h>

/*
 * USB keyboard routines, especially for converting ASCII characters
 * to keyboard keycodes and sending them to the host.
 */

// Modifier constants
#define KB_MOD_NONE 0
// Left shift keyboard modifier
#define KB_MOD_SHIFT 1 << 1

// Keypress constants
#define KB_ENTER       0x28
#define KB_ESC         0x29
#define KB_BACKSPACE   0x2a
#define KB_TAB         0x2b
#define KB_SPACE       0x2c
#define KB_MINUS       0x2d
#define KB_EQUAL       0x2e
#define KB_LEFTBRACE   0x2f
#define KB_RIGHTBRACE  0x30
#define KB_BACKSLASH   0x31
#define KB_HASHTILDE   0x32
#define KB_SEMICOLON   0x33
#define KB_APOSTROPHE  0x34
#define KB_GRAVE       0x35
#define KB_COMMA       0x36
#define KB_DOT         0x37
#define KB_SLASH       0x38
#define KB_CAPSLOCK    0x39

// Numbers keycodes
#define KB_1           0x1e
#define KB_2           0x1f
#define KB_3           0x20
#define KB_4           0x21
#define KB_5           0x22
#define KB_6           0x23
#define KB_7           0x24
#define KB_8           0x25
#define KB_9           0x26
#define KB_0           0x27


// Type a single ascii char
void kb_send_ascii_char(char ch);

// Send a null terminated ascii string from program flash
void kb_send_ascii_string_pgm(const char* str);

// Check if the host wants to change the delay in between keys and
// change the delay if necessary
uint8_t kb_check_delay_change(void);

// Keyboard report allowing one simultaneous keypress
struct {
    // Modifier byte (Shift, Alt, etc.)
    uint8_t modifier;
    // Keycode (a, b, etc.)
    uint8_t keycode;
} __attribute__((packed)) kb_report;

// Required by HID standard (in 4 ms values)
extern volatile uint8_t kb_idle_rate;

#endif
