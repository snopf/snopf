#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from keymap_editing import *

from pytestqt import *

def test_validator(qtbot):
    val = KeymapValidator()
    # Test complete keymap
    assert val.validate(''.join(pg.KEY_TABLE), 0) == QValidator.Acceptable
    # Test to many chars
    assert val.validate(''.join(pg.KEY_TABLE + ['a']), 0) == QValidator.Invalid
    # Test single valid char
    assert val.validate(''.join(['a']), 0) == QValidator.Acceptable
    # Test single invalid char
    assert val.validate(''.join(['y']), 0) == QValidator.Invalid
    
def test_remaining_keys(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    used_chars = []
    for k in pg.KEY_TABLE:
        used_chars.append(k)
        with qtbot.waitSignal(edit.keymapChanged) as blocker:
            edit.insert(k)
        assert blocker.args[0] == pg.sort_keys(pg.key_table_set - set(used_chars))
        
def test_insert_over_max_length(qtbot):
    edit = KeymapLineEdit()
    text = edit.text()
    edit.insert('a')
    assert text == edit.text()
    edit.clear()
    edit.insert('a')
    assert 'a' == edit.text()

def test_insert_invalid(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    edit.insert('z')
    assert edit.text() == ''
    edit.insert('{')
    assert edit.text() == ''
    
def test_add_lowercase(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    edit.addLowercase()
    assert edit.text() == ''.join(pg.KEY_TABLE[0:pg.PW_GROUP_BOUND_LOWERCASE])
    
def test_add_uppercase(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    edit.addUppercase()
    assert edit.text() == ''.join(pg.KEY_TABLE[pg.PW_GROUP_BOUND_LOWERCASE:pg.PW_GROUP_BOUND_UPPERCASE])
    
def test_add_numerical(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    edit.addNumerical()
    assert edit.text() == ''.join(pg.KEY_TABLE[pg.PW_GROUP_BOUND_UPPERCASE:pg.PW_GROUP_BOUND_DIGIT])
    
def test_add_special(qtbot):
    edit = KeymapLineEdit()
    edit.clear()
    edit.addSpecial()
    assert edit.text() == ''.join(pg.KEY_TABLE[pg.PW_GROUP_BOUND_DIGIT:])
    
def test_presets(qtbot):
    edit = KeymapLineEdit()
    for km in pg.keymaps.values():
        edit.clear()
        for k in km:
            edit.insert(pg.KEY_TABLE[k])
        assert set(edit.text()) == set([pg.KEY_TABLE[k] for k in km])
    
        
    
