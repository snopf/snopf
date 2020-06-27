#!/usr/bin/env python3

# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
QT main application for managing the account table.
'''

from ui_snopf_manager import Ui_SnopfManager

import requests
import usb_comm
from new_entry_dialog import NewEntryDialog
from get_commit_hash import get_commit_hash
from set_secret_wizard import SetSecretWizard
import password_generator as pw
import account_table as at
import snopf_logging

import sys
from PySide2.QtCore import *
from PySide2.QtNetwork import *
from PySide2.QtWebSockets import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import os
import json
import fcntl
import copy
from pathlib import Path
import logging
import resources_rc

logger = snopf_logging.get_logger('main')

class KeymapValidator(QValidator):
    
    def __init__(self, lineEdit, parent=None):
        super(KeymapValidator, self).__init__(parent)
        self.lineEdit = lineEdit
        
    def validate(self, inp, pos):
        if len(set(inp)) == len(inp) and all([i in pw.KEY_TABLE for i in inp]):
            return QValidator.Acceptable
        return QValidator.Invalid
    
    
class SnopfManager(QMainWindow):

# TODO Add last date changed entry (+ what was changed?)
# TODO change keyboard layout on device tool
# TODO read keyboard data (delay + keyboard)
# TODO test cases with mockup
# TODO undo / redo
# TODO make backups of loaded account tables
# TODO autosave every n minutes / after every new entry
# TODO show entropy of password settings
# TODO secure websocket connection (whitelisting)
# TODO option for allowing/disallowing new entries from websockets
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_SnopfManager()
        self.ui.setupUi(self)
        
        # Log uncaught exceptions
        sys.excepthook = self.logException
        
        logger.info('Application started')
        
        # Initialize tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(':/icon/icon/icon.svg'))
        self.tray.setToolTip('Snopf')
        trayMenu = QMenu(self)
        actionExit = trayMenu.addAction('Exit') 
        actionExit.triggered.connect(self.exit)
        self.tray.setContextMenu(trayMenu)
        self.tray.activated.connect(self.trayIconActivated)
        self.tray.show()
        
        # Filename of open account table
        self.__fileName = None
        
        # Currently selected data from account table
        self.selectedEntry = None
        self.selectedAccount = None
        self.selectedService = None
        
        self.commitHash = get_commit_hash()
        logger.info('Git hash: %s' % self.commitHash)
        
        # Master passphrase for current account table
        self.masterPassphrase = None
        
        # Flag if account table has been changed
        self.dataChanged = False
        
        # Connect menu actions
        self.ui.actionNew.triggered.connect(self.newAccountTable)
        self.ui.actionOpen.triggered.connect(self.openAccountTable)
        self.ui.actionSave.triggered.connect(self.saveAccountTable)
        self.ui.actionSaveAs.triggered.connect(self.saveAccountTableAs)
        self.ui.actionSave.setEnabled(False)
        self.ui.actionSaveAs.setEnabled(False)
        
        self.ui.actionExit.triggered.connect(self.exit)
        
        self.ui.actionNewEntry.triggered.connect(self.newEntry)
        self.ui.actionDeleteEntry.triggered.connect(self.deleteEntry)
        # Entry modyfing only makes sense if we have an active account table
        self.ui.actionNewEntry.setEnabled(False)
        self.ui.actionDeleteEntry.setEnabled(False)
        
        self.ui.actionVersionInfo.triggered.connect(self.showVersionInfo)
        self.ui.actionSetSnopfSecret.triggered.connect(self.startSecretWizard)
        self.ui.actionSetKeyboardDelay.triggered.connect(self.setKeyboardDelay)
        
        # Account table
        self.ui.accountTreeWidget.setHeaderLabels(['Service', 'Account'])
        self.ui.accountTreeWidget.itemActivated.connect(self.accountItemActivated)
        self.ui.commitChangesButton.clicked.connect(self.commitChanges)
        self.ui.deleteEntryButton.clicked.connect(self.deleteEntry)
        self.ui.requestPasswordButton.clicked.connect(lambda x: self.requestPassword())
        self.lastTabIndex = 0
        self.ui.tabWidget.currentChanged.connect(self.tabChanged)
        
        # Keymap editing
        self.ui.keymapEdit.textChanged.connect(self.fixKeymapEdit)
        v = KeymapValidator(self.ui.remainingKeysEdit, self)
        self.ui.keymapEdit.setValidator(v)
        self.ui.addLowercaseButton.clicked.connect(self.kmAddLowercase)
        self.ui.addUppercaseButton.clicked.connect(self.kmAddUppercase)
        self.ui.addNumericalButton.clicked.connect(self.kmAddNumerical)
        self.ui.addSpecialButton.clicked.connect(self.kmAddSpecial)
        self.ui.applyKeymapButton.clicked.connect(self.kmSelectPreset)
        self.fillKeymapCombobox()
        self.addAppendixValidator()
        
        # Password settings
        self.ui.lengthSpinner.setMinimum(pw.MIN_PW_LENGTH)
        self.ui.lengthSpinner.setMaximum(pw.MAX_PW_LENGTH)
        self.ui.lengthSpinner.setValue(pw.DEFAULT_PW_LENGTH)
        
        self.ui.lengthSpinner.valueChanged.connect(self.updateSelectedEntry)
        self.ui.includeLowercaseCB.stateChanged.connect(self.updateSelectedEntry)
        self.ui.includeUppercaseCB.stateChanged.connect(self.updateSelectedEntry)
        self.ui.includeNumericalCB.stateChanged.connect(self.updateSelectedEntry)
        self.ui.includeSpecialCB.stateChanged.connect(self.updateSelectedEntry)
        self.ui.pwAppendixEdit.editingFinished.connect(self.updateSelectedEntry)
        self.ui.keymapEdit.editingFinished.connect(self.updateSelectedEntry)
        
        # Load snopf options file
        self.loadOptions()
        
        # load last loaded file
        if self.options['last-filename']:
            try:
                self.openAccountTable(self.options['last-filename'])
            except FileNotFoundError:
                logger.warning('Last file % s not found, skipping auto load' % lastFileName)
        
        self.initWebsocketServer()
    
    def logException(self, exctype, value, traceback):
        '''Log uncaught execptions and show an info message'''
        logger.error('Exception', exc_info=(exctype, value, traceback))
        QMessageBox.critical(self, 'Uncaught Exception', str(exctype) + str(value), QMessageBox.Ok)
                
    def loadOptions(self):
        if not Path('snopf_options.json').exists():
            logger.info('snopf_options not found, creating new file')
            with open('snopf_options.json', 'w') as f:
                json.dump({}, f)
        with open('snopf_options.json', 'r') as f:
            logger.info('loading snopf options')
            self.options = json.load(f)
        
        # Initialize to default values if not set
        self.options['last-filename'] = self.options.get('last-filename', None)
        self.options['websocket-port'] = self.options.get('websocket-port', 60100)
    
    def getFileName(self):
        return self.__fileName
    
    def setFileName(self, fileName):
        self.__fileName = fileName
        self.setWindowTitle('Snopf %s' % self.__fileName)
    
    fileName = property(getFileName, setFileName)
        
    def initWebsocketServer(self):
        '''Init Snopf websocket server for browser plugin'''
        self.websocketServer = QWebSocketServer('snopf-websocket-server',
                                                QWebSocketServer.SslMode.NonSecureMode , self)
        # List of connections
        self.websockets = []
        # Start server
        success = self.websocketServer.listen(QHostAddress.LocalHost,
                                              port=self.options['websocket-port'])
        if not success:
            logger.error('Cannot start websocket server')
            err = self.websocketServer.errorString()
            logger.error(err)
            QMessageBox.critical(
                self, 'Websocket Error', 'Could not start websocket server. Error Message: %s' % err,
                QMessageBox.Ok)
        
        logger.info('Running websocket server with name %s' % self.websocketServer.serverName())
        logger.info('Websocket server address: %s, port: %d' % (
            self.websocketServer.serverAddress(), self.websocketServer.serverPort()))
        
        self.websocketServer.newConnection.connect(self.wsNewConnection)
        self.websocketServer.acceptError.connect(self.wsAcceptError)
        self.websocketServer.serverError.connect(self.wsServerError)
                
    def wsNewConnection(self):
        logger.info('New websocket connection')
        websocket = self.websocketServer.nextPendingConnection()
        self.websockets.append(websocket)
        logger.info('current list of websockets: %s' % str(self.websockets))
        websocket.textMessageReceived.connect(lambda msg: self.wsTextMessageReceived(websocket, msg))
        websocket.disconnected.connect(lambda: self.wsDisconnected(websocket))
        websocket.error.connect(lambda: self.wsError(websocket))
        
    def wsAcceptError(self, socketError):
        logger.error('Websocket Accept Error %d' % socketError)
        err = self.websocketServer.errorString()
        logger.error(err)
        QMessageBox.critical(self, 'Websocket Error', err, QMessageBox.Ok)
    
    def wsServerError(self, closeCode):
        logger.error('Websocket Server Error %d' % closeCode)
        err = self.websocketServer.errorString()
        logger.error(err)
        QMessageBox.critical(self, 'Websocket Error', err, QMessageBox.Ok)
    
    def wsDisconnected(self, websocket):
        logger.info('ws disconnected %s' % str(websocket))
        self.websockets.pop(self.websockets.index(websocket))
        logger.info('current list of websockets: %s' % str(self.websockets))
        
    def wsError(self, websocket, socketError):
        logger.error('ws error %d' % socketError)
        err = websocket.errorString()
        logger.error(err)
        QMessageBox.critical(self, 'Websocket Error', err, QMessageBox.Ok)
        
    def wsCreateMessage(self, cmd, data=''):
        '''Build websocket message for command cmd and payload data'''
        return json.dumps({'cmd': cmd, 'data': data})
        
    def getAccounts(self):
        '''Just return a hostname: accounts dictionary without additional information (passsword length etc.)'''
        return {hostname: [account for account in self.accountTable[hostname].keys()]
                for hostname in self.accountTable.keys()}
        
    def wsTextMessageReceived(self, websocket, msg):
        '''Slot for text messages from websocket connections'''
        logger.info('ws text msg received from %s' % str(websocket))
        try:
            msg = json.loads(msg)
        except json.JSONDecodeError:
            logger.error('Could not read message from client')
            return
        if msg['cmd'] == 'get-accounts':
            logger.info('got get-accounts msg')
            data = self.getAccounts()
            ourMsg = self.wsCreateMessage('new-accounts', data)
            websocket.sendTextMessage(ourMsg)
            return
        if msg['cmd'] == 'get-device-available':
            logger.info('got device-available msg')
            data = {'device-available': usb_comm.is_device_available()}
            ourMsg = self.wsCreateMessage('device-available', data)
            websocket.sendTextMessage(ourMsg)
            return
        if msg['cmd'] == 'password-request':
            logger.info('got password-request')
            data = msg['data']
            if not self.entryExists(data['service'], data['account']):
                if data['add_new_entries']:
                    logger.info('adding new entry')
                    self.addEntry(data['service'], data['account'])
                else:
                    logger.warning('Invalid request, unknown entry requested')
                    return
            
            self.requestPassword(data['service'], data['account'])
            
    def wsSendAccountTable(self):
        '''Send the current account table to all connected websockets'''
        data = self.getAccounts()
        msg = self.wsCreateMessage('new-accounts', data)
        for websocket in self.websockets:
            websocket.sendTextMessage(msg)
        
    def fixKeymapEdit(self):
        '''Sort keys in the keymap edit and fill up remaining key set'''
        self.ui.keymapEdit.setText(''.join(pw.sort_keys(self.ui.keymapEdit.text())))
        remainingKeys = pw.key_table_set.difference(set(self.ui.keymapEdit.text()))
        self.ui.remainingKeysEdit.setText(''.join(pw.sort_keys(remainingKeys)))
        
    def kmAddLowercase(self):
        for char in pw.KEY_TABLE[:pw.PW_GROUP_BOUND_LOWERCASE]:
            self.ui.keymapEdit.insert(char)
            
    def kmAddUppercase(self):
        for char in pw.KEY_TABLE[pw.PW_GROUP_BOUND_LOWERCASE:pw.PW_GROUP_BOUND_UPPERCASE]:
            self.ui.keymapEdit.insert(char)
    
    def kmAddNumerical(self):
        for char in pw.KEY_TABLE[pw.PW_GROUP_BOUND_UPPERCASE:pw.PW_GROUP_BOUND_DIGIT]:
            self.ui.keymapEdit.insert(char)
    
    def kmAddSpecial(self):
        for char in pw.KEY_TABLE[pw.PW_GROUP_BOUND_DIGIT:]:
            self.ui.keymapEdit.insert(char)
            
    def fillKeymapCombobox(self):
        for name in pw.keymap_names.keys():
            self.ui.selectKeymapComboBox.addItem(name)
            
    def kmSelectPreset(self, index):
        km = pw.keymaps[pw.keymap_names[self.ui.selectKeymapComboBox.currentText()]]
        self.ui.keymapEdit.clear()
        for char in km:
            self.ui.keymapEdit.insert(pw.KEY_TABLE[char])
            
    def addAppendixValidator(self):
        '''Validator for appendix input that only allows input from snopf character table'''
        regex = '^['
        # Add all lowercase + uppercase + digits
        for i in range(pw.PW_GROUP_BOUND_DIGIT):
            regex += str(pw.KEY_TABLE[i])
        # Add special characters
        for i in range(pw.PW_GROUP_BOUND_DIGIT, pw.PW_GROUP_BOUND_SPECIAL):
            regex += '\\' + str(pw.KEY_TABLE[i])
        regex += ']*'
        validator = QRegExpValidator(QRegExp(regex), self)
        self.ui.pwAppendixEdit.setValidator(validator)
        
    def getRules(self):
        '''Get rules integer from selected checkboxes'''
        rules = 0
        if self.ui.includeLowercaseCB.isChecked():
            rules += pw.PW_RULE_INCLUDE_LOWERCASE
        if self.ui.includeUppercaseCB.isChecked():
            rules += pw.PW_RULE_INCLUDE_UPPERCASE
        if self.ui.includeNumericalCB.isChecked():
            rules += pw.PW_RULE_INCLUDE_DIGIT
        if self.ui.includeSpecialCB.isChecked():
            rules += pw.PW_RULE_INCLUDE_SPECIAL
        if self.ui.avoidRepCB.isChecked():
            rules += pw.PW_RULE_NO_REP
        if self.ui.avoidSeqCB.isChecked():
            rules += pw.PW_RULE_NO_SEQ
        return rules
    
    def setRulesUi(self, rules):
        '''Set checkboxes according to rules'''
        self.ui.includeLowercaseCB.setChecked(bool(rules & pw.PW_RULE_INCLUDE_LOWERCASE))
        self.ui.includeUppercaseCB.setChecked(bool(rules & pw.PW_RULE_INCLUDE_UPPERCASE))
        self.ui.includeNumericalCB.setChecked(bool(rules & pw.PW_RULE_INCLUDE_DIGIT))
        self.ui.includeSpecialCB.setChecked(bool(rules & pw.PW_RULE_INCLUDE_SPECIAL))
        self.ui.avoidRepCB.setChecked(bool(rules & pw.PW_RULE_NO_REP))
        self.ui.avoidSeqCB.setChecked(bool(rules & pw.PW_RULE_NO_SEQ))
        
    def updateEntropy(self, *args, **kwargs):
        '''Update the entropy field value'''
        if not self.selectedEntry:
            self.ui.entropyEdit.setText('')
            return
        entropy = pw.calc_entropy_password(self.selectedEntry['keymap'],
                                           self.selectedEntry['password_length'])
        self.ui.entropyEdit.setText('{:0.2f}'.format(entropy))
        self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(255, 255, 255); }')
        self.ui.entropyEdit.setToolTip('')
        if self.selectedEntry['rules'] != 0:
            self.ui.entropyEdit.setText('\N{WARNING SIGN} {:0.2f}'.format(entropy))
            self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(240, 125, 125); }')
            self.ui.entropyEdit.setToolTip('Warning: The entropy might be lower than shown due to selected rules.')
    
    def serviceFromItem(self, item):
        '''Get the name of the service for the selected item, None if it's a toplevel item'''
        if item.childCount() != 0:
            return None
        return item.parent().text(0)
    
    def accountFromItem(self, item):
        '''Get the name of the account for the selected item, None if it's a toplevel item'''
        if item.childCount() != 0:
            return None
        return item.text(1)    
    
    def initAccountTableWidget(self):
        '''Initialize tree widget with new account table entries'''
        logger.info('Refilling account table widget')
        self.ui.accountTreeWidget.clear()
        self.ui.accountTreeWidget.invisibleRootItem().setExpanded(True)
        for service in sorted(self.accountTable.keys()):
            sItem = QTreeWidgetItem()
            sItem.setText(0, service)
            for account in sorted(self.accountTable[service].keys()):
              aItem = QTreeWidgetItem()
              aItem.setText(1, account)
              sItem.addChild(aItem)
            
            self.ui.accountTreeWidget.invisibleRootItem().addChild(sItem)
            sItem.setExpanded(True)
        # Enable account table editing
        self.ui.actionNewEntry.setEnabled(True)
        self.ui.actionDeleteEntry.setEnabled(True)
        self.ui.actionSave.setEnabled(True)
        
    def accountItemActivated(self, item):
        '''Slot for activated item in account table tree widget'''
        logger.info('Account item activated: %s' % str(item))
        service = self.serviceFromItem(item)
        if service is None:
            # Select the first account entry item instead if we clicked on the toplevel item
            item = item.child(0)
            self.ui.accountTreeWidget.setCurrentItem(item)
            self.accountItemActivated(item)
            return
        account = self.accountFromItem(item)
        
        self.checkCommit()
        
        self.selectedAccount = account
        self.selectedService = service
        self.selectedEntry = copy.deepcopy(self.accountTable[service][account])
        self.ui.serviceEdit.setText(service)
        self.ui.accountEdit.setText(account)
        self.ui.commentEdit.setText(self.selectedEntry['comment'])
        self.ui.lengthSpinner.setValue(self.selectedEntry['password_length'])
        self.ui.iterationSpinner.setValue(self.selectedEntry['password_iteration'])
        
        self.setRulesUi(self.selectedEntry['rules'])
        
        self.updateEntropy()
        
        self.ui.pwAppendixEdit.clear()
        for a in self.selectedEntry['appendix']:
            self.ui.pwAppendixEdit.insert(pw.KEY_TABLE[a])
            
        self.ui.keymapEdit.clear()
        for key in self.selectedEntry['keymap']:
            self.ui.keymapEdit.insert(pw.KEY_TABLE[key])
            
    def tabChanged(self, index):
        # Not really a change
        if index == self.lastTabIndex:
            return
        # Check whether the changes we made are compatible
        keymap = pw.keys_to_keymap(self.ui.keymapEdit.text())
        if (not pw.check_keymap_valid(keymap)
            or not pw.check_rules_valid(self.selectedEntry['rules'], keymap)):
            self.ui.tabWidget.setCurrentIndex(self.lastTabIndex)
            QMessageBox.information(self, 'Invalid Keymap',
                                    'The chosen keymap and rules are incompatible',
                                    QMessageBox.Ok)
            return
            
        self.lastTabIndex = index
        self.updateSelectedEntry()
        
    def checkCommit(self):
        '''Check if the entry has been changed and ask for commit if necessary'''
        if self.selectedEntry:
            self.updateSelectedEntry()
            if self.selectedEntry != self.accountTable[self.selectedService][self.selectedAccount]:
                logger.info('Selected entry has new data')
                if self.askUser('Entry changed',
                                'The entry for %s / %s has been changed. Commit changes?' % (self.selectedService, self.selectedAccount)):
                    logger.info('Commiting changes')
                    self.commitChanges()
    
    def updateSelectedEntry(self):
        '''Update currently selected entry with data from gui'''
        self.selectedEntry['password_length'] = self.ui.lengthSpinner.value()
        self.selectedEntry['password_iteration'] = self.ui.iterationSpinner.value()
        self.selectedEntry['rules'] = self.getRules()
        self.selectedEntry['keymap'] = pw.keys_to_keymap(self.ui.keymapEdit.text())
        self.selectedEntry['comment'] = self.ui.commentEdit.text()
        self.selectedEntry['appendix'] = [pw.KEY_TABLE.index(c) for c in self.ui.pwAppendixEdit.text()]
        self.updateEntropy()
        
    def commitChanges(self):
        '''Commit changed data to the account table in RAM (not persistent!)'''
        if not self.selectedEntry:
            return
        logger.info('committing changes')
        self.dataChanged = True
        self.updateSelectedEntry()
        self.accountTable[self.selectedService][self.selectedAccount].update(self.selectedEntry)
                
    def deleteEntry(self):
        '''Delete the entry from the account table'''
        item = self.ui.accountTreeWidget.currentItem()
        if not item:
            return
        service = self.serviceFromItem(item)
        account = self.accountFromItem(item)
        if self.askUser('Remove Entry', 
                        'Do you really want to remove the entry %s / %s' % (service, account)):
            logger.info('Deleting selected item')
            parent = item.parent()
            parent.removeChild(item)
            if parent.childCount() == 0:
                # Remove the service completely if no accounts are left
                self.ui.accountTreeWidget.invisibleRootItem().removeChild(parent)
                logger.info('Service entry is now empty and thus deleted')
                
            self.accountTable[service].pop(account)
            if len(self.accountTable[service]) == 0:
                self.accountTable.pop(service)
                
            self.selectedEntry = None
            self.accountItemActivated(self.ui.accountTreeWidget.currentItem())
            # Send new data to all connected websockets
            self.wsSendAccountTable()
            
    def addEntryItem(self, service, account):
        '''Add account item to tree widget'''
        sItem = None
        for i in range(self.ui.accountTreeWidget.invisibleRootItem().childCount()):
            if self.ui.accountTreeWidget.invisibleRootItem().child(i).text(0) == service:
                sItem = self.ui.accountTreeWidget.invisibleRootItem().child(i)
                break
        if sItem is None:
            sItem = QTreeWidgetItem()
            sItem.setText(0, service)
            self.ui.accountTreeWidget.invisibleRootItem().addChild(sItem)
        aItem = QTreeWidgetItem()
        aItem.setText(1, account)
        sItem.addChild(aItem)
        sItem.setExpanded(True)
        # Send new data to all connected websockets
        self.wsSendAccountTable()
        
    def entryExists(self, service, account):
        '''Check whether a service/account tuple already exists'''
        return service in self.accountTable and account in self.accountTable[service]
    
    def addEntry(self, service, account):
        '''Create a new entry in the account table'''
        if self.entryExists(service, account):
            logger.warning('Attempted to create existing entry')
            return
        if not service in self.accountTable:
            self.accountTable[service] = {}
            
        self.accountTable[service][account] = at.create_entry()
        self.addEntryItem(service, account)
        self.dataChanged = True
    
    def newEntry(self):
        '''Create a new entry'''
        self.checkCommit()
        d = NewEntryDialog()
        if d.exec_() == QDialog.Accepted:
            service = d.service()
            account = d.account()
            
            if self.entryExists(service, account):
                QMessageBox.critical(self, 'Entry exists',
                                     'An entry for the same service and account already exists',
                                     QMessageBox.Ok)
                return
            
            self.addEntry(service, account)
            
    def checkCurrentDataSave(self):
        '''Check if current account table has been changed and whether changes should be saved'''
        self.checkCommit()
        if self.dataChanged:
            if self.askUser('Account table has been changed',
                              'Save current account table?'):
                logger.info('Saving current account table')
                self.saveAccountTable()
        
    def newAccountTable(self):
        '''Create an empty account table'''
        self.checkCurrentDataSave()
        # Set a master key for the new account table
        passphrase_one = self.getPassphrase()
        if not passphrase_one:
            return
        passphrase_two = self.getPassphrase('Repeat Passphrase')
        if not passphrase_one == passphrase_two:
            QMessageBox.critical(self, 'Wrong Passphrase', 'Passphrases do not match',
                                 QMessageBox.Ok)
            return
        self.masterPassphrase = passphrase_one
        self.accountTable = {}
        self.initAccountTableWidget()
        self.fileName = None
        self.dataChanged = False
        
    def getPassphrase(self, title=None, text=None):
        '''Get a master passphrase from user input'''
        if not title:
            title = 'Enter Master Passphrase'
        if not text:
            text = 'Passphrase:'
        passphrase, ok = QInputDialog.getText(self, title, text, QLineEdit.Password, '')
        if ok:
            return passphrase.encode()
        return None
    
    def openAccountTable(self, fileName=None):
        '''Open existing account table file'''
        self.checkCurrentDataSave()
        if not fileName:
            fileName,_ = QFileDialog.getOpenFileName(
                self, 'Open Account Table', str(Path.home()), 'Account table (*.snopf)')
        if not fileName:
            return
        passphrase = self.getPassphrase(text='Passphrase for file %s' % fileName)
        if not passphrase:
            return
        try:
            with open(fileName, 'rb') as f:
                try:
                    data = at.open_account_table_file(f, passphrase)
                except ValueError as e:
                    logger.error('Could not decrypt file', exc_info=sys.exc_info())
                    QMessageBox.critical(self, 'Error', 'Cannot decrypt file', QMessageBox.Ok)
                    return
        except FileNotFoundError:
            logger.error('File not found %s' % fileName)
            QMessageBox.critical(self, 'File not found', 'File not found', QMessageBox.Ok)
            return
        try:
            self.accountTable = json.loads(data['table'])
        except json.JSONDecodeError:
            logger.error('Could not decode json', exc_info=sys.exc_info())
            QMessageBox.critical(self, 'Error', 'Cannot read file', QMessageBox.Ok)
            return
        # All went well, update data to loaded table
        self.masterPassphrase = passphrase
        self.dataChanged = False
        self.fileName = fileName
        self.initAccountTableWidget()
    
    def saveAccountTable(self):
        '''Save curent account table to hard disk'''
        if not self.fileName:
            self.saveAccountTableAs()
            return
            
        if not self.fileName.endswith('.snopf'):
            self.fileName += '.snopf'
        try:
            with open(self.fileName, 'wb') as f:
                at.save_account_table(f, self.accountTable, self.masterPassphrase,
                                      self.commitHash.encode()[:at.GIT_HASH_SIZE])
                logger.info('Saving file')
        except IOError:
            logger.error('Could not save to file', exc_info=sys.exc_info())
            QMessageBox.critical(self, 'Error', 'Cannot write to file %s' % self.fileName,
                                 QMessageBox.Ok)
            return
        
        self.dataChanged = False
        
    def saveAccountTableAs(self):
        '''Save under new name'''
        fileName,_ = QFileDialog.getSaveFileName(self, 'Save Account Table',
                                                 str(Path.home()), 'Account table (*.snopf)')
        if not fileName:
            return
        self.fileName = fileName
        self.saveAccountTable()
        
    def getPathFromCurrentFile(self):
        '''Get the path for the currently open file'''
        if not self.fileName:
            return str(Path.home())
        return os.path.dirname(os.path.abspath(self.fileName))
            
    def requestPassword(self, service=None, account=None):
        '''Make a password request to snopf using the currently selected entry'''
        if not service:
            service = self.selectedService
            account = self.selectedAccount
        self.checkCommit()
        
        if not usb_comm.is_device_available():
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                 QMessageBox.Ok)
            return
        
        password_iteration = self.accountTable[service][account]['password_iteration']
        password_length = self.accountTable[service][account]['password_length']
        rules = self.accountTable[service][account]['rules']
        appendix = self.accountTable[service][account]['appendix']
        keymap = self.accountTable[service][account]['keymap']
        
        req_msg = requests.combine_standard_request(service.encode(), account.encode(),
                                                    self.masterPassphrase, password_iteration)
        
        req = usb_comm.build_request(req_msg, password_length, rules, appendix, keymap)
        dev = usb_comm.get_standard_device()
        if not dev:
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.', QMessageBox.Ok)
            return
        
        usb_comm.send_message(dev, req)
        
    def setKeyboardDelay(self):
        '''Set the keyboard delay for a connected snopf device'''
        delay, ok = QInputDialog.getInt(self, 'Set Keyboard Delay', 'Delay in ms', 10, 0, 255)
        if ok:
            if not usb_comm.is_device_available():
                QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                     QMessageBox.Ok)
                return
            dev = usb_comm.get_standard_device()
            usb_comm.write_keyboard_delay(dev, delay)
            QMessageBox.information(self, 'Setting Keyboard Delay',
                                    'Press the Button on the device for five seconds.',
                                    QMessageBox.Ok)
    
    def askUser(self, title, question):
        '''Get yes / no answer from user'''
        qm = QMessageBox
        ret = qm.question(self, title, question, qm.Yes | qm.No)
        return ret == qm.Yes
    
    def showVersionInfo(self):
        QMessageBox.information(
            self, 'Version Info', 'Git commit: %s' % self.commitHash,
            QMessageBox.Ok)
        
    def startSecretWizard(self):
        '''Change the secret on the connected snopf device'''
        logger.info('Secret wizard started')
        w = SetSecretWizard(self)
        w.show()

    def saveOptions(self):
        '''Save current app options to persistent json'''
        logger.info('Saving options')
        self.options['last-filename'] = self.fileName
        with open('snopf_options.json', 'w') as f:
            json.dump(self.options, f)
            
    def trayIconActivated(self, reason):
        if reason != QSystemTrayIcon.Context:
            logger.info('Maximizing from tray')
            self.show()
        
    def closeEvent(self, event):
        logger.info('Minimizing to tray')
        self.hide()
        event.ignore()
        
    def cleanup(self):
        '''Clean up before closing'''
        self.websocketServer.close()
        
    def exit(self):
        self.checkCurrentDataSave()
        self.saveOptions()
        self.cleanup()
        logger.info('Exiting')
        sys.exit()
        
if __name__ == '__main__':
    app = QApplication([])
    w = SnopfManager()
    w.show()
    sys.exit(app.exec_())
