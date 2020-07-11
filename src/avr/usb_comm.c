// Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
// License: GNU GPL v2 (see License.txt)

#include "usb_comm.h"
#include "usb_keyboard.h"
#include "usbdrv.h"
#include "io_stuff.h"
#include "eeprom_access.h"
#include "password_generator/password_generator.h"
#include <string.h>

volatile uint8_t usb_msg_buffer[USB_MSG_LENGTH];

volatile uint8_t usb_recv_bytes = 0;

// Allow host to read out the usb_msg_buffer
volatile uint8_t usb_read_buffer_ok = 0;

#define USB_READ_RQ 0xC0
#define USB_VENDOR_RQ 0x40

// Processes all request from the USB host
usbMsgLen_t usbFunctionSetup(uint8_t data[8])
{
    usbRequest_t *rq = (void*)data;

    if ((rq->bmRequestType & USBRQ_TYPE_MASK) == USBRQ_TYPE_CLASS) {
        // HID class request
        switch (rq->bRequest) {
        case USBRQ_HID_GET_REPORT:
            // Should never happen, but just in case and b/c it's required
            // by the USB HID specs
            usbMsgPtr = (void*)&kb_report;
            return sizeof(kb_report);
        case USBRQ_HID_SET_REPORT:
            // We ignore any LED settings etc.
            return USB_NO_MSG;
        case USBRQ_HID_GET_IDLE:
            // Unused, but required by USB HID spec
            usbMsgPtr = (uint8_t*)&kb_idle_rate;
            return 1;
        case USBRQ_HID_SET_IDLE:
            // Unused, but required by USB HID spec
            kb_idle_rate = rq->wValue.bytes[1];
            return 0;
        default:
            return 0;
        }
    }
    // TODO FIXME
    else if (rq->bmRequestType == USB_READ_RQ) {
            if (usb_read_buffer_ok) {
                usbMsgPtr = (void*)usb_msg_buffer;
                // We allow reading out only once
                usb_read_buffer_ok = 0;
                // maximum number of valid bytes is 64, how much of that is
                // valid data is up to the host to decide
                return 64;
            } else {
                return 0;
            }
    } else if (rq->bmRequestType == USB_VENDOR_RQ) {
        // Vendor specific request, tell host to use usbFunctionWrite to
        // send data by returning USB_NO_MSG
        return USB_NO_MSG;
    }

    // Ignore all other requests
    return 0;
}

// Processes the data sent to us by the host
usbMsgLen_t usbFunctionWrite(uint8_t* data, uint8_t len)
{
    // If we get more bytes from the host than expected we go into
    // shutdown mode
    if ((usb_recv_bytes + len) > USB_MSG_LENGTH) {
        io_failure_shutdown();
    }
    memcpy(((uint8_t*)usb_msg_buffer)+usb_recv_bytes, data, len);
    usb_recv_bytes += len;
    // Return 1 if we have read all data
    return usb_recv_bytes == USB_MSG_LENGTH;
}

int8_t usb_comm_process_request(void)
{
    // Working buffer for the SHA256 algorithm and buffer for the password
    static uint8_t pw_work_buffer[256];
    // Buffer for the SHA256 hash result
    static uint8_t seed_buffer[32];
       
    struct USB_REQUEST* usb_data = (struct USB_REQUEST*)usb_msg_buffer;
 
    int8_t success = pw_gen_generate_mapped(pw_work_buffer, seed_buffer,
                                            eeprom_layout.secret,
                                            usb_data->request_msg,
                                            usb_data->keymap,
                                            usb_data->length,
                                            usb_data->rules);
    if (!(success)) {
        // TODO refactor buffer clearing copy/paste
        // This should not happen normally but just if the user sent
        // us an invalid request
        // Clear all buffers
        memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
        memset(pw_work_buffer, 0, 256);
        memset(seed_buffer, 0, 32);
        return 0;
    }
    
    if (!kb_send_string(pw_work_buffer, usb_data->length)) {
        // We might fail if the host sent us a keymap with keys outside
        // of the key area
        memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
        memset(pw_work_buffer, 0, 256);
        memset(seed_buffer, 0, 32);
        return 0;
    }
    
    // Send appendix if requested by user, values above 63 signal 'no appendix'
    for (uint8_t i = 0; i < 3; i++) {
        if (usb_data->appendix[i] >= 64) {
            break;
        }
        kb_send_string((usb_data->appendix) + i, 1); 
    }

    if (usb_data->rules & PW_GEN_HIT_ENTER) {
        kb_hit_enter();
    }
    
    // Clear all buffers
    memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
    memset(pw_work_buffer, 0, 256);
    memset(seed_buffer, 0, 32);
    
    return 1;
}

int8_t usb_comm_process_message(void)
{
    int8_t ret = 0;
    switch (((uint8_t*)usb_msg_buffer)[0]) {
        case USB_MSG_FLAG_REQUEST:
            if (!io_wait_for_user_bttn()) {
                // FIXME move the button press after the request has been processed
                return 1;
            }
            ret = usb_comm_process_request();
            break;
        
        case USB_MSG_FLAG_KEYBOARD_READ:
        {
            if (!io_wait_for_user_bttn()) {
                return 1;
            }
            struct UBS_READ_KEYBOARD *usb_msg = (
                struct UBS_READ_KEYBOARD*)usb_msg_buffer;
            // The maximum size of keys to read is limited by the size
            // of the usb_msg_buffer and we have two bytes per key
            // (modifer + keycode)
            if (usb_msg->num > (USB_MSG_LENGTH / 2)) {
                return 0;
            }
            ret = ee_access_read_keycodes(
                (uint8_t*)usb_msg_buffer, usb_msg->begin, usb_msg->num);
            if (ret) {
                usb_read_buffer_ok = 1;
            }
        } break;
            
        case USB_MSG_FLAG_KB_DELAY_READ:
        {
            if (!io_wait_for_user_bttn()) {
                return 1;
            }
            ret = ee_access_read_kb_delay((uint8_t*)usb_msg_buffer);
            if (ret) {
                usb_read_buffer_ok = 1;
            }
        } break;
        
        case USB_MSG_FLAG_WRITE_EEPROM_UNPROTECTED:
        {
            if (!io_wait_for_user_bttn_hold()) {
                return 1;
            }
            struct USB_WRITE_EEPROM *usb_msg = (
                struct USB_WRITE_EEPROM*)usb_msg_buffer;
            // Check that the number of data bytes submitted is sane
            if (usb_msg->len > USB_EEPROM_PAYLOAD_SIZE) {
                return 0;
            }
            ret = ee_access_write_unprotected(
                usb_msg->begin, usb_msg->payload, usb_msg->len);
            // Clear buffer
            memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
        } break;
            
        case USB_MSG_FLAG_WRITE_EEPROM_PROTECTED:
        {
            if (!io_wait_for_user_bttn_hold()) {
                // Clear buffer
                memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
                return 1;
            }
            struct USB_WRITE_EEPROM *usb_msg = (
                struct USB_WRITE_EEPROM*)usb_msg_buffer;
            if (usb_msg->len > USB_EEPROM_PAYLOAD_SIZE) {
                return 0;
            }
            ret = ee_access_write_protected(
                usb_msg->begin, usb_msg->payload, usb_msg->len);
            // Clear buffer
            memset((uint8_t*)usb_msg_buffer, 0, USB_MSG_LENGTH);
        } break;
    }
    return ret;
}
