#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from mnemonic import *

import json
import os

import bip39_mnemonic_reference_trezor as bip39_ref

def test_against_test_vectors():
    with open('../test_vectors/test_vectors_trezor.json') as f:
        test_vectors = json.load(f)['english']
    
    for test in test_vectors:
        entropy = bytes.fromhex(test[0])
        mnemonic = test[1].split()
        if len(mnemonic) > 12:
            # We only use 128 bit tests
            continue
        assert to_mnemonic(entropy) == mnemonic
        assert to_entropy(mnemonic) == entropy
        
def test_against_trezor_impl():
    ref_mnemonic = bip39_ref.Mnemonic('english')
    n_rand = 500
    for i in range(n_rand):
        rand_seed = os.urandom(16)
        our_mnemonic = to_mnemonic(rand_seed)
        
        assert ref_mnemonic.to_mnemonic(rand_seed) == ' '.join(our_mnemonic)
        assert (ref_mnemonic.to_entropy(' '.join(our_mnemonic))
                == to_entropy(our_mnemonic))
