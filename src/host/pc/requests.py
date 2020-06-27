#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Routines to build request templates for the device. All host implementations
(android, browser extension, etc.) must follow the same rules as here to
guarantee the same results for the same inputs on different platforms.
'''

from hashlib import sha256

# All password requests are the first 16 bytes of sha256(msg)
MSG_LENGTH = 16

def reduce_message(msg):
    '''
    Reduce any byte message to a 16 byte message
    '''
    return sha256(msg).digest()[:MSG_LENGTH]

def combine_standard_request(service, account, master_passphrase, password_iteration):
    '''
    Combines the request data in the correct order
    
    service : bytes
    account : bytes
    master_passphrase : bytes
    password_iteration : int
    '''
    if password_iteration == 0:
        # For the first iteration we just want to have an empty string here
        password_iteration = ''.encode()
    else:
        password_iteration = str(password_iteration).encode()
    
    # The important part, this order MUST not be changed!
    msg = service + account + master_passphrase + password_iteration
    return reduce_message(msg)
