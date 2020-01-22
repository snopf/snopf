#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
This is the implementation of the password generation algorithm used
on the avr in python for testing purposes or for generating passwords on
a trusted machine.
"""

from usb_comm import MIN_PW_LENGTH, MAX_PW_LENGTH

from hashlib import sha256
import zmq.utils.z85 as zmq_z85

def password_is_ok(password):
    """
    Returns true if the password includes
    a capital letter,
    a lower letter, 
    a number,
    a special character
    """
    z85_special_chars = ".-:+=^!/*?&<>()[]{}@%$#"
    return (any([c.islower() for c in password])
            and any([c.isupper() for c in password])
            and any([c.isdigit() for c in password])
            and any([c in z85_special_chars for c in password]))
    
def encode_password(secret, message, pw_length):
    """Encode the secret + message to a password"""
    pw = zmq_z85.encode(sha256(secret+message).digest())[:pw_length]
    return pw.decode()

def generate_password(secret, message, pw_length=MAX_PW_LENGTH):
    """
    Generates a password for the given 128 bit / 16 byte secret and the
    message with the given password length.
    secret and message must be given as bytes or bytearray objects.
    """
    assert MIN_PW_LENGTH <= pw_length <= MAX_PW_LENGTH
    message = bytearray(message)
    secret = bytearray(secret)
    
    password = encode_password(secret, message, pw_length)
    i = 0
    while not password_is_ok(password):
        # To guarantee a valid password we might have to modify the first
        # byte of the message until all necessary characters are included
        message[0] = (message[0] + 1) % 256
        password = encode_password(secret, message, pw_length)
        i += 1
        if i == 255:
            # This shouldn't happen anyways but infinite loops don't look
            # pleasant
            raise ValueError(
                "More than 255 attempts required to find password.")
        
    return password
