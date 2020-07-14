// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usb_keyboard.h"
#include "usbdrv.h"
#include "usb_comm.h"
#include "poll_delay.h"
#include "eeprom_access.h"

#include <avr/pgmspace.h>

struct KeyboardReport kb_report = {
    .modifier = 0,
    .reserved = 0,
    .keycode = 0
};

// Required by USB HID standard
volatile uint8_t kb_idle_rate = 0;

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
static inline void kb_send_report(void)
{
    wait_for_usb_interrupt_ready();
    poll_delay_ms((uint16_t)eeprom_read_byte(&eeprom_layout.kb_delay));
    usbSetInterrupt((void*)&kb_report, sizeof(kb_report));
    // Always send the release key signal
    wait_for_usb_interrupt_ready();
    kb_report.modifier = 0;
    kb_report.keycode = 0;
    poll_delay_ms((uint16_t)eeprom_read_byte(&eeprom_layout.kb_delay));
    usbSetInterrupt((void*)&kb_report, sizeof(kb_report));
}

int8_t kb_send_string(const uint8_t* keycodes, uint8_t len)
{
    for (uint8_t i = 0; i < len; i++) {
        if (!(ee_access_get_key_modifier(keycodes[i], &kb_report.modifier))) {
            return 0;
        }
        if (!(ee_access_get_key_code(keycodes[i], &kb_report.keycode))) {
            return 0;
        }
        kb_send_report();
    }
    return 1;
}

void kb_hit_enter(void)
{
    kb_report.modifier = 0;
    kb_report.keycode = 0x28;
    kb_send_report();
}

int8_t kb_send_password(const uint8_t* password, uint8_t len, const uint8_t* appendix,
                        uint8_t hit_enter)
{
    int8_t success = kb_send_string(password, len);
    
    // Send appendix if requested by user, values above 63 signal 'no appendix'
    for (uint8_t i = 0; i < 3; i++) {
        if (appendix[i] >= 64) {
            break;
        }
        if (success) {
            success = kb_send_string((appendix) + i, 1);
        }
    }
    
    if (success) {
        if (hit_enter) {
            kb_hit_enter();
        }
    }
    
    return success;
}
