#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


"""
Test routines to check if the AVR is working as expected

NOTE The avr code should be compiled using the
    TEST_PASSWORD_GENERATION_DANGEROUS
flag to disable the button pressing on the device
"""

# TODO Secret change test

import usb_comm
import password_generator as pg
import os
import sys
import random

# Standard secret for all new devices
STANDARD_SECRET = b'0123456789012345'

def test_password_request(request_message, secret=STANDARD_SECRET,
                          pw_length=pg.MIN_PW_LENGTH, hit_enter=True):
    usb_comm.send_standard_pw_request(request_message, 
                                      hit_enter=hit_enter,
                                      pw_length=pw_length)
    recv_pw = input()
    print(pg.generate_password(secret, request_message, pw_length))
    assert recv_pw == pg.generate_password(secret, request_message, pw_length)
    
def test_random_password_requests(num_runs, secret=STANDARD_SECRET,
                                  hit_enter=True, pw_length='random'):
    if pw_length == 'random':
        pw_length = [random.randint(pg.MIN_PW_LENGTH, pg.MAX_PW_LENGTH)
                     for i in range(num_runs)]
    
    else:
        assert usb_comm.MIN_PW_LENGTH <= pw_length <= usb_comm.MAX_PW_LENGTH
        pw_length = [pw_length] * num_runs
        
    messages = [os.urandom(16) for i in range(num_runs)]
    
    [test_password_request(messages[i], secret, pw_length[i], hit_enter)
     for i in range(num_runs)]
    
    print('Test passed with %d random requests.' % num_runs)
    
def test_usb_message_lengths():
    # A complete raw message is 18 byte long
    # (ctrl byte + password length byte + 16 byte message)
    
    # Test message that is too short
    usb_comm.send_message(bytes(17))
    ask_result()
    print('Device should be shutdown now.')
    input('Reinsert for next test and press enter.')
    
    # Test message that is too long
    usb_comm.send_message(bytes(19))
    ask_result()
    print('Device should be shutdown now.')
    input('Reinsert for next test and press enter.')
    
    # Test message that could overflow the buffer
    usb_comm.send_message(bytes(4**64))
    ask_result()
    print('Device should be shutdown now.')
    print('All tests done.')
    
if __name__ == '__main__':
    print('Running %d tests:' % int(sys.argv[1]))
    test_random_password_requests(int(sys.argv[1]))
