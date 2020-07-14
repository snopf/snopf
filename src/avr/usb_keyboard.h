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

// Type password into host device
int8_t kb_send_password(const uint8_t* password, uint8_t len, const uint8_t* appendix,
                        uint8_t hit_enter);

// Required by HID standard (in 4 ms values)
extern volatile uint8_t kb_idle_rate;

#endif
