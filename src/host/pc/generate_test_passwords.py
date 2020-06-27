#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

# Module for test vector generation using the python implementation of
# the password generation module

from password_generator import *
import base64
import itertools
import os

all_rules = [PW_RULE_INCLUDE_LOWERCASE, PW_RULE_INCLUDE_UPPERCASE,
             PW_RULE_INCLUDE_DIGIT, PW_RULE_INCLUDE_SPECIAL]

valid_rules = {
    'all': all_rules,
    'digits': [PW_RULE_INCLUDE_DIGIT],
    'letters': [PW_RULE_INCLUDE_LOWERCASE, PW_RULE_INCLUDE_UPPERCASE],
    'lowercase': [PW_RULE_INCLUDE_LOWERCASE],
    'uppercase': [PW_RULE_INCLUDE_UPPERCASE],
    'alpha_numer': [PW_RULE_INCLUDE_LOWERCASE, PW_RULE_INCLUDE_UPPERCASE,
                    PW_RULE_INCLUDE_DIGIT],
    'hex': [PW_RULE_INCLUDE_LOWERCASE, PW_RULE_INCLUDE_DIGIT]
    }
        
def create_entry(secret, message, length, rules, keymap):
    d = {'keymap':keymap, 'length':length}
    d['secret'] = base64.encodebytes(secret).decode()
    d['message'] = base64.encodebytes(message).decode()
    pw = get_mapped_password(secret, message, length, rules, keymap)
    pw_string = map_to_characters(pw)
    d['mapped_password'] = pw
    d['password_string'] = pw_string
    d['rules'] = rules
    return d

def create_test_dict(num=10):
    tests = []
    pw_lengths = [i for i in range(6, 42)]
    
    for name in keymaps.keys():
        rules = valid_rules[name] + [PW_RULE_NO_SEQ, PW_RULE_NO_REP]
        rule_combinations = [
            sum(rule) for n in range(0, len(rules)+1)
            for rule in itertools.combinations(rules, n)]
        
        for length in pw_lengths:
            for rule in rule_combinations:
                for i in range(num):
                    tests.append(create_entry(os.urandom(32), os.urandom(16),
                                              length, rule, keymaps[name]))
    
    return tests
