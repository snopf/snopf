#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Routines to communicate with the USB device using the pyUSB / hidapi library.
'''

import usb.core
import usb.util
from hashlib import sha256
import platform
import hid

use_hidapi = False
windows = False
if platform.system() == 'Windows':
    use_hidapi = True
    windows = True
        
class DeviceNotFound(Exception):
    pass

# The devices identification
VENDOR_ID = 0x1209
PRODUCT_ID = 0x7370

# HID report request type (endpoint, class)
HID_REPORT_REQUEST_TYPE = 0x22
# HID report request
USBRQ_HID_SET_REPORT = 0x09

# ID for buffer read requests
READ_REQUEST_NUM = 0xC0

# USB message flags and corresponding message lengths
MSG_FLAG_REQUEST = (1 << 0).to_bytes(1, 'little')
MSG_LEN_REQUEST = 86
MSG_FLAG_SET_SECRET = (1 << 1).to_bytes(1, 'little')
MSG_LEN_SET_SECRET = 33
MSG_FLAG_SET_KB_DELAY = (1 << 2).to_bytes(1, 'little')
MSG_LEN_SET_KB_DELAY = 2
MSG_FLAG_SET_KEYBOARD_CODES = (1 << 3).to_bytes(1, 'little')
MSG_LEN_SET_KEYBOARD_CODES = 129

# Maximum USB message length (128 keycodes + message type)
MAX_USB_MSG_LEN = 129

def send_message(dev, msg):
    '''Send the raw byte message to the device dev'''
    if use_hidapi:
        if windows:
            # We always have to send the exact same message size as defined in
            # the USB HID descriptor when using the Windows HID driver API
            msg += b'\x00' * (MAX_USB_MSG_LEN + 1 - len(msg))
            # And we have to submit the report ID (0) when running windows
            msg = b'\x00' + msg
        dev.send_feature_report(msg)
        dev.close()
        return
    return dev.ctrl_transfer(HID_REPORT_REQUEST_TYPE, USBRQ_HID_SET_REPORT, 0, 0, msg)

def build_request_message(request, length, rules, appendix, keymap):
    '''Build a password request message'''
    while len(appendix) < 3:
        appendix.append(0xff)
    return (MSG_FLAG_REQUEST
            + request + int.to_bytes(length, 1, 'little')
            + int.to_bytes(rules, 1, 'little')
            + b''.join([int.to_bytes(i, 1, 'little') for i in appendix])
            + b''.join([int.to_bytes(i, 1, 'little') for i in keymap]))

def build_set_keyboard_delay_message(delay):
    '''Get new keyboard delay byte message'''
    return MSG_FLAG_SET_KB_DELAY + int.to_bytes(delay, 1, 'little')
    
def build_new_secret_message(secret):
    '''Get write new secret message'''
    return MSG_FLAG_SET_SECRET + secret
    
def build_new_keyboard_keycodes_message(keycodes):
    '''Get new keyboard keycodes message'''
    return MSG_FLAG_SET_KEYBOARD_CODES + keycodes

def is_device_available():
    '''Test if the device is plugged in'''
    if use_hidapi:
        devs = hid.enumerate()
        for dev in devs:
            if dev['vendor_id'] == VENDOR_ID and dev['product_id'] == PRODUCT_ID:
                return True
        return False
    
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    return dev != None
    
def get_standard_device():
    '''Get the real USB device'''
    if use_hidapi:
        dev = hid.device()
        try:
            dev.open(VENDOR_ID, PRODUCT_ID)
        except OSError as e:
            raise DeviceNotFound()
        return dev
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise DeviceNotFound()
    return dev
