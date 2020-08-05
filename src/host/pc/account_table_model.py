# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
TableModel for using the QtTableView with the account table
"""

from password_generator import (password_rules, rules_to_bool, bool_to_rules, check_keymap_valid,
                                check_rules_valid, calc_entropy_password)
import account_table as at

from PySide2.QtCore import *
from PySide2.QtGui import *
import copy

class AccountTableViewProxyModel(QSortFilterProxyModel):
    
    # Filters out all columns except for Service and Account
    
    def filterAcceptsColumn(self, source_column, source_parent):
        if source_column == AccountTableModel.keyColumns['service'] or source_column == AccountTableModel.keyColumns['account']:
            return True
        return False

class AccountTableModel(QAbstractTableModel):
    
    keyColumns = {
        'service': 0,
        'account': 1,
        'password_length': 2,
        'password_iteration': 3,
        'comment': 4,
        'keymap': 5,
        'include_lowercase': 6,
        'include_uppercase': 7,
        'include_digit': 8,
        'include_special': 9,
        'no_repetitions': 10,
        'no_sequences': 11,
        'appendix': 12,
        'entropy': 13
        }
    
    columnKeys = {c: k for k, c in keyColumns.items()}
    
    invalidNewData = Signal(str)    
    
    def __init__(self, accountTable, parent=None):
        super().__init__(parent)
        
        # We keep the original accountTable for tracking changes
        # but we won't update / change it unless explicitly asked
        self.originalTable = accountTable
        # Our table
        self.table = at.sort_account_table(copy.deepcopy(accountTable))
        # Markers for deleted items
        self.deletedItems = [False for i in self.table]
    
    def rowCount(self, parent=None):
        if parent and parent.isValid():
            return 0
        return len(self.table)
    
    def columnCount(self, parent):
        if parent and parent.isValid():
            return 0
        return len(self.keyColumns)
    
    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()
        colKey = self.columnKeys[column]
        entry = self.table[row]
        
        if colKey == 'entropy':
            return self.getEntropyString(entry)
        
        value = entry[colKey]
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if self.deletedItems[index.row()] and (colKey == 'service' or colKey == 'account'):
                # strikethrough deleted entries
                return ''.join([char + '\u0336' for char in value])
            
            return value
        
        if role == Qt.BackgroundRole:
            if self.deletedItems[index.row()] and (colKey == 'service' or colKey == 'account'):
                # Deleted items are redish
                return QBrush(QColor(250, 160, 130))
            if (not entry in self.originalTable 
                or entry != at.get_entry(self.originalTable, entry['service'], entry['account'])):
                # New or changed entries have a different background
                return QBrush(QColor(220, 240, 180))
                    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        
        if orientation == Qt.Horizontal:
            if section == self.keyColumns['service']:
                return 'Service'
            if section == self.keyColumns['account']:
                return 'Account'
            return ''
        
        return None
    
    def setData(self, index, value, role):
        colKey = self.columnKeys[index.column()]
        if colKey == 'entropy':
            return False
        if role == Qt.EditRole:
            # First check whether the new data would break rules
            entry = copy.deepcopy(self.table[index.row()])
            entry[colKey] = value
            if (not check_keymap_valid(entry['keymap'])
                or not check_rules_valid(bool_to_rules(entry), entry['keymap'])):
                self.dataChanged.emit(index, index)  # Emit data changed to undo breaking change
                self.invalidNewData.emit('Keymap and rules are incompatible')
                return False
            # if not, update data accordingly
            self.table[index.row()][colKey] = value
            # Update entropy if rules or password length have changed
            if colKey in ['include_lowercase', 'include_uppercase', 'include_digit',
                          'include_special', 'no_repetitions', 'no_sequences',
                          'password_length']:
                endIndex = self.createIndex(index.row(), self.keyColumns['entropy'])
            else:
                endIndex = index
            self.dataChanged.emit(index, endIndex)
            return True
        return False
        
    def newEntry(self, service, account):
        '''Create a new entry with default values for given service and accout'''
        if at.check_entry_exists(self.table, service, account):
            raise KeyError('Entry already exists')
        index = self.rowCount()
        at.add_new_entry(self.table, service, account)
        self.deletedItems.append(False)
        self.beginInsertRows(QModelIndex(), index, index)
        self.endInsertRows()
        return True
    
    def removeRow(self, index):
        '''Mark the entry with the given row index for deletion'''
        self.deletedItems[index.row()] = True
        self.dataChanged.emit(index, index)
        
    def tableChanged(self):
        '''Return whether any data has changed'''
        return not self.table == self.originalTable
    
    def getLiveEntries(self):
        '''Get entries that aren't marked for deletion'''
        return [entry for entry, delItem in zip(self.table, self.deletedItems) if not delItem]
    
    def commitData(self):
        '''Apply all data changes'''
        self.table = at.sort_account_table(self.getLiveEntries())
        self.deletedItems = [False for i in self.table]
        self.originalTable = copy.deepcopy(self.table)
        
    def getSaveData(self):
        '''Get data for persistent storage'''
        return self.getLiveEntries()
    
    def getServiceAccounts(self):
        '''Return a dictionary with a list of accounts for every existing service'''
        return at.get_accounts_for_services(self.table)
    
    def getEntry(self, service, account):
        '''Return entry for given service, account combination.
        Raises KeyError if service, account is not in table'''
        return at.get_entry(self.table, service, account)

    def getEntropyString(self, entry):
        '''Calculate entropy for given entry and build corresponding entropy string'''
        entropy = calc_entropy_password(entry['keymap'], entry['password_length'])
        if bool_to_rules(entry):
            return '\N{WARNING SIGN} {:0.2f}'.format(entropy)
        return '{:0.2f}'.format(entropy)
            
        
