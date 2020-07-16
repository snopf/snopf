#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Qt Widget for accessing the account table
'''

from PySide2.QtCore import *
from PySide2.QtWidgets import *

import logging
logger = logging.getLogger('account-table-widget')

class AccountTableWidget(QTreeWidget):
        
    serviceColumn = 0
    accountColumn = 1
    
    # Account selected item, delivers service and account string
    accountSelected = Signal(str, str)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.itemClicked.connect(self.selectFirstChild)
        
    def initNewAccountTable(self, accountTable):
        '''Init widget with new account table'''
        logger.info('Initializing widget with new account table')
        self.clear()
        for service in sorted(accountTable.keys()):
            for account in sorted(accountTable[service].keys()):
                self.addItem(service, account)
        self.invisibleRootItem().setExpanded(True)
        self.setHeaderLabels(['Service', 'Account'])
        
    def currentService(self):
        '''Get service name for currently selected item'''
        item = self.currentItem()
        if item.childCount() != 0:
            return None
        return item.parent().text(self.serviceColumn)
    
    def currentAccount(self):
        '''Get account name for currently selected item'''
        item = self.currentItem()
        if item.childCount() != 0:
            return None
        return item.text(self.accountColumn)
    
    def selectFirstChild(self, item):
        '''We always want to select the first child if we selected a toplevel item'''
        if item.childCount() != 0:
            item = item.child(0)
            self.setCurrentItem(item, True)
            
        service = self.currentService()
        account = self.currentAccount()
        self.accountSelected.emit(service, account)
        
    def getServiceItem(self, service):
        '''Get parent item with the given service string, returns None if no
        matching toplevel item exists'''
        for i in range(self.invisibleRootItem().childCount()):
            sItem = self.invisibleRootItem().child(i)
            if sItem.text(self.serviceColumn) == service:
                return sItem
        return None
    
    def getAccountItem(self, parentItem, account):
        '''Get Account item for selected service parentItem'''
        for i in range(parentItem.childCount()):
            aItem = parentItem.child(i)
            if aItem.text(self.accountColumn) == account:
                return aItem
        return None
    
    def createParentItem(self, service):
        '''Create new parent item for service'''
        sItem = QTreeWidgetItem()
        sItem.setText(self.serviceColumn, service)
        self.invisibleRootItem().addChild(sItem)
        return sItem
        
    def addItem(self, service, account):
        '''Add new item to widget'''
        logger.info('adding new entry')
        sItem = self.getServiceItem(service)
        if not sItem:
            sItem = self.createParentItem(service)
        if self.getAccountItem(sItem, account):
            raise KeyError('Entry already exists')
        aItem = QTreeWidgetItem()
        aItem.setText(self.accountColumn, account)
        sItem.addChild(aItem)
        sItem.setExpanded(True)
        # Select the new item
        self.setCurrentItem(aItem)
        
    def deleteEntry(self, service, account):
        '''Delete the entry with given strings for service and account'''
        sItem = self.getServiceItem(service)
        if not sItem:
            raise KeyError('No entry for service')
        aItem = self.getAccountItem(sItem, account)
        if not aItem:
            raise KeyError('No entry for account')
        sItem.removeChild(aItem)
        logger.info('Removed account entry')
        if sItem.childCount() == 0:
            self.invisibleRootItem().removeChild(sItem)
            logger.info('Removed parent item (was empty)')
