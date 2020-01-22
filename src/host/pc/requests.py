#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
Routines to build request templates for the device. All host implementations
(android, browser extension, etc.) must follow the same rules as here to
guarantee the same results for the same inputs on different platforms.
"""

from hashlib import sha256

# All password requests are the first 16 bytes of sha256(msg)
MSG_LENGTH = 16

def reduce_message(msg):
    """
    Reduce any unicode string message to a 16 byte message the device accepts
    """
    if not isinstance(msg, bytes):
        # in case of unicode text
        msg = msg.encode()
    return sha256(msg).digest()[:MSG_LENGTH]

def combine_standard_request(request_dict):
    """
    This is how a standard password request is created for example
    for a mail account login etc. All requests must follow this order
    to guarantee that we always get the same password for the same
    hostname + account combination!
    """
    hostname = request_dict.get('hostname', '')
    account = request_dict.get('account', '')
    pin = request_dict.get('pin', '')
    password_iteration = request_dict.get('password_iteration', 0)
    if password_iteration == 0:
        # For the first iteration we just want to have an empty string here
        # We could also just add a 0-string instead but for now that's how
        # it's happened...
        password_iteration = ''
    else:
        password_iteration = str(password_iteration)
        
    free_string = request_dict.get('free_string', '')
    
    # The important part, this order MUST not be changed!
    return reduce_message(hostname + account + pin 
                          + password_iteration + free_string)
