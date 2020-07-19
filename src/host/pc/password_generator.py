#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
This is the implementation of the password generation algorithm used
on the avr in python for testing purposes or for generating passwords on
a trusted machine.
"""

from hashlib import sha256
import math

# Minimum length of a password
MIN_PW_LENGTH = 6
# Maximum length of a password (32 seed bytes to base64)
MAX_PW_LENGTH = 42
# Default password length (132 bit entropy for keymap['all']
DEFAULT_PW_LENGTH = 22

# Password generation rules
PW_RULE_GROUP_SUM = 0xf
PW_RULE_INCLUDE_LOWERCASE = 1 << 0
PW_RULE_INCLUDE_UPPERCASE = 1 << 1
PW_RULE_INCLUDE_DIGIT = 1 << 2
PW_RULE_INCLUDE_SPECIAL = 1 << 3

PW_GROUP_BOUND_LOWERCASE = 18
PW_GROUP_BOUND_UPPERCASE = 36
PW_GROUP_BOUND_DIGIT = 46
PW_GROUP_BOUND_SPECIAL = 64

# Remove sequential and repeated characters
PW_RULE_NO_SEQ = 1 << 4
PW_RULE_NO_REP = 1 << 5

# Comfort access to rules
password_rules = {
    'include_lowercase': PW_RULE_INCLUDE_LOWERCASE,
    'include_uppercase': PW_RULE_INCLUDE_UPPERCASE,
    'include_digit': PW_RULE_INCLUDE_DIGIT,
    'include_special': PW_RULE_INCLUDE_SPECIAL,
    'no_repetitions': PW_RULE_NO_REP,
    'no_sequences': PW_RULE_NO_SEQ}

rule_names = [key for key in password_rules.keys()]

def rules_to_bool(rules):
    '''Return dict with boolean entries for each rule for the given rules integer'''
    return {rule_name: bool(rules & rule_num) for rule_name, rule_num in password_rules.items()}

def bool_to_rules(rule_dict):
    '''Return rules integer for given rules'''
    rule = 0
    for rule_name in password_rules.keys():
        if rule_dict[rule_name]:
            rule |= password_rules[rule_name]
            
    return rule

# "hit enter rule" for completeness, unused in the python implementation
PW_RULE_HIT_ENTER = 1 << 6

# Absolute size of all keymaps
KEYMAP_SIZE = 64

keymaps = {}
# Standard keymap that uses all keys
keymaps['all'] = [i for i in range(KEYMAP_SIZE)]

# Maps all base64 indices to the ten digits from 0 to 9
keymaps['digits'] = ([i for i in range(PW_GROUP_BOUND_UPPERCASE,
                                   PW_GROUP_BOUND_DIGIT)] * 7)[:KEYMAP_SIZE]

# Maps all base64 indices to letters only
keymaps['letters'] = ([i for i in range(0, PW_GROUP_BOUND_UPPERCASE)] * 2)[:KEYMAP_SIZE]

# Maps all base64 indices to lowercase only
keymaps['lowercase'] = ([i for i in range(0, PW_GROUP_BOUND_LOWERCASE)] * 4)[:KEYMAP_SIZE]

# Maps all base64 indices to uppercase only
keymaps['uppercase'] = ([i for i in range(PW_GROUP_BOUND_LOWERCASE,
                                      PW_GROUP_BOUND_UPPERCASE)] * 4)[:KEYMAP_SIZE]

# Maps all base64 indices to digits + letters only
keymaps['alpha_numer'] = ([i for i in range(0, PW_GROUP_BOUND_DIGIT)] * 2)[:KEYMAP_SIZE]

# Maps all base64 indices to hex numbers only
keymaps['hex'] = [0, 1, 2, 3, 4, 5, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45] * 4
    
keymap_names = {'All': 'all', 'Digits': 'digits', 'Letters': 'letters', 'Lowercase': 'lowercase',
                'Uppercase': 'uppercase', 'Alphanumerical': 'alpha_numer', 'Hex': 'hex'}

# Keys the indices map the base64 transformed password to
KEY_TABLE = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
             'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
             'q', 'r', 'A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
             'O', 'P', 'Q', 'R', '0', '1', '2', '3',
             '4', '5', '6', '7', '8', '9', '-', '@',
             '!', '?', '$', '*', '+', '=', '&', '#',
             '[', ']', '(', ')', '.', ':', '<', '>']

key_table_set = set(KEY_TABLE)

def sort_keys(keys):
    """
    Sort Keys according to KEY_TABLE
    """
    return sorted(keys, key=KEY_TABLE.index)

def keys_to_keymap(keys):
    """
    Create a keymap from the given list of keys
    """
    if not keys:
        return []
    # Remove multiple entries and sort according to KEY_TABLE
    keys = sort_keys(set(keys))
    # Replace entries with indices
    keys = [KEY_TABLE.index(k) for k in keys]
    num_keys = len(keys)
    # Fill up until we have 64 entries
    for i in range(num_keys, KEYMAP_SIZE):
        keys.append(keys[i%num_keys])
    return keys

def check_if_preset_keymap(keymap):
    """
    Check whether the given keymap is the same as a known keymap, e.g. hex, lowercase..
    """
    for name in keymaps.keys():
        if keymap == keymaps[name]:
            return name
    return None

def base64_encode(seed, length):
    seed_as_int = int.from_bytes(seed, 'little')
    b64_password = []
    for i in range(length):
        b64_password.append(seed_as_int & 0x3f)
        seed_as_int >>= 6
    return b64_password

def map_base64(base64_password, keymap):
    mapped_password = []
    for index in base64_password:
        mapped_password.append(keymap[index])
    return mapped_password

def invert_uint32(data):
    # Assumes the data to be a stream of 32 bit integers and inverts
    # the endianess
    invert = lambda x: int.to_bytes(int.from_bytes(x, 'big'), 4, 'little')
    return b''.join([invert(data[i:i+4]) for i in range(0, len(data),4)])

def create_seed(secret, message):
    # We only work with the first 20 bytes of the SHA256 hash and omit the rest
    # Input and output has to be inverted due to the optimized SHA256 version
    # for the avr
    data = invert_uint32(secret + message)
    return invert_uint32(sha256(data).digest())

def check_inclusion_rules(mapped_password, rules):
    '''
    Checks whether the generated password fulfills the rules given in rules.
    
    Parameters
    ----------
    mapped_password : list
        Mapped password
    rules : int
        Integer defining rules for the password. The first four bits define
        which integers have to be included in the raw password
    
    Returns
    -------
    True if the raw password adheres to the rules, else False
    '''
    for index in mapped_password:
        if index < PW_GROUP_BOUND_LOWERCASE:
            rules &= ~(PW_RULE_INCLUDE_LOWERCASE)
        elif index < PW_GROUP_BOUND_UPPERCASE:
            rules &= ~(PW_RULE_INCLUDE_UPPERCASE)
        elif index < PW_GROUP_BOUND_DIGIT:
            rules &= ~(PW_RULE_INCLUDE_DIGIT)
        else:
            rules &= ~(PW_RULE_INCLUDE_SPECIAL)
        
        if not (rules & PW_RULE_GROUP_SUM):
            return True
    
    return False

def replace_reps(b64_password, keymap):
    '''
    Replace repeated characters in the base64 password
    '''
    for i in range(1, len(b64_password)):
        k = 0
        while keymap[b64_password[i]] == keymap[b64_password[i-1]]:
            b64_password[i] += 1
            b64_password[i] %= 64
            k += 1
            if k == 64:
                raise Exception('Invalid keymap')

def replace_seqs(b64_password, keymap):
    '''
    Replace character sequences (like `abc`) in the base64 password
    '''
    for i in range(1, len(b64_password)):
        k = 0
        while keymap[b64_password[i]] == keymap[b64_password[i-1]] + 1:
            b64_password[i] += 1
            b64_password[i] %= 64
            k += 1
            if k == 64:
                raise Exception('Invalid keymap')

def replace_seqs_and_reps(b64_password, keymap):
    '''
    Replace repeated characters and sequences of characters in the base64
    password
    '''
    for i in range(1, len(b64_password)):
        k = 0
        while (keymap[b64_password[i]] == keymap[b64_password[i-1]] + 1
               or keymap[b64_password[i]] == keymap[b64_password[i-1]]):
            b64_password[i] += 1
            b64_password[i] %= 64
            k += 1
            if k == 64:
                raise Exception('Invalid keymap')
            
def apply_seq_and_rep_rules(b64_password, rules, keymap):
    '''
    If the rules include any rules about repeated and sequenced characters
    we apply them here
    '''
    if rules & PW_RULE_NO_SEQ and rules & PW_RULE_NO_REP:
        replace_seqs_and_reps(b64_password, keymap)
    elif rules & PW_RULE_NO_SEQ:
        replace_seqs(b64_password, keymap)
    elif rules & PW_RULE_NO_REP:
        replace_reps(b64_password, keymap)
    
def create_password(seed, length, rules, keymap):
    '''
    Create a mapped password for the given rules
    '''
    b64 = base64_encode(seed, length)
    apply_seq_and_rep_rules(b64, rules, keymap)
    mapped_password = map_base64(b64, keymap)
    return mapped_password

def get_mapped_password(secret, message, length, rules, keymap,
                        return_num_runs=False):
    '''
    Generate the keycodes for a snopf password with the given parameters
    
    Parameters
    ----------
    secret : bytes
        32 byte secret
    message : bytes
        16 byte request message
    length : int
        Length of the requested password in characters
        (length - len(appendix) must be between 6 and 28)
    rules : int
        See check_inclusion_rules for valid values
    keymap : iterable
        64 keycodes that the base64 output will be mapped to
    return_num_runs : bool
        If True, the number of iterations for finding a valid password
        is returned
        
    Returns
    -------
    password : list
        The requested password as a list of key indices
    (num_runs) : int
        Number of iterations for finding a password
        (only returned if return_num_runs is set to True)
    '''
    if not MIN_PW_LENGTH <= length <= MAX_PW_LENGTH:
        raise Exception('Generated password length must be between 6 and 28')
    
    message = bytearray(message)
    seed = create_seed(secret, message)
    
    password = create_password(seed, length, rules, keymap)
    
    cnt = 0
    while not check_inclusion_rules(password, rules) and cnt < 255:
        message[0] = (message[0] + 1) % 256
        seed = create_seed(secret, message)
        password = create_password(seed, length, rules, keymap)
        cnt += 1
    
    if cnt == 255:
        raise OverflowError('More than 255 attempts required to find password')
    
    if return_num_runs:
        return password, cnt
    
    return password

def append_keys(password, appendix):
    '''For some edge cases we allow the addition of keys to the password'''
    if len(appendix) > 3:
        raise Exception('Maximum length of appendix is three')
    # all indices above 63 will be ignored
    for a in appendix:
        if a >= 64:
            break
        password.append(a)

def map_to_characters(password, keys=KEY_TABLE):
    '''Map the key indices to the given key table'''
    return ''.join([keys[k] for k in password])

def check_rules_valid(rules, keymap):
    '''
    For the rules to be valid you must include at minimum 10 characters from
    every group that shall be included by the rules.
    
    Parameters
    ----------
    rules : int
        Flags for group inclusion
    keymap : iterable
        Indices for the base64 transformation
        
    Returns
    -------
    True if the rules are valid, else False
    '''
    num_keys = {PW_RULE_INCLUDE_LOWERCASE: 0, PW_RULE_INCLUDE_UPPERCASE: 0,
                PW_RULE_INCLUDE_DIGIT: 0, PW_RULE_INCLUDE_SPECIAL: 0}
    for key in keymap:
        if key < PW_GROUP_BOUND_LOWERCASE:
            num_keys[PW_RULE_INCLUDE_LOWERCASE] += 1
        elif key < PW_GROUP_BOUND_UPPERCASE:
            num_keys[PW_RULE_INCLUDE_UPPERCASE] += 1
        elif key < PW_GROUP_BOUND_DIGIT:
            num_keys[PW_RULE_INCLUDE_DIGIT] += 1
        else:
            num_keys[PW_RULE_INCLUDE_SPECIAL] += 1
    
    for rule in num_keys.keys():
        if rules & rule and num_keys[rule] < 10:
            return False
    
    return True

def check_keymap_valid(keymap):
    '''
    Returns True if the keymap is valid, else False
    A valid keymap must be of length 64 and each index must be between 0 and 63,
    and at least 3 different indices must be in the map.
    '''
    if len(keymap) != KEYMAP_SIZE:
        return False
    if len(set(keymap)) < 3:
        return False
    if not all([0 <= key < KEYMAP_SIZE for key in keymap]):
        return False
    return True

def calc_entropy_password(keymap, length):
    '''
    Calculates the entropy for a password of the given length using the given
    keymap.
    WARNING: The calculated entropy is not correct if rules != 0
    '''
    # TODO lower boundary calculation for rules
    key_freq = [keymap.count(key) for key in set(keymap)]
    return length * -(sum([num/len(keymap) * math.log2(num/len(keymap)) for num in key_freq]))
