#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ctypes import *
import json

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *

c_lib = CDLL('./snopf_test.so')

def test_pw_gen_base64():
    c_buffer = (c_char * 160)()
    with open('../test_data/test_vectors_base64.json') as f:
        tests = json.load(f)['tests']
        for test_set in tests:
            for test in test_set:
                inp = get_bytes_from_json(test['inp'])
                c_lib.pw_gen_base64(c_buffer, inp, test['len'])
                outp = [int.from_bytes(i, 'little') for i in c_buffer
                        ][:test['len']]
                assert outp == test['outp']

def test_pw_gen_generate_mapped():
    pw_gen_generate_mapped = c_lib.pw_gen_generate_mapped
    pw_gen_generate_mapped.restype = POINTER(c_char)
    with open('../test_data/test_vectors_passwords.json') as f:
        tests = json.load(f)
        
        keymap = (c_char * 64)()
                
        for test in tests:
            for i in range(64):
                keymap[i] = test['keymap'][i]
            secret = get_bytes_from_json(test['secret'])
            message = get_bytes_from_json(test['message'])
            
            password = pw_gen_generate_mapped(secret, message, keymap, test['length'], test['rules'])
            
            for i in range(test['length']):
                assert  password[:test['length']] == b''.join(
                    [int.to_bytes(i, 1, 'little') for i in test['mapped_password']])
                
PW_GEN_INCLUDE_GROUP_1 = (1 << 0)
PW_GEN_INCLUDE_GROUP_2 = (1 << 1)
PW_GEN_INCLUDE_GROUP_3 = (1 << 2)
PW_GEN_INCLUDE_GROUP_4 = (1 << 3)

def get_kmap():
    kmap = (c_char * 64)()
    for i in range(64):
        kmap[i] = int.to_bytes(i, 1, 'little')
    return kmap
                
def test_pw_gen_check_inclusion_rules_lowercase():
    kmap = get_kmap()
    buff = (c_char * 28)()
    buff[0] = 0
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_1)
    assert res
        
    buff[0] = 18
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_1)
    assert not res
    
def test_pw_gen_check_inclusion_rules_uppercase():
    kmap = get_kmap()    
    buff = (c_char * 28)()
    buff[0] = 18
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_2)
    assert res
        
    buff[0] = 36
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_2)
    assert not res
    
def test_pw_gen_check_inclusion_rules_digits():
    kmap = get_kmap()
    
    buff = (c_char * 28)()
    buff[0] = 36
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_3)
    assert res
        
    buff[0] = 46
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_3)
    assert not res

def test_pw_gen_check_inclusion_rules_special():
    kmap = get_kmap()
    
    buff = (c_char * 28)()
    buff[0] = 46
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_4)
    assert res
        
    buff[0] = 0
    res = c_lib.pw_gen_check_inclusion_rules(
        buff, kmap, 1, PW_GEN_INCLUDE_GROUP_4)
    assert not res
    
def test_pw_gen_check_inclusion_rules_all():
    all_rules = (PW_GEN_INCLUDE_GROUP_1 + PW_GEN_INCLUDE_GROUP_2
                 + PW_GEN_INCLUDE_GROUP_3 + PW_GEN_INCLUDE_GROUP_4)
    kmap = get_kmap()
    
    buff = (c_char * 28)()
    buff[0] = 0
    buff[1] = 18
    buff[2] = 36
    buff[3] = 46
    
    res = c_lib.pw_gen_check_inclusion_rules(buff, kmap, 4, all_rules)
    assert res
        
    buff[0] = 18
    res = c_lib.pw_gen_check_inclusion_rules(buff, kmap, 4, all_rules)
    assert not res
    
    buff[0] = 0
    buff[1] = 0
    res = c_lib.pw_gen_check_inclusion_rules(buff, kmap, 4, all_rules)
    assert not res
    
    buff[0] = 0
    buff[1] = 18
    buff[2] = 18
    res = c_lib.pw_gen_check_inclusion_rules(buff, kmap, 4, all_rules)
    assert not res
    
    buff[0] = 0
    buff[1] = 18
    buff[2] = 36
    buff[3] = 0
    res = c_lib.pw_gen_check_inclusion_rules(buff, kmap, 4, all_rules)
    assert not res
    
PW_GEN_NO_SEQ = (1 << 4)
PW_GEN_NO_REP =(1 << 5)

def test_replace_reps():
    kmap = get_kmap()
    _pw = [0, 0, 2, 3, 4, 4]
    pw = (c_char * len(_pw))(*_pw)
    res = c_lib.pw_gen_replace_reps_and_seqs(pw, kmap, len(_pw), PW_GEN_NO_REP)
    assert res
    assert ([int.from_bytes(pw[i], 'little') for i in range(len(_pw))]
            == [0, 1, 2, 3, 4, 5])
    
def test_replace_seqs():
    kmap = get_kmap()
    _pw = [0, 1, 2, 4, 5]
    pw = (c_char * len(_pw))(*_pw)
    res = c_lib.pw_gen_replace_reps_and_seqs(pw, kmap, len(_pw), PW_GEN_NO_SEQ)
    assert res
    assert ([int.from_bytes(pw[i], 'little') for i in range(len(_pw))]
            == [0, 2, 2, 4, 6])

def test_replace_seqs_and_reps():
    kmap = get_kmap()
    _pw = [0, 0, 2, 3, 3, 4]
    pw = (c_char * len(_pw))(*_pw)
    res = c_lib.pw_gen_replace_reps_and_seqs(pw, kmap, len(_pw),
                                             PW_GEN_NO_SEQ + PW_GEN_NO_REP)
    assert res
    assert ([int.from_bytes(pw[i], 'little') for i in range(len(_pw))]
            == [0, 2, 4, 3, 5, 4])
