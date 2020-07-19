#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from account_table_model import *

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *
from pytestqt import *
import pytest
from PySide2.QtTest import *
from password_generator import keymaps

def get_test_account_table():
    return json.load(open('../../test_data/account_table_dummy.json'))

def testCount():
    at = get_test_account_table()
    model = AccountTableModel(at)
    assert model.rowCount() == len(at)
    assert model.columnCount(None) == 14
    
def testGetData():
    at = get_test_account_table()
    model = AccountTableModel(at)
    for row in range(len(at)):
        for col in range(13):
            index = model.createIndex(row, col)
            assert model.data(index) == at[row][model.columnKeys[col]]
        index = model.createIndex(row, 13)
        assert model.data(index) == '132.00'
        
def testSetData(qtbot):
    at = get_test_account_table()
    model = AccountTableModel(at)
    # Try to set entropy
    index = model.createIndex(0, model.keyColumns['entropy'])
    assert model.setData(index, 0, Qt.EditRole) == False
    # Change password length
    index = model.createIndex(0, model.keyColumns['password_length'])
    with qtbot.waitSignal(model.dataChanged, timeout=100) as blocker:
        assert model.setData(index, 23, Qt.EditRole) == True
    endIndex = model.createIndex(0, model.keyColumns['entropy'])
    assert blocker.args == [index, endIndex, []]
    # Make invalid change for new rule
    index = model.createIndex(0, model.keyColumns['include_lowercase'])
    assert model.setData(index, True, Qt.EditRole) == True
    index = model.createIndex(0, model.keyColumns['keymap'])
    assert model.setData(index, keymaps['uppercase'], Qt.EditRole) == False
    # Make valid change for new new rule
    assert model.setData(index, keymaps['hex'], Qt.EditRole) == True
    # Remove rule
    index = model.createIndex(0, model.keyColumns['include_lowercase'])
    assert model.setData(index, False, Qt.EditRole) == True
    # All keymaps should be valid now
    index = model.createIndex(0, model.keyColumns['keymap'])
    for key, km in keymaps.items():
        assert model.setData(index, km, Qt.EditRole) == True
    
    
        
