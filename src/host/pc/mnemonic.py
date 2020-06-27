#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Code for mnemonic generation for the device's secret. This code is following
the Bitcoin BIP39 standard and uses the english wordlist of Electron Cash
version 3.2.1. The last part of BIP39, from mnemonic to seed, which uses
PBKDF2 with a salt/passphrase, is omitted as we don't need a password.

BIP39: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
'''

from hashlib import sha256
import os

def read_word_list():
    '''
    Reads the word list txt file and checks it's integrity against the known
    hash of the word list we want to use.
    '''
    english = os.path.join(os.path.dirname(__file__), 'wordlist/english.txt')
    with open(english, 'r') as f:
        word_list = [line.rstrip() for line in f]
    
    check_file_hash = 'ad90bf3beb7b0eb7e5acd74727dc0da96e0a280a258354e7293fb7e211ac03db'
    tmp = sha256()
    [tmp.update(w.encode()) for w in word_list]
    assert tmp.hexdigest() == check_file_hash
    
    return word_list

def entropy_checksum(entropy):
    # For 256 bit entropy, the checksum is the first byte of the SHA-256
    # hash of the entropy
    return sha256(entropy).digest()[0]
    
def add_checksum(entropy, cs):
    # Shift left and add the checksum byte
    message = (int.from_bytes(entropy, 'big') << 8) + cs
    # bit length can only be 256 bit of entropy + 8 bit checksum at max
    assert message.bit_length() <= 264
    return message

def to_mnemonic(entropy):
    '''
    Retrieve 24 word mnemonic from 256 bit entropy. 
    entropy must be a 32 byte string.
    '''
    assert type(entropy) == bytes
    assert len(entropy) == 32
    cs = entropy_checksum(entropy)
    message = add_checksum(entropy, cs)
    # 0x7ff mask for 11 bit
    indexes = [(message >> (i * 11)) & 0x7ff for i in reversed(range(24))]
    word_list = read_word_list()
    mnemonic = [word_list[index] for index in indexes]
                
    assert entropy == to_entropy(mnemonic)
    return mnemonic

def sanitize_mnemomic(mnemonic):
    mnemonic = [word.lower() for word in mnemonic]
    mnemonic = [word.strip() for word in mnemonic]
    return mnemonic

def to_entropy(mnemonic):
    '''
    Retrieve the 256 bit secret from the given 24 word mnemonic
    as a bytes object.
    '''    
    wordlist = read_word_list()
    entropy = int(sum([(wordlist.index(word) << (11 * (23 - i)))
                          for i, word in enumerate(mnemonic)]))
    checksum = entropy & 0xff
    entropy = (entropy >> 8).to_bytes(32, 'big')
    
    assert checksum == entropy_checksum(entropy)
    
    return entropy
