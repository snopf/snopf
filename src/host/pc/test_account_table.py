#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from account_table import *

import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *
import tempfile
import json

def test_encrypt_decrypt_unpadded():
    data = 'a short test message of 32 bytes'
    salt = generate_salt()
    k = key_from_passphrase(b'password', salt)
    iv, encrypted = encrypt_str(data, k)
    assert data == decrypt_str(encrypted, iv, k)
    
def test_encrypt_decrypt_padded():
    data = 'a short test message of 31 byte'
    salt = generate_salt()
    k = key_from_passphrase(b'password', salt)
    iv, encrypted = encrypt_str(data, k)
    assert data == decrypt_str(encrypted, iv, k)

def test_account_table_file():
    tmp = tempfile.SpooledTemporaryFile(max_size=10000)
    at = {'a':'b', 'x':'y'}
    master_key = key_from_passphrase(b'passsword', generate_salt())
    commit_hash = b'0123456789'
    save_account_table(tmp, at, master_key, commit_hash)
    tmp.flush()
    tmp.seek(0)
    data = open_account_table_file(tmp, master_key)
    assert json.loads(data['table']) == at
    assert data['commit_hash'] == commit_hash
    
