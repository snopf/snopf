#!/usr/bin/env python3

# Copyright (c) 2018 Hajo Kortmann
# License: GNU GPL v2 (see License.txt)

from ctypes import *
import numpy as np
import os
import builtins

# Python Z85 implementation
import zmq.utils.z85 as zmq_z85

# Z85 Reference C implementation
ref_z85 = CDLL("./z85_ref.so")
ref_z85_encode = ref_z85.Z85_encode
ref_z85_encode.restype = c_char_p

# Own Z85 implementation
z85 = CDLL("./z85.so")

def check_pw_reqs(pw, length=None):
    """Check if the password includes lower letters, capital letters,
    numbers and special characters"""        
    z85_special_chars = ".-:+=^!/*?&<>()[]{}@%$#"
    
    pw = pw[:length]
    
    return (builtins.any(c.islower() for c in pw)
            and builtins.any(c.isupper() for c in pw)
            and builtins.any(c.isdigit() for c in pw)
            and builtins.any(c in z85_special_chars for c in pw))

v_check_pw_reqs = np.vectorize(check_pw_reqs)

def test_passwords_lengths(num):
    """Create a number of random passwords and check how many fulfill
    the requirements for a given password length."""
    random_bytes = [os.urandom(40) for i in range(num)]
    
    passwords = [zmq_z85.encode(h) for h in random_bytes]
    
    # Count the number of passes for every password length
    num_passes =[]
    # Count the max number of rehashes needed to fulfill the requirements
    indices = np.arange(num)
    # max password length is 32/4 * 5  == 40 and minimum requirement is length
    # 4 to include all kind of characters
    for i in range(4, 41):
        passes = v_check_pw_reqs(passwords, i)
        num_passes.append(sum(passes))

    return num_passes

def test_z85_encoding(num):
    """Test the Z85 encoding routine against the reference implementation in C
    and the reference implementation in Python"""
    for i in range(num):
        num_4_byte_chunks = np.random.randint(1, 15)
        z85_buffer = (c_char * (num_4_byte_chunks * 5))()
        inp_vector = os.urandom(4 * num_4_byte_chunks)
        
        ref_zmq = zmq_z85.encode(inp_vector)
        
        ref_z85 = ref_z85_encode(inp_vector, num_4_byte_chunks * 4)
        
        [z85.z85_encode_chunk(byref(z85_buffer, k*5), inp_vector[4*k:])
         for k in range(num_4_byte_chunks)]
        
        assert z85_buffer[:] == ref_zmq == ref_z85
        
    print("Test passed")


if __name__ == "__main__":
    test_z85_encoding(10000)
