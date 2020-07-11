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

// Simplified USB HID descriptor for a keyboard with a 2 byte report
// This descriptor is taken from the HID Test program by Christian Starkjohann
const char
    usbHidReportDescriptor[USB_CFG_HID_REPORT_DESCRIPTOR_LENGTH] PROGMEM = {
    0x05, 0x01,                    // USAGE_PAGE (Generic Desktop)
    0x09, 0x06,                    // USAGE (Keyboard)
    0xa1, 0x01,                    // COLLECTION (Application)
    0x05, 0x07,                    //   USAGE_PAGE (Keyboard)
    0x19, 0xe0,                    //   USAGE_MINIMUM (Keyboard LeftControl)
    0x29, 0xe7,                    //   USAGE_MAXIMUM (Keyboard Right GUI)
    0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
    0x25, 0x01,                    //   LOGICAL_MAXIMUM (1)
    0x75, 0x01,                    //   REPORT_SIZE (1)
    0x95, 0x08,                    //   REPORT_COUNT (8)
    0x81, 0x02,                    //   INPUT (Data,Var,Abs)
    0x95, 0x01,                    //   REPORT_COUNT (1)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x81, 0x03,                    //   INPUT (Cnst,Var,Abs)
    0x95, 0x01,                    //   REPORT_COUNT (1)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x15, 0x00,                    //   LOGICAL_MINIMUM (0)
    0x25, 0x65,                    //   LOGICAL_MAXIMUM (101)
    0x05, 0x07,                    //   USAGE_PAGE (Keyboard)
    0x19, 0x00,                    //   USAGE_MINIMUM (Reserved (no event indicated))
    0x29, 0x65,                    //   USAGE_MAXIMUM (Keyboard Application)
    0x81, 0x00,                    //   INPUT (Data,Ary,Abs)
    0x05, 0x07,                    //   USAGE_PAGE (Keyboard)
    0x95, 0x56,                    //   REPORT_COUNT (86)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x09, 0x00,                    //   USAGE (Reserved (no event indicated))
    0xb1, 0x00,                    // FEATURE (Data,Ary,Abs)
    0xc0                           // END_COLLECTION
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

int8_t kb_send_string(uint8_t* keycodes, uint8_t len)
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
