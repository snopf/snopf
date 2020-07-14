// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usb_comm.h"
#include "usb_keyboard.h"
#include "usbdrv.h"
#include "io_stuff.h"
#include "eeprom_access.h"
#include "password_generator/password_generator.h"
#include <string.h>

// Flag for the main loop that a message has arrived
volatile uint8_t usb_msg_recv = 0;

// Number of received bytes
static volatile uint16_t usb_recv_bytes = 0;
// Number of bytes we expect for the current message (when using windows this will always be 129)
static volatile uint16_t usb_expected_bytes = 0;

/*
 * Since RAM is a sparse resource on the AVR and we need large coherent arrays for different parts
 * of the firmware we have to use the same statically allocated memory multiple times in different
 * roles
 */

// The size of the USB message buffer is the maximum message (128 keycodes + 1 msg type byte)
// Note that the actual size of the buffer union is much larger (342) bytes due to shared memory
#define USB_BUFFER_SIZE 192

// Minimum message size is a keyboard change, one flag byte + one new keyboard delay byte
#define USB_MIN_MSG_SIZE 2

volatile union {
    // Access to the different types of messages
    struct {
        // Flag for the USB message type
        uint8_t msg_type;
        // Different types of usb messages
        union {
                // For a standard password request (size = 341 bytes)
                struct 
                {
                    uint8_t password_request_msg[16];
                    uint8_t password_length;
                    uint8_t password_rules;
                    uint8_t password_appendix[3];
                    uint8_t password_keymap[64];
                    union {
                        // Shared memory for SHA256 W vector and the password result
                        uint32_t sha256_w[64];
                        uint8_t password_result[MAX_PW_LENGTH];
                    };
                }__attribute__((packed));
                
                // For a secret change request (size = 32 bytes)
                struct 
                {
                    uint8_t secret[32];
                }__attribute__((packed));
                
                // For a new keyboard delay request
                // Or for a keyboard read request
                // (size = 1 byte)
                struct
                {
                    uint8_t kb_delay;
                }__attribute__((packed));
                
                // For a new keyboard layout request
                // Or for a keyboard layout read request
                // (size = 128 bytes)
                struct
                {
                    uint8_t keyboard_codes[128];
                }__attribute__((packed));
        };
    }__attribute__((packed));
    
    // Buffer for usbWrite
    uint8_t msg_buffer[USB_BUFFER_SIZE];
} shared_buffer;

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
    0x95, 0x81,                    //   REPORT_COUNT (192)
    0x75, 0x08,                    //   REPORT_SIZE (8)
    0x09, 0x00,                    //   USAGE (Reserved (no event indicated))
    0xb1, 0x00,                    // FEATURE (Data,Ary,Abs)
    0xc0                           // END_COLLECTION
};

// Processes all request from the USB host
usbMsgLen_t usbFunctionSetup(uint8_t data[8])
{
    usbRequest_t *rq = (void*)data;

    if ((rq->bmRequestType & USBRQ_TYPE_MASK) == USBRQ_TYPE_CLASS) {
        // HID class request
        switch (rq->bRequest) {
            case USBRQ_HID_GET_REPORT:
                // Required by HID spec
                usbMsgPtr = (void*)&kb_report;
                return sizeof(kb_report);
            case USBRQ_HID_SET_REPORT:
                if ((rq->wLength.word > USB_BUFFER_SIZE) || (rq->wLength.word < USB_MIN_MSG_SIZE)) {
                    // Ignore insane requests 
                    return 0;
                }
                if (usb_expected_bytes > 0) {
                    // We did not expect a new request, something went wrong
                    io_failure_shutdown();
                }
                usb_expected_bytes = rq->wLength.word;
                // We abuse the feature report for sending data to us
                return USB_NO_MSG;
            default:
                return 0;
        }
    }
    // Ignore all other requests
    return 0;
}

// Processes the data sent to us by the host
usbMsgLen_t usbFunctionWrite(uint8_t* data, uint8_t len)
{
    // If we get more bytes from the host than expected we go into
    // shutdown mode
    if ((usb_recv_bytes + len) > usb_expected_bytes) {
        io_failure_shutdown();
    }
    memcpy(((uint8_t*)shared_buffer.msg_buffer)+usb_recv_bytes, data, len);
    usb_recv_bytes += len;
    if (usb_recv_bytes == usb_expected_bytes) {
        // Set flag for main loop
        usb_msg_recv = 1;
        // Return 1 if we have read all data
        return 1;
    }
    return 0;
}

// USB message type flags and lengths
#define USB_MSG_FLAG_REQUEST    (1 << 0)
#define USB_MSG_LEN_REQUEST     86

#define USB_MSG_FLAG_SET_SECRET    (1 << 1)
#define USB_MSG_LEN_SET_SECRET     33

#define USB_MSG_FLAG_SET_KB_DELAY    (1 << 2)
#define USB_MSG_LEN_SET_KB_DELAY     2

#define USB_MSG_FLAG_SET_KEYBOARD_CODES (1 << 3)
#define USB_MSG_LEN_SET_KEYBOARD_CODES  129


static int8_t process_password_request(void)
{
    int8_t success = pw_gen_generate_mapped((uint8_t*)shared_buffer.password_result,
                                            eeprom_layout.secret,
                                            (uint8_t*)shared_buffer.password_request_msg,
                                            (uint8_t*)shared_buffer.password_keymap,
                                            (uint8_t)shared_buffer.password_length,
                                            (uint8_t)shared_buffer.password_rules);
    if (!success) {
        return 0;
    }
    if (io_wait_for_user_bttn()) {
        return kb_send_password((uint8_t*)shared_buffer.password_result,
                                (uint8_t)shared_buffer.password_length,
                                (uint8_t*)shared_buffer.password_appendix,
                                ((uint8_t)shared_buffer.password_rules) & PW_GEN_HIT_ENTER);
    }
    // User did not press the button but no failure either
    return 1;
}

static int8_t process_secret_request(void)
{
    if (io_wait_for_user_bttn_hold()) {
        ee_access_set_secret((uint8_t*)shared_buffer.secret);
    }
    return 1;
}

static int8_t process_set_kb_delay(void)
{
    if (io_wait_for_user_bttn()) {
        ee_access_set_keyboard_delay(shared_buffer.kb_delay);
    }
    return 1;
}

static int8_t process_set_keyboard_codes(void)
{
    if (io_wait_for_user_bttn_hold()) {
        ee_access_set_keyboard_codes((uint8_t*)shared_buffer.keyboard_codes);
    }
    return 1;
}

int8_t usb_comm_process_message(void)
{
    int8_t ret_val = 0; 
    switch (shared_buffer.msg_type) {
        case USB_MSG_FLAG_REQUEST:
            ret_val = process_password_request();
            break;
        case USB_MSG_FLAG_SET_SECRET:
            ret_val = process_secret_request();
            break;
        case USB_MSG_FLAG_SET_KB_DELAY:
            ret_val = process_set_kb_delay();
            break;
        case USB_MSG_FLAG_SET_KEYBOARD_CODES:
            ret_val = process_set_keyboard_codes();
            break;
    }
    
    // Clear the buffer
    memset((void*)&shared_buffer, 0, sizeof(shared_buffer));
    return ret_val;
}

void usb_comm_reset(void)
{
    usb_msg_recv = 0;
    usb_recv_bytes = 0;
    usb_expected_bytes = 0;
}
