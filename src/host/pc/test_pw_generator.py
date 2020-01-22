#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from password_generator import *

from test_tools import *

def test_password_is_ok_all():
    valid_password = 'aA!1'
    assert password_is_ok(valid_password)

def test_password_is_ok_upper():
    invalid_password = 'aa!1'
    assert not password_is_ok(invalid_password)
    
def test_password_is_ok_lower():
    invalid_password = 'AA!1'
    assert not password_is_ok(invalid_password)
    
def test_password_is_ok_digit():
    invalid_password = 'aA!!'
    assert not password_is_ok(invalid_password)
    
def test_password_is_ok_special_character():
    invalid_password = 'aA11'
    assert not password_is_ok(invalid_password)
    
def test_encode_password():
    assert (encode_password(TEST_SECRET, b'testmessage', 40)
            == '5{haL)0DbXA3*7>Pk3/zrZ5g84tVPAVTy8y<JUce')
    assert (encode_password(TEST_SECRET, b'testmessage', 4)
            == '5{ha')
    
def test_generate_password():
    with open('../test_vectors/test_vectors_password_creation.json') as f:
        tests = json.load(f)['tests']
    for test in tests:
        req = get_bytes_from_json(test['request'])
        pw = generate_password(TEST_SECRET, req, test['password_length'])
        assert pw == test['password']
