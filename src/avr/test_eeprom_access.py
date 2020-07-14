#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ctypes import *

c_lib = CDLL('./snopf_test.so')

def test_ee_access_get_key_code_overflow():
    b = (c_char * 1)()
    assert c_lib.ee_access_get_key_code(0, b) == 1
    assert c_lib.ee_access_get_key_code(64, b) == 0
    
def test_ee_access_get_key_modifier_overflow():
    b = (c_char * 1)()
    assert c_lib.ee_access_get_key_modifier(0, b) == 1
    assert c_lib.ee_access_get_key_modifier(64, b) == 0
    
