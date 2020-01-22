# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
TableModel for using the QtTableView with the account table
"""

from PySide2 import QtCore, QtGui
import bisect

def columnToKey(colInd):
    colKeys = ['hostname', 'account',
               'password_length', 'password_iteration']
    return colKeys[colInd]


class AccountTableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, parent, accountTable):
        super().__init__(parent)
        
        # We keep the original accountTable for tracking changes
        # but we won't update / change it unless explicitly asked
        self.accountTable = accountTable
        
        self.entries = []
        for hostname in sorted(accountTable.keys()):
            for account in sorted(accountTable[hostname]):
                password_length = accountTable[hostname][account][
                    'password_length']
                password_iteration = accountTable[hostname][account][
                    'password_iteration']
                self.entries.append({'hostname': hostname,
                                     'account': account,
                                     'password_length': password_length,
                                     'password_iteration': password_iteration})
        
        # For finding the right insertion index build tuples (host, account)
        self.keylist = [(x['hostname'], x['account']) for x in self.entries]
                
    def rowCount(self, parent=None):
        return len(self.entries)
    
    def columnCount(self, parent):
        return 4
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        key = columnToKey(index.column())
        entry = self.entries[index.row()]
        hostname = entry['hostname']
        account = entry['account']
        data = entry[key]
        
        if role == QtCore.Qt.DisplayRole:
            return data
        
        if role == QtCore.Qt.EditRole:
            return data
        
        if role == QtCore.Qt.BackgroundRole:
            # New entries are red
            if (not hostname in self.accountTable
                or not account in self.accountTable[hostname]):
                return QtGui.QBrush(QtCore.Qt.red)
            # And changed settings as well
            if ((key == 'password_iteration' or key == 'password_length')
                and data != self.accountTable[hostname][account][key]):
                return QtGui.QBrush(QtCore.Qt.red)
        
    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            key = columnToKey(index.column())
            
            self.entries[row][key] = value
                
            self.dataChanged.emit(index, index)
                        
            return True
        return False
    
    def newEntry(self, entry):
        if (entry['hostname'], entry['account']) in self.keylist:
            return False
        
        index = bisect.bisect_left(self.keylist,
                                   (entry['hostname'], entry['account']))
        
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.entries.insert(index, entry)
        self.keylist.insert(index, (entry['hostname'], entry['account']))
        
        self.endInsertRows()
        return True
    
    def deleteEntry(self, entry):
        index = self.keylist.index((entry['hostname'], entry['account']))
        self.beginRemoveRows(QtCore.QModelIndex(), index, index)
        self.entries.pop(index)
        self.keylist.pop(index)
        self.endRemoveRows()
        return True
    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        
        if orientation == QtCore.Qt.Horizontal:
            h = ['Hostname', 'Account',
                 'Password Length', 'Password Iteration']
            return h[section]
        
        return None
    
    def flags(self, index):
        flags = super().flags(index)
        key = columnToKey(index.column())
        if key == 'password_length' or key == 'password_iteration':
            flags |= QtCore.Qt.ItemIsEditable
        return flags
    
    def createAccountTable(self):
        """
        Creates a new account table from our (updated) data
        """
        table = {}
        for row in range(self.rowCount()):
            entry = self.entries[row]
            if not entry['hostname'] in table.keys():
                table[entry['hostname']] = {}
                      
            table[entry['hostname']][entry['account']] = {
                'password_length': entry['password_length'],
                'password_iteration': entry['password_iteration']}
        return table
    
    def dataManipulated(self):
        """
        Returns True if the original account table has been altered in any way.
        """
        newTable = self.createAccountTable()
        return newTable != self.accountTable
