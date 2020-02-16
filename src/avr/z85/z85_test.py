#!/usr/bin/env python3

# Copyright (c) 2018 Hajo Kortmann
# License: GNU GPL v2 (see License.txt)

from ctypes import *
import os
import builtins

# Python Z85 implementation
import zmq.utils.z85 as zmq_z85

# Z85 Reference C implementation
ref_z85 = CDLL('./z85_ref.so')
ref_z85_encode = ref_z85.Z85_encode
ref_z85_encode.restype = c_char_p

# Own Z85 implementation
z85 = CDLL('./z85.so')

def test_z85_encoding(num):
    '''
    Test the Z85 encoding routine against the reference implementation in C
    and the reference implementation in Python
    '''
    rand_inp = os.urandom(4 * num)
    
    ref_py = zmq_z85.encode(rand_inp)
    ref_c = ref_z85_encode(rand_inp, num * 4)
    
    outp_buffer = (c_char * (num * 5))()
    
    [z85.z85_encode_chunk(byref(outp_buffer, k*5), rand_inp[4*k:4*k+4])
     for k in range(num)]
    
    assert outp_buffer[:] == ref_py == ref_c
    
    print('Test passed')


if __name__ == '__main__':
    test_z85_encoding(10000)
