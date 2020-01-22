#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
Routines to communicate with the USB device using the pyUSB library.
"""

import usb.core
import usb.util
from hashlib import sha256

class DeviceNotFound(Exception):
    pass

# The devices identification
VENDOR_ID = 0x16c0
PRODUCT_ID = 0x27db
SERIAL_ID = 'snopf.com:snopf'

# 0x40 is the ID for vendor specific requests on the HID device
VENDOR_REQUEST_NUM = 0x40

# The control byte of the message can be one of these values
control_messages = {'none': (0).to_bytes(1, 'little'),
                    'hit_enter': (1).to_bytes(1, 'little'),
                    'change_kb_delay': (1 << 6).to_bytes(1, 'little'),
                    'change_secret': (1 << 7).to_bytes(1, 'little')}

# Length of the raw message (bytes), excluding the control byte and 
# the password length byte. The message must be exactly this long.
USB_MSG_LENGTH = 16

# The minimum and maximum password length in characters. We want a minimum of
# six characters to a) securely include all types of characters and b) to
# keep the computation time low
MIN_PW_LENGTH = 6
# The maximum password length is 40 (32 SHA256 bytes / 4 * 5 (Z85 encoding))
MAX_PW_LENGTH = 40

def is_device_available():
    """Test if the device is plugged in """
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID,
                        serial_number=SERIAL_ID)
    return dev != None
    
def get_standard_device():
    """Get the real USB device"""
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID,
                        serial_number=SERIAL_ID)
    if dev is None:
        raise DeviceNotFound()
    return dev

def send_message(msg, dev=None):
    """
    Send the raw byte message to the device dev. If dev is None,
    the standard USB device will be used.
    (This should always be the case except for test cases)
    """
    if dev is None:
        dev = get_standard_device()
        
    return dev.ctrl_transfer(VENDOR_REQUEST_NUM, 0, 0, 0, msg)
    
def build_message(ctrl, pw_length, msg):
    """
    Build a control message for the USB device from the ctrl byte,
    the requested password length (will be ignored for requests other than
    password requests) and the request message
    """
    assert len(msg) == USB_MSG_LENGTH
    return ctrl + pw_length.to_bytes(1, 'little') + msg

def set_kb_delay(ms, dev=None):
    """Set the key press delay for the usb device to the given ms value"""
    msg = build_message(ctrl=control_messages['change_kb_delay'],
                        pw_length=ms,
                        msg=bytes(USB_MSG_LENGTH))
    return send_message(msg, dev)

def send_standard_pw_request(msg, pw_length, dev=None, hit_enter=False):
    """
    Send a standard passwort request to the device. The first 16 bytes
    of SHA256(msg) will be transmitted to the device dev. Use hit_enter=True
    if the device should type "\n" after typing in the password
    """
    assert MIN_PW_LENGTH <= pw_length <= MAX_PW_LENGTH
    assert len(msg) == USB_MSG_LENGTH
    ctrl = (control_messages['hit_enter'] if hit_enter 
            else control_messages['none'])
    msg = build_message(ctrl, pw_length, msg)
    return send_message(msg, dev)

def send_new_secret(secret, dev=None):
    """Sends a new secret to the device"""
    assert len(secret) == 16
    msg = build_message(control_messages['change_secret'], 0, secret)
    send_message(msg, dev=dev)
    
def send_empty_message(dev=None):
    """
    Send just zeros to the device, used in the secret change routine
    """
    msg = bytes(18)
    send_message(msg, dev=dev)

def send_shutdown_message(dev=None):
    """Just send a message that is too long, to shutdown the device"""
    if dev is None:
        dev = get_standard_device()
    try:
        send_message(bytes(20), dev)
    except usb.core.USBError:
        pass
