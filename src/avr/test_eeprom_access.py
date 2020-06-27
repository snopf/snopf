#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ctypes import *

c_lib = CDLL('./snopf_test.so')

def test_ee_access_write_unprotected_access_err():
    d = (c_char * 1)()
    # writing to protected area should return 0
    assert c_lib.ee_access_write_unprotected(0, d, 1) == 0
    assert c_lib.ee_access_write_unprotected(0x140, d, 1) == 0

def test_ee_access_write_unprotected_valid():
    d = (c_char * 1)()
    # writing to unprotected area should return 1
    assert c_lib.ee_access_write_unprotected(0x141, d, 1) == 1
    
def test_ee_access_write_unprotected_overflow():
    d = (c_char * 210)()    
    # Overwriting the eeprom should return 0
    assert c_lib.ee_access_write_unprotected(0x141, d, 0xc0) == 0
    # But writing to the limit should be allowed
    assert c_lib.ee_access_write_unprotected(0x141, d, 0xc0-1) == 1

def test_ee_access_write_protected_overflow():
    d = (c_char * 210)()    
    # Overwriting the eeprom should return 0
    assert c_lib.ee_access_write_unprotected(0x141, d, 0xc0) == 0

def test_ee_access_write_protected():
    d = (c_char * 1)()    
    # Writing to the start should be allowed
    assert c_lib.ee_access_write_protected(0, d, 1) == 1
    
def test_ee_access_read_keycodes_overflow():
    b = (c_char * 64)()
    assert c_lib.ee_access_read_keycodes(b, 63, 2) == 0
    assert c_lib.ee_access_read_keycodes(b, 0, 44) == 0

def test_ee_access_get_keycode_overflow():
    b = (c_char * 2)()
    assert c_lib.ee_access_get_keycode(0, b) == 1
    assert c_lib.ee_access_get_keycode(64, b) == 0
