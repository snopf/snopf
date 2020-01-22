#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from usb_comm import *

from requests import reduce_message

class MockDevice(object):
    
    def ctrl_transfer(self, bmRequestType, bRequest, wValue=0, wIndex=0,
                      data_or_wLength = None, timeout = None):
        self.bmRequestType = bmRequestType
        self.bRequest = bRequest
        self.wValue = wValue
        self.wIndex = wIndex
        self.data_or_wLength = data_or_wLength
        self.timeout = timeout
        
def test_build_message():
    ctrl_byte = (2).to_bytes(1, 'little')
    pw_length = 25
    msg = reduce_message('testmessage')
    assert (build_message(ctrl_byte, pw_length, msg)
            == b'\x02\x19B\t\xd1\xb6\xe7u\xef\xbc\x9c\xdd\xb2U\xa8O\xe1%')
    
def test_set_kb_delay():
    dev = MockDevice()
    set_kb_delay(50, dev)
    assert dev.bmRequestType == VENDOR_REQUEST_NUM
    assert dev.data_or_wLength \
        == b'@2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
