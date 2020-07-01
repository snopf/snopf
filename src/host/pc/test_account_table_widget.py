#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from account_table_widget import *

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../../test_data'))
from test_tools import *
from pytestqt import *
import pytest
from PySide2.QtTest import *

_account_table = {'service1': {'account1': {}, 'account2': {}, 'account3': {}},
                  'service2': {'account1': {}, 'account2': {}, 'account3': {}}}

def test_complete_account_table(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable(_account_table)
    # Test that all services have been inserted
    assert widget.invisibleRootItem().childCount() == len(_account_table)
    # Test that all accounts have been inserted
    for service in _account_table.keys():
        assert widget.getServiceItem(service).childCount() == len(_account_table[service])
        for account in _account_table[service].keys():
            # Make sure that we can't create an entry twice
            with pytest.raises(KeyError):
                widget.addItem(service, account)
    # Test emptying the whole widget
    for service in _account_table.keys():
        for account in _account_table[service].keys():
            widget.deleteEntry(service, account)
    assert widget.invisibleRootItem().childCount() == 0
    
def test_adding_existing_item(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable({})
    widget.addItem('test', 'test')
    with pytest.raises(KeyError):
        widget.addItem('test', 'test')
        
def test_removing_non_existing_service(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable({})
    with pytest.raises(KeyError):
        widget.deleteEntry('test', 'test')
        
def test_removing_non_existing_account(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable({'test': {'test': {}}})
    with pytest.raises(KeyError):
        widget.deleteEntry('test', 'abc')
        
def test_account_selected_signal(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable(_account_table)
    firstItem = widget.invisibleRootItem().child(0)
    rect = widget.visualItemRect(firstItem)
    with qtbot.waitSignal(widget.accountSelected, timeout=100) as blocker:
        qtbot.mouseClick(widget.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())

def test_current_service(qtbot):
    widget = AccountTableWidget(None)
    widget.initNewAccountTable(_account_table)
    firstItem = widget.invisibleRootItem().child(0)
    rect = widget.visualItemRect(firstItem)
    qtbot.mouseClick(widget.viewport(), Qt.LeftButton, Qt.NoModifier, rect.center())

    assert widget.currentService() == 'service1'
    assert widget.currentAccount() == 'account1'
    
