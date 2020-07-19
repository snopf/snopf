#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from password_generator import *

import sys
import os
import random
import pytest
from itertools import combinations
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *

def test_base64():
    with open('../../test_data/test_vectors_base64.json') as f:
        tests = json.load(f)['tests']
        for test_set in tests:
            for test in test_set:
                assert (
                    base64_encode(get_bytes_from_json(test['inp']), test['len'])
                    == test['outp'])
                
def test_passwords():
    with open('../../test_data/test_vectors_passwords.json') as f:
        tests = json.load(f)
        for test in tests:
            mapped_pw = get_mapped_password(
                get_bytes_from_json(test['secret']),
                get_bytes_from_json(test['message']), test['length'],
                test['rules'], test['keymap'])
            assert mapped_pw == test['mapped_password']
            assert map_to_characters(mapped_pw) == test['password_string']
            
def test_bool_rules():
    r = {'include_lowercase': False,
         'include_uppercase': False,
         'include_digit': False,
         'include_special': False,
         'no_repetitions': False,
         'no_sequences': False}
    rr = {key: val for key, val in r.items()}
    rr['include_lowercase'] = True
    assert bool_to_rules(rr) == PW_RULE_INCLUDE_LOWERCASE
    assert rules_to_bool(PW_RULE_INCLUDE_LOWERCASE) == rr
    rr = {key: val for key, val in r.items()}
    rr['include_uppercase'] = True
    assert bool_to_rules(rr) == PW_RULE_INCLUDE_UPPERCASE
    assert rules_to_bool(PW_RULE_INCLUDE_UPPERCASE) == rr
    rr = {key: val for key, val in r.items()}
    rr['include_digit'] = True
    assert bool_to_rules(rr) == PW_RULE_INCLUDE_DIGIT
    assert rules_to_bool(PW_RULE_INCLUDE_DIGIT) == rr
    rr = {key: val for key, val in r.items()}
    rr['include_special'] = True
    assert bool_to_rules(rr) == PW_RULE_INCLUDE_SPECIAL
    assert rules_to_bool(PW_RULE_INCLUDE_SPECIAL) == rr
    rr = {key: val for key, val in r.items()}
    rr['no_repetitions'] = True
    assert bool_to_rules(rr) == PW_RULE_NO_REP
    assert rules_to_bool(PW_RULE_NO_REP) == rr
    rr = {key: val for key, val in r.items()}
    rr['no_sequences'] = True
    assert bool_to_rules(rr) == PW_RULE_NO_SEQ
    assert rules_to_bool(PW_RULE_NO_SEQ) == rr
    
    for i in range(64):     # We have 2^6 different rule combinations
        assert bool_to_rules(rules_to_bool(i)) == i
                
def test_check_inclusion_rules_lowercase():
    pw = [KEY_TABLE.index('a')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_LOWERCASE)
    pw = [KEY_TABLE.index('r')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_LOWERCASE)
    pw = [KEY_TABLE.index('A')]
    assert not check_inclusion_rules(pw, PW_RULE_INCLUDE_LOWERCASE)
    
def test_check_inclusion_rules_uppercase():
    pw = [KEY_TABLE.index('A')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_UPPERCASE)
    pw = [KEY_TABLE.index('R')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_UPPERCASE)
    pw = [KEY_TABLE.index('a')]
    assert not check_inclusion_rules(pw, PW_RULE_INCLUDE_UPPERCASE)
    
def test_check_inclusion_rules_digits():
    pw = [KEY_TABLE.index('0')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_DIGIT)
    pw = [KEY_TABLE.index('9')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_DIGIT)
    pw = [KEY_TABLE.index('a')]
    assert not check_inclusion_rules(pw, PW_RULE_INCLUDE_DIGIT)

def test_check_inclusion_rules_special():
    pw = [KEY_TABLE.index('-')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_SPECIAL)
    pw = [KEY_TABLE.index('>')]
    assert check_inclusion_rules(pw, PW_RULE_INCLUDE_SPECIAL)
    pw = [KEY_TABLE.index('a')]
    assert not check_inclusion_rules(pw, PW_RULE_INCLUDE_SPECIAL)
    
def test_check_inclusion_rules_all():
    pw = [KEY_TABLE.index('a'), KEY_TABLE.index('A'), KEY_TABLE.index('0'),
          KEY_TABLE.index('-')]
    rules = (PW_RULE_INCLUDE_LOWERCASE + PW_RULE_INCLUDE_UPPERCASE
             + PW_RULE_INCLUDE_DIGIT + PW_RULE_INCLUDE_SPECIAL)
    assert check_inclusion_rules(pw, rules)
    pw = [KEY_TABLE.index('A'), KEY_TABLE.index('0'), KEY_TABLE.index('-')]
    assert not check_inclusion_rules(pw, rules)
    pw = [KEY_TABLE.index('a'), KEY_TABLE.index('0'), KEY_TABLE.index('-')]
    assert not check_inclusion_rules(pw, rules)
    pw = [KEY_TABLE.index('a'), KEY_TABLE.index('A'), KEY_TABLE.index('-')]
    assert not check_inclusion_rules(pw, rules)
    pw = [KEY_TABLE.index('a'), KEY_TABLE.index('A'), KEY_TABLE.index('0')]
    assert not check_inclusion_rules(pw, rules)
    
def test_replace_reps():
    pw = [0, 0, 2, 3, 4, 4]
    replace_reps(pw, keymaps['all'])
    assert pw == [0, 1, 2, 3, 4, 5]
    
def test_replace_seqs():
    pw = [0, 1, 2, 4, 5]
    replace_seqs(pw, keymaps['all'])
    assert pw == [0, 2, 2, 4, 6]

def test_replace_seqs_and_reps():
    pw = [0, 0, 2, 3, 3, 4]
    replace_seqs_and_reps(pw, keymaps['all'])
    assert pw == [0, 2, 4, 3, 5, 4]
    
def test_replace_seqs_and_reps_fuzz():
    for kmap in keymaps.values():
        data = random.choices([i for i in range(64)], k=10000)
        replace_seqs_and_reps(data, kmap)
        for i in range(1, len(data)):
            assert kmap[data[i]] != kmap[data[i-1]]
            assert kmap[data[i]] != kmap[data[i-1]] + 1
    
def test_check_rules_valid_rules_all():
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
    
    for kmap_name in valid_rules.keys():
        kmap = keymaps[kmap_name]
        valid_combinations = [
            [sum(c) for c in combinations(valid_rules[kmap_name], i)]
            for i in range(1, len(all_rules)+1)]
        for x in valid_combinations:
            for y in x:
                assert check_rules_valid(y, kmap)
        
        invalid_rules = set(all_rules).difference(set(valid_rules[kmap_name]))
        invalid_combinations = [
            [sum(c) for c in combinations(invalid_rules, i)]
            for i in range(1, len(all_rules)+1)]
        
        for x in invalid_combinations:
            for y in x:
                print(y, kmap_name)
                assert not check_rules_valid(y, kmap)

def test_check_keymap_valid():
    km = [i for i in range(65)]
    assert not check_keymap_valid(km)
    for km in keymaps.values():
        assert check_keymap_valid(km)
    km = [0, 1] * 32
    assert not check_keymap_valid(km)
    km = [0, 1, 3] * 22
    assert check_keymap_valid(km[:64])

def test_keys_to_keymap():
    assert keys_to_keymap('abcdefghijklmnopqr') == keymaps['lowercase']
    assert keys_to_keymap('ABCDEFGHIJKLMNOPQR') == keymaps['uppercase']
    assert keys_to_keymap('0123456789') == keymaps['digits']
    assert keys_to_keymap('abcdefghijklmnopqrABCDEFGHIJKLMNOPQR0123456789') == keymaps['alpha_numer']
    assert keys_to_keymap('abcdefghijklmnopqrABCDEFGHIJKLMNOPQR') == keymaps['letters']
    assert keys_to_keymap('0123456789abcdef') == keymaps['hex']
    
def test_keys_to_keymap_invalid_key():
    with pytest.raises(ValueError):
        keys_to_keymap('s')
    with pytest.raises(ValueError):
        keys_to_keymap('S')
    with pytest.raises(ValueError):
        keys_to_keymap('_')
        
def test_keys_to_keymap_zero_length():
    assert keys_to_keymap([]) == []
        
def test_check_if_preset_keymap():
    assert check_if_preset_keymap(keys_to_keymap('1234567890')) == 'digits'
    
def test_calc_entropy():
    assert calc_entropy_password(keymaps['all'], 1) == pytest.approx(6)
    assert calc_entropy_password(keymaps['digits'], 1) == pytest.approx(3.317740814944148)
    assert calc_entropy_password(keymaps['letters'], 1) == pytest.approx(5.125)
    assert calc_entropy_password(keymaps['lowercase'], 1) == pytest.approx(4.155639062229568)
    assert calc_entropy_password(keymaps['uppercase'], 1) == pytest.approx(4.155639062229568)
    assert calc_entropy_password(keymaps['alpha_numer'], 1) == pytest.approx(5.4375)
    assert calc_entropy_password(keymaps['hex'], 1) == pytest.approx(4.0)
