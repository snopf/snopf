#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from keyboard_layouts import *

import pytest
import json

def get_us_layout():
    with open('keyboard_layout_files/us.json') as f:
        keyboard_layout = json.load(f)
    return keyboard_layout

def test_to_bytes():
    keyboard_layout = get_us_layout()
    assert to_bytes(keyboard_layout) == b'\x00\x04\x00\x05\x00\x06\x00\x07\x00\x08\x00\t\x00\n\x00\x0b\x00\x0c\x00\r\x00\x0e\x00\x0f\x00\x10\x00\x11\x00\x12\x00\x13\x00\x14\x00\x15\x02\x04\x02\x05\x02\x06\x02\x07\x02\x08\x02\t\x02\n\x02\x0b\x02\x0c\x02\r\x02\x0e\x02\x0f\x02\x10\x02\x11\x02\x12\x02\x13\x02\x14\x02\x15\x00\'\x00\x1e\x00\x1f\x00 \x00!\x00"\x00#\x00$\x00%\x00&\x00-\x02\x1f\x02\x1e\x028\x02!\x02%\x02.\x00.\x02$\x02 \x00/\x000\x02&\x02\'\x007\x023\x026\x027'
    
def test_check_keyboard_layout():
    keyboard_layout = get_us_layout()
    assert check_keyboard_layout(keyboard_layout) == True
    
def test_check_keyboard_layout_missing():
    keyboard_layout = get_us_layout()
    keyboard_layout.pop('a')
    with pytest.raises(ValueError):
        check_keyboard_layout(keyboard_layout)

def test_check_keyboard_layout_invalid_num():
    keyboard_layout = get_us_layout()
    keyboard_layout['a'].append(0)
    with pytest.raises(ValueError):
        check_keyboard_layout(keyboard_layout)
        
def test_check_keyboard_layout_invalid_arg():
    keyboard_layout = get_us_layout()
    keyboard_layout['a'][0] = 'x'
    with pytest.raises(ValueError):
        check_keyboard_layout(keyboard_layout)
