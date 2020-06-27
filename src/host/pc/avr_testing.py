#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


"""
Test routines to check if the AVR is working as expected

NOTE The avr code should be compiled using the
    AVR_TESTING_NO_USER_INPUT
flag to disable the button pressing on the device
"""


from usb_comm import *
from password_generator import *
import os
import sys
import random

# Standard secret for all new devices
STANDARD_SECRET = b'\x00' * 32

def test_random_password_requests(num):
    
    dev = get_standard_device()
    for i in range(num):
        req_msg = os.urandom(16)
        length = random.randint(MIN_PW_LENGTH, MAX_PW_LENGTH)
        
        kmap = keymaps[random.choice([k for k in keymaps.keys()])]
        rules = random.randint(0, 63)
        while not check_rules_valid(rules, kmap):
            rules = random.randint(0, 63)
        
        rules += PW_RULE_HIT_ENTER
        
        appendix = [0xff, 0xff, 0xff]
        for k in range(random.randint(0,3)):
            appendix[k] = random.randint(0, 63)
        
        exp = get_mapped_password(STANDARD_SECRET, req_msg, length,
                                  rules, kmap)
        append_keys(exp, appendix)
        print(map_to_characters(exp))
        msg = build_request(req_msg, length, rules, appendix, kmap)
        send_message(dev, msg)
        inp = input()
        assert inp == map_to_characters(exp)
        
    
if __name__ == '__main__':
    print('Running %d tests:' % int(sys.argv[1]))
    test_random_password_requests(int(sys.argv[1]))
