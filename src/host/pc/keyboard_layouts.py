# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

keys = 'abcdefghijklmnopqrABCDEFGHIJKLMNOPQR0123456789-@!?$*+=&#[]().:><'

def to_bytes(keyboard_layout):
    byte_layout = b''
    for c in keys:
        byte_layout += int.to_bytes(keyboard_layout[c][0], 1, 'little')
        byte_layout += int.to_bytes(keyboard_layout[c][1], 1, 'little')
    return byte_layout
    
def check_keyboard_layout(keyboard_layout):
    '''Check if a valid entry exists for every key.
    Raises ValueError in case of invalid data'''
    for key in keys:
        if not key in keyboard_layout:
            raise ValueError('No entry for key \"%s\" found.' % key)
        if not len(keyboard_layout[key]) == 2:
            raise ValueError('Invalid entry for key \"%s\".' % key)
        if not (type(keyboard_layout[key][0]) == int and type(keyboard_layout[key][1]) == int):
            raise ValueError('Invalid entry for key \"%s\".' % key)
    return True
