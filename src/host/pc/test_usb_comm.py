#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from usb_comm import *

import pytest
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *

def test_build_request_no_appendix():
    req_msg = os.urandom(16)
    km = [i for i in range(64)]
    req = build_request(req_msg, 40, 15, [], km)
    assert req == MSG_FLAG_REQUEST + req_msg + b'(\x0f\xff\xff\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?'

def test_build_request_short_appendix():
    req_msg = os.urandom(16)
    km = [i for i in range(64)]
    req = build_request(req_msg, 40, 15, [1], km)
    assert req == MSG_FLAG_REQUEST + req_msg + b'(\x0f\x01\xff\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?'

def test_build_request_full_appendix():
    req_msg = os.urandom(16)
    km = [i for i in range(64)]
    req = build_request(req_msg, 40, 15, [1, 2, 3], km)    
    assert req == MSG_FLAG_REQUEST + req_msg + b'(\x0f\x01\x02\x03\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?'
