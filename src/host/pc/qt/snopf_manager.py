#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
QT main application for managing the account table.
"""

from ui_snopf_manager import Ui_SnopfManager
import resources

import sys
sys.path.append('..')

import requests
import usb_comm
from account_table_model import AccountTableModel
from spin_box_delegate import SpinBoxDelegate
from new_entry_dialog import NewEntryDialog
from pin_dialog import PinDialog
from get_vers_info import get_commit

from PySide2 import QtCore, QtWidgets 
import os
import json
import fcntl

class SnopfManager(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_SnopfManager()
        self.ui.setupUi(self)
        
        # The user can select to save the password pin for this session
        self.userPin = None
        
        self.loadAccountTable()
                
        # Add a context menu for deleting / editing entries
        self.ui.accountTableView.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)
        self.ui.accountTableView.customContextMenuRequested.connect(
            self.openContextMenu)

        # Connect menu actions
        self.ui.actionNewEntry.triggered.connect(self.newEntry)
        self.ui.actionDeleteEntry.triggered.connect(self.deleteEntry)
        self.ui.actionSaveChanges.triggered.connect(
            self.saveChanges)
        self.ui.actionVersionInfo.triggered.connect(self.showVersionInfo)
        
        
    def loadAccountTable(self):
        app_path = os.getcwd()
        account_table_path = app_path + '/account_table.json'
        if not os.path.exists(account_table_path):
            with open(account_table_path, 'w') as f: json.dump({}, f)
        
        self.accountTableFile = open(account_table_path, 'r+')
        # Snopf manager locks the file until it's closed
        try:
            fcntl.flock(self.accountTableFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            QtWidgets.QMessageBox.critical(
                self, "File busy", "Cannot lock file!",
                QtWidgets.QMessageBox.Ok)
            sys.exit(1)
        
        accountTable = json.load(self.accountTableFile)
        self.initTableModel(accountTable)
        
    def initTableModel(self, data):
        # Init account table view
        accountTableModel = AccountTableModel(self, data)
        self.ui.accountTableView.setModel(accountTableModel)
        self.ui.accountTableView.resizeColumnsToContents()
        header = self.ui.accountTableView.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.ui.accountTableView.setItemDelegate(SpinBoxDelegate())
        
    def openContextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Make Password Request', self.passwordRequest)
        menu.addAction('New entry', self.newEntry)
        menu.addAction('Delete entry', self.deleteEntry)
        menu.exec_(self.ui.accountTableView.viewport().mapToGlobal(position))
    
    def newEntry(self):
        d = NewEntryDialog()
        if d.exec_() == QtWidgets.QDialog.Accepted:
            self.ui.accountTableView.model().newEntry(d.getNewEntry())
            
    def getSelectedEntry(self):
        try:
            row = self.ui.accountTableView.selectedIndexes()[0].row()
        except IndexError:
            return None
        return self.ui.accountTableView.model().entries[row]

    def deleteEntry(self):
        entry = self.getSelectedEntry()
        if entry:
            msg = 'Delete Entry for account %s' % entry['account']
            msg += ' for hostname %s?' % entry['hostname']
            if self.getAnswer('Are you sure?', msg):
                self.ui.accountTableView.model().deleteEntry(entry)
            
    def saveChanges(self):
        if self.getAnswer('Save Changes',
                          'Save all changes to password file?'):
            self.initTableModel(self.saveData())
            
    def saveData(self):
        newTable = self.ui.accountTableView.model().createAccountTable()
        self.accountTableFile.seek(0)
        json.dump(newTable, self.accountTableFile, indent=4, sort_keys=True)
        self.accountTableFile.truncate()
        return newTable
                
    def getAnswer(self, title, question):
        qm = QtWidgets.QMessageBox
        ret = qm.question(self, title, question, qm.Yes | qm.No)
        return ret == qm.Yes
    
    def passwordRequest(self):
        entry = self.getSelectedEntry()
        if not entry:
            return
            
        if self.userPin:
            pin = self.userPin
        else:
            d = PinDialog()
            if d.exec_() == QtWidgets.QDialog.Accepted:
                pin = d.ui.pinEdit.text()
                if d.ui.savePinCheckBox.isChecked():
                    self.userPin = pin
            else:
                return
        
        entry['pin'] = pin
        request = requests.combine_standard_request(entry)
        try:
            usb_comm.send_standard_pw_request(
                request, entry['password_length'])
        except usb_comm.DeviceNotFound:
            QtWidgets.QMessageBox.critical(
                self, "Device not found", "The device is not plugged in.",
                QtWidgets.QMessageBox.Ok)
                
    def showVersionInfo(self):
        QtWidgets.QMessageBox.information(
            self, "Version Info", "Git commit: " + get_commit(),
            QtWidgets.QMessageBox.Ok)
        
    def closeFile(self):
        fcntl.flock(self.accountTableFile, fcntl.LOCK_UN)
        self.accountTableFile.close()

    def closeEvent(self, event):
        if self.ui.accountTableView.model().dataManipulated():
            msg = 'Some data has been changed, do you really want to quit?'
            if self.getAnswer('Data changed', msg):
                self.closeFile()
                event.accept()
            else:
                event.ignore()
        else:
            self.closeFile()
            event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = SnopfManager()
    w.show()
    sys.exit(app.exec_())
