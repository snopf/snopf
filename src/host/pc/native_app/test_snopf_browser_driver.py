#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from snopf_browser_driver import *

import pytest
import json
import fcntl

def get_test_table():
    return {'hostname1': 
                {'account1': {
                    'password_length': 40, 'password_iteration': 0}}}

def get_test_entry():
    return {'hostname': 'hostname1', 'account': 'account2',
            'password_length': 40, 'password_iteration': 0}

def test_entry_is_new_existing():
    test_table = get_test_table()
    test_entry = {'hostname': 'hostname1', 'account': 'account1'}
    assert not entry_is_new(test_entry, test_table)
    
def test_entry_is_new_account():
    test_table = get_test_table()
    test_entry = {'hostname': 'hostname1', 'account': 'account2'}
    assert entry_is_new(test_entry, test_table)

def test_entry_is_new_hostname():
    test_table = get_test_table()    
    test_entry = {'hostname': 'hostname2', 'account': 'account1'}
    assert entry_is_new(test_entry, test_table)
    
def test_insert_entry_existing_hostname():
    test_table = get_test_table()
    test_entry = {'hostname': 'hostname1', 'account': 'account2',
                  'password_length': 40, 'password_iteration': 0}
    insert_entry(test_entry, test_table)
    assert test_table == {'hostname1': {'account1': {
                                            'password_length': 40,
                                            'password_iteration': 0},
                                        'account2': {
                                            'password_length': 40,
                                            'password_iteration': 0}
                                        }
                            }
                                        
def test_insert_entry_new_hostname():
    test_table = get_test_table()
    test_entry = {'hostname': 'hostname2', 'account': 'account1',
                  'password_length': 40, 'password_iteration': 0}
    insert_entry(test_entry, test_table)
    assert test_table == {'hostname1': {'account1': {
                                            'password_length': 40,
                                            'password_iteration': 0}},
                          'hostname2': {'account1': {
                                            'password_length': 40,
                                            'password_iteration': 0}
                                        }
                            }
                          
def test_insert_entry_exception():
    test_table = get_test_table()
    test_entry = {'hostname': 'hostname1', 'account': 'account1',
                  'password_length': 40, 'password_iteration': 0}
    with pytest.raises(AssertionError):
        insert_entry(test_entry, test_table)
        
def create_account_table(tmp_path):
    account_table_path = tmp_path / "account_table_file"
    with open(account_table_path, 'w') as f:
        json.dump({}, f)
    return account_table_path

def test_save_new_entry_blocked(tmp_path):
    account_table_path = create_account_table(tmp_path)
    f = open(account_table_path, 'r')
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not save_new_entry(get_test_entry(), account_table_path)
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()
    
def test_save_new_entry_append(tmp_path):
    account_table_path = create_account_table(tmp_path)
    with open(account_table_path, 'w') as f:
        json.dump(get_test_table(), f)
    save_new_entry(get_test_entry(), account_table_path)
    with open(account_table_path, 'r') as f:
        file_table = json.load(f)
    test_table = get_test_table()
    test_table['hostname1']['account2'] = {
        'password_iteration': 0, 'password_length': 40}
    assert test_table == file_table
    
    
