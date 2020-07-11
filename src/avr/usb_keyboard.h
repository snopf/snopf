// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#ifndef __usb_keyboard_h__
#define __usb_keyboard_h__

#include <stdint.h>

// USB keyboard hid report, key modifier and key code
struct KeyboardReport {
    uint8_t modifier;
    uint8_t reserved;
    uint8_t keycode;
} __attribute__((packed));

extern struct KeyboardReport kb_report;

// Send string to host
int8_t kb_send_string(uint8_t* key_indices, uint8_t len);

// Hit enter
void kb_hit_enter(void);

// Required by HID standard (in 4 ms values)
extern volatile uint8_t kb_idle_rate;

#endif
