#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Routines to communicate with the USB device using the pyUSB library.
'''

import usb.core
import usb.util
from hashlib import sha256

class DeviceNotFound(Exception):
    pass

# The devices identification
VENDOR_ID = 0x1209
PRODUCT_ID = 0x7370

# ID for vendor specific requests
VENDOR_REQUEST_NUM = 0x40

# ID for buffer read requests
READ_REQUEST_NUM = 0xC0

# USB message flags
MSG_FLAG_REQUEST = (1 << 0).to_bytes(1, 'little')
MSG_FLAG_KEYBOARD_READ = (1 << 1).to_bytes(1, 'little')
MSG_FLAG_KB_DELAY_READ = (1 << 2).to_bytes(1, 'little')
MSG_FLAG_WRITE_EEPROM_UNPROTECTED = (1 << 3).to_bytes(1, 'little')
MSG_FLAG_WRITE_EEPROM_PROTECTED =   (1 << 4).to_bytes(1, 'little')

# EEPROM layout
EEPROM_SECRET_ADDR = 0x01
EEPROM_KB_DELAY_ADDR = 0x141
EEEPROM_KEYBOARD_ADDR = 0x142

# Every writing message to the device has to have this length
USB_MSG_LENGTH = 86

def check_msg_length(build_func):
    def f(*args, **kwargs):
        m = build_func(*args, **kwargs)
        assert len(m) == USB_MSG_LENGTH
        return m
    return f

@check_msg_length
def build_request(req_msg, length, rules, appendix, keymap):
    '''Build a password request message'''
    if not appendix:
        appendix=[0xff, 0xff, 0xff]
    for i in range(3-len(appendix)):
        appendix.append(0xff)
    return (MSG_FLAG_REQUEST
            + req_msg + int.to_bytes(length, 1, 'little')
            + int.to_bytes(rules, 1, 'little')
            + b''.join([int.to_bytes(i, 1, 'little') for i in appendix])
            + b''.join([int.to_bytes(i, 1, 'little') for i in keymap]))

@check_msg_length
def build_read_keyboard_msg(begin, num):
    '''Assing the device to write num keyboard codes starting at begin to
    the message buffer'''
    return (MSG_FLAG_KEYBOARD_READ
            + int.to_bytes(begin, 1, 'little')
            + int.to_bytes(num, 1, 'little')
            + b'\x00' * 83)

@check_msg_length
def build_read_keyboard_delay():
    ''' Assigns the device to write the keyboard delay value to the 
    message buffer '''
    return (MSG_FLAG_KB_DELAY_READ
            + b'\x00' * (USB_MSG_LENGTH - 1))

@check_msg_length
def build_write_eeprom_unprotected(data, begin_addr):
    ''' Writes the data to the unprotected area of the eeprom, starting at addr '''
    # Unprotected eeprom space starts at EEPROM_KB_DELAY_ADDR
    assert begin_addr >= EEPROM_KB_DELAY_ADDR
    m = (MSG_FLAG_WRITE_EEPROM_UNPROTECTED
         + int.to_bytes(begin_addr, 2, 'little')
         + int.to_bytes(len(data), 1, 'little')
         + data)
    m += b'\x00' * (USB_MSG_LENGTH - len(m))
    return m

@check_msg_length
def build_write_eeprom_protected(data, begin_addr):
    ''' Writes the data to the protected area of the eeprom, starting at addr '''
    m = (MSG_FLAG_WRITE_EEPROM_PROTECTED
         + int.to_bytes(begin_addr, 2, 'little')
         + int.to_bytes(len(data), 1, 'little')
         + data)
    m += b'\x00' * (USB_MSG_LENGTH - len(m))
    return m

def read_buffer(dev):
    '''
    Read the msg buffer of the device after a valid read request has been send
    '''
    return dev.ctrl_transfer(READ_REQUEST_NUM, 0, 0, 0, 64)

def read_keyboard_delay(dev):
    '''Read keyboard delay (after keyboard delay read command was sent)'''
    return read_buffer(dev)[0]

def write_keyboard_delay(dev, delay):
    '''Write new keyboard delay to device'''
    m = build_write_eeprom_unprotected(
        int.to_bytes(delay, 1, 'little'), EEPROM_KB_DELAY_ADDR)
    send_message(dev, m)
    
def write_secret(dev, secret):
    '''Write new secret to device'''
    m = build_write_eeprom_protected(secret, EEPROM_SECRET_ADDR)
    send_message(dev, m)
    
def write_keyboard_keycodes(dev, keycodes, first_index):
    # Keycodes have to modifier + keycode pairs
    assert len(keycodes) % 2 == 0
    assert first_index % 2 == 0
    m = build_write_eeprom_unprotected(keycodes,
                                       EEEPROM_KEYBOARD_ADDR + first_index)
    send_message(dev, m)

def send_message(dev, msg):
    '''
    Send the raw byte message to the device dev. If dev is None,
    the standard USB device will be used.
    (This should always be the case except for test cases)
    '''
    return dev.ctrl_transfer(VENDOR_REQUEST_NUM, 0, 0, 0, msg)
    
def is_device_available():
    '''Test if the device is plugged in'''
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    return dev != None
    
def get_standard_device():
    '''Get the real USB device'''
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise DeviceNotFound()
    return dev
