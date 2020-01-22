#!/usr/bin/env python3

from ctypes import *
import hashlib
import os

sha256_c_lib = CDLL("./sha256.so")
sha256_c = sha256_c_lib.sha256_calculate_hash

def test_sha256_c(n):
    """Test the SHA256 C implementation against Python's SHA256"""
    # Input vectors need to be 256 bit / 32 byte for the C implementation
    inp_vectors = os.urandom(n * 32)
    ref_hashes = [hashlib.sha256(
        inp_vectors[i*32 : (i+1)*32]).digest() for i in range(n)]
    
    c_hashes = [(c_char * 32)() for i in range(n)]
    [sha256_c(c_hash, inp_vectors[i*32:], inp_vectors[i*32+16:])
     for i, c_hash in enumerate(c_hashes)]
    
    assert all([c.raw == r for c, r in zip(c_hashes[:10], ref_hashes[:10])])
    
    print("SHA256 test passed with %d random inputs." % n)
    
if __name__ == "__main__":
    test_sha256_c(10000)
