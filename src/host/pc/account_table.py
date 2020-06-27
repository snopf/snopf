#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Account table managing
'''

from hashlib import pbkdf2_hmac
from Crypto.Cipher import AES
import os
import json
import password_generator as pw

'''
An account table file is constructed like this:
16 byte AES initialization vector
16 byte PBKDF2 salt
10 bytes shortened git commit hash of snopf version that was used to save the file
10 bytes reserved space
followed by the account table json (UTF-8 encoded)
'''

KEY_SIZE = 32
IV_SIZE = 16
SALT_SIZE = 16
GIT_HASH_SIZE = 10
RESERVED_SPACE_SIZE = 10

def generate_salt():
    return os.urandom(SALT_SIZE)

def key_from_passphrase(passphrase, salt):
    '''Get master key  and salt from master passphrase'''
    if len(salt) != SALT_SIZE:
        raise ValueError('Expected salt of 16 bytes length')
    num_runs = 100000
    return pbkdf2_hmac('sha256', passphrase, salt, num_runs)

def encrypt_str(str_data, key):
    '''AES encrypt string using the given key and iv'''
    iv = os.urandom(IV_SIZE)
    aes = AES.new(key, AES.MODE_CBC, iv)
    data = str_data.encode()
    # Pad input data to be multiple of 16 for aes
    data += b'\x00' * (16 - len(data) % 16)
    encrypted = aes.encrypt(data)
    return iv, encrypted
    
def decrypt_str(str_data, iv, key):
    '''AES decrypt string using the given key and iv'''
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.decrypt(str_data).decode().strip('\x00')

def save_account_table(f, at, passphrase, commit_hash):
    '''Save account table to file'''
    if len(commit_hash) != GIT_HASH_SIZE:
        raise ValueError('Commit hash must be of size 10 bytes')    
    salt = generate_salt()
    key = key_from_passphrase(passphrase, salt)
    at_str = json.dumps(at)
    iv, encrypted = encrypt_str(at_str, key)
    f.write(iv)
    f.write(salt)
    f.write(commit_hash)
    f.write(b'\x00' * RESERVED_SPACE_SIZE)
    f.write(encrypted)
        
def open_account_table_file(f, passphrase):
    '''Returns a dictionary including all information from the account table file'''
    data = {}
    iv = f.read(IV_SIZE)
    salt = f.read(SALT_SIZE)
    data['commit_hash'] = f.read(GIT_HASH_SIZE)
    data['reserved_data'] = f.read(RESERVED_SPACE_SIZE)
    encrypted = f.read()
    key = key_from_passphrase(passphrase, salt)
    data['table'] = decrypt_str(encrypted, iv, key)
    
    return data

def create_entry():
    '''Create a new account table entry filled with default values'''
    entry = {}
    entry['password_length'] = pw.DEFAULT_PW_LENGTH
    entry['password_iteration'] = 0
    entry['comment'] = ''
    entry['keymap'] = pw.keymaps['all']
    entry['rules'] = 0
    entry['appendix'] = []
    return entry
