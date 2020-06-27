#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)


from ctypes import *
import hashlib
import os

c_lib = CDLL('./snopf_test.so')
sha256_c = c_lib.sha256

def invert_endianess(byte_data):
    return b''.join([byte_data[i*4:(i+1)*4][::-1]
                     for i in range(len(byte_data[::4]))])

def test_sha256_c(n=10000):
    #Test the SHA256 C implementation against Python's SHA256
    
    inp_messages = [os.urandom(16) for i in range(n)]
    inp_secrets = [os.urandom(32) for i in range(n)]
    sha256_w = (c_char * 64 * 4)()
    
    c_hash_results = [(c_char * 32)() for i in range(n)]
    [sha256_c(c_hash, inp_secret, inp_message, sha256_w)
     for c_hash, inp_secret, inp_message in zip(
         c_hash_results, inp_secrets, inp_messages)]
         
    ref_hashes = [hashlib.sha256(
        invert_endianess(s) + invert_endianess(m)).digest()
        for s, m in zip(inp_secrets, inp_messages)]
        
    assert all([c.raw == invert_endianess(r)
                for c, r in zip(c_hash_results, ref_hashes)])
