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
import password_generator as pg
import account_table as at
from websocket_server import SnopfWebsocketServer
import snopf_logging

import sys
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtSvg import *
import os
import json
import copy
from pathlib import Path
import resources_rc
from usb.core import USBError

logger = snopf_logging.get_logger('main')

class SnopfManager(QMainWindow):

# TODO Add last date changed entry (+ what was changed?)
# TODO change keyboard layout on device tool
# TODO read keyboard data (delay + keyboard)
# TODO test cases with mockup
# TODO undo / redo
# TODO make backups of loaded account tables
# TODO autosave every n minutes / after every new entry
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
        self.ui.accountTableWidget.accountSelected.connect(self.accountSelected)
        self.ui.commitChangesButton.clicked.connect(self.commitChanges)
        self.ui.deleteEntryButton.clicked.connect(self.deleteEntry)
        self.ui.requestPasswordButton.clicked.connect(lambda x: self.requestPassword())
        self.lastTabIndex = 0
        self.ui.tabWidget.currentChanged.connect(self.tabChanged)
        
        # Keymap editing
        self.ui.keymapEdit.keymapChanged.connect(
            lambda remKeys: self.ui.remainingKeysEdit.setText(''.join(remKeys)))
        self.ui.addLowercaseButton.clicked.connect(self.ui.keymapEdit.addLowercase)
        self.ui.addUppercaseButton.clicked.connect(self.ui.keymapEdit.addUppercase)
        self.ui.addNumericalButton.clicked.connect(self.ui.keymapEdit.addNumerical)
        self.ui.addSpecialButton.clicked.connect(self.ui.keymapEdit.addSpecial)
        self.ui.applyKeymapButton.clicked.connect(self.selectPresetKeymap)
        self.fillKeymapCombobox()
        
        # Appendix
        self.addAppendixValidator()
        
        # Password settings
        self.ui.lengthSpinner.setMinimum(pg.MIN_PW_LENGTH)
        self.ui.lengthSpinner.setMaximum(pg.MAX_PW_LENGTH)
        self.ui.lengthSpinner.setValue(pg.DEFAULT_PW_LENGTH)
        
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
        
        # Websocket server
        self.websocketServer = SnopfWebsocketServer(self, self.options['websocket-port'])
        self.websocketServer.deviceAvailableRequest.connect(
            lambda ws: self.websocketServer.sendDeviceAvailable(ws, usb_comm.is_device_available()))
        self.websocketServer.accountsRequest.connect(
            lambda ws: self.websocketServer.sendAccountsList(ws, self.getAccounts()))
        self.websocketServer.passwordRequest.connect(self.requestPassword)
    
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
    
    def fillKeymapCombobox(self):
        for name in pg.keymap_names.keys():
            self.ui.selectKeymapComboBox.addItem(name)
            
    def selectPresetKeymap(self, index):
        km = pg.keymaps[pg.keymap_names[self.ui.selectKeymapComboBox.currentText()]]
        self.ui.keymapEdit.clear()
        for char in km:
            self.ui.keymapEdit.insert(pg.KEY_TABLE[char])
            
    def addAppendixValidator(self):
        '''Validator for appendix input that only allows input from snopf character table'''
        regex = '^['
        # Add all lowercase + uppercase + digits
        for i in range(pg.PW_GROUP_BOUND_DIGIT):
            regex += str(pg.KEY_TABLE[i])
        # Add special characters
        for i in range(pg.PW_GROUP_BOUND_DIGIT, pg.PW_GROUP_BOUND_SPECIAL):
            regex += '\\' + str(pg.KEY_TABLE[i])
        regex += ']*'
        validator = QRegExpValidator(QRegExp(regex), self)
        self.ui.pwAppendixEdit.setValidator(validator)
        
    def getRules(self):
        '''Get rules integer from selected checkboxes'''
        rules = 0
        if self.ui.includeLowercaseCB.isChecked():
            rules += pg.PW_RULE_INCLUDE_LOWERCASE
        if self.ui.includeUppercaseCB.isChecked():
            rules += pg.PW_RULE_INCLUDE_UPPERCASE
        if self.ui.includeNumericalCB.isChecked():
            rules += pg.PW_RULE_INCLUDE_DIGIT
        if self.ui.includeSpecialCB.isChecked():
            rules += pg.PW_RULE_INCLUDE_SPECIAL
        if self.ui.avoidRepCB.isChecked():
            rules += pg.PW_RULE_NO_REP
        if self.ui.avoidSeqCB.isChecked():
            rules += pg.PW_RULE_NO_SEQ
        return rules
    
    def setRulesUi(self, rules):
        '''Set checkboxes according to rules'''
        self.ui.includeLowercaseCB.setChecked(bool(rules & pg.PW_RULE_INCLUDE_LOWERCASE))
        self.ui.includeUppercaseCB.setChecked(bool(rules & pg.PW_RULE_INCLUDE_UPPERCASE))
        self.ui.includeNumericalCB.setChecked(bool(rules & pg.PW_RULE_INCLUDE_DIGIT))
        self.ui.includeSpecialCB.setChecked(bool(rules & pg.PW_RULE_INCLUDE_SPECIAL))
        self.ui.avoidRepCB.setChecked(bool(rules & pg.PW_RULE_NO_REP))
        self.ui.avoidSeqCB.setChecked(bool(rules & pg.PW_RULE_NO_SEQ))
        
    def updateEntropy(self, *args, **kwargs):
        '''Update the entropy field value'''
        if not self.selectedEntry:
            self.ui.entropyEdit.setText('')
            return
        entropy = pg.calc_entropy_password(self.selectedEntry['keymap'],
                                           self.selectedEntry['password_length'])
        self.ui.entropyEdit.setText('{:0.2f}'.format(entropy))
        self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(255, 255, 255); }')
        self.ui.entropyEdit.setToolTip('')
        if self.selectedEntry['rules'] != 0:
            self.ui.entropyEdit.setText('\N{WARNING SIGN} {:0.2f}'.format(entropy))
            self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(240, 125, 125); }')
            self.ui.entropyEdit.setToolTip('Warning: The entropy might be lower than shown due to selected rules.')
            
    def initNewAccountTable(self):
        '''Initialize tree widget with new account table entries'''
        self.ui.accountTableWidget.initNewAccountTable(self.accountTable)
        # Enable account table editing
        self.ui.actionNewEntry.setEnabled(True)
        self.ui.actionDeleteEntry.setEnabled(True)
        self.ui.actionSave.setEnabled(True)
        
    def accountSelected(self, service, account):
        '''Slot for activated item in account table tree widget'''
        self.checkCommit()
        self.selectedService = service
        self.selectedAccount = account
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
            self.ui.pwAppendixEdit.insert(pg.KEY_TABLE[a])
        self.ui.keymapEdit.clear()
        for key in self.selectedEntry['keymap']:
            self.ui.keymapEdit.insert(pg.KEY_TABLE[key])
            
    def tabChanged(self, index):
        if not self.selectedEntry:
            return
        # Not really a change
        if index == self.lastTabIndex:
            return
        # Check whether the changes we made are compatible
        keymap = pg.keys_to_keymap(self.ui.keymapEdit.text())
        if (not pg.check_keymap_valid(keymap)
            or not pg.check_rules_valid(self.selectedEntry['rules'], keymap)):
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
        if not self.selectedEntry:
            return
        self.selectedEntry['password_length'] = self.ui.lengthSpinner.value()
        self.selectedEntry['password_iteration'] = self.ui.iterationSpinner.value()
        self.selectedEntry['rules'] = self.getRules()
        self.selectedEntry['keymap'] = pg.keys_to_keymap(self.ui.keymapEdit.text())
        self.selectedEntry['comment'] = self.ui.commentEdit.text()
        self.selectedEntry['appendix'] = [pg.KEY_TABLE.index(c) for c in self.ui.pwAppendixEdit.text()]
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
        service = self.ui.accountTableWidget.currentService()
        account = self.ui.accountTableWidget.currentAccount()
        if self.askUser('Remove Entry', 
                        'Do you really want to remove the entry %s / %s' % (service, account)):
            logger.info('Deleting selected item')
            
            self.ui.accountTableWidget.deleteEntry(service, account)
            self.accountTable[service].pop(account)
            if len(self.accountTable[service]) == 0:
                self.accountTable.pop(service)
                
            self.selectedEntry = None

    def getAccounts(self):
        '''Just return a hostname: accounts dictionary without additional information (passsword length etc.)'''
        return {hostname: [account for account in self.accountTable[hostname].keys()]
                for hostname in self.accountTable.keys()}
    
    def entryExists(self, service, account):
        '''Check whether a service/account tuple already exists'''
        return service in self.accountTable and account in self.accountTable[service]
    
    def addEntry(self, service, account):
        '''Create a new entry in the account table using default values'''
        if self.entryExists(service, account):
            logger.warning('Attempted to create existing entry')
            return
        if not service in self.accountTable:
            self.accountTable[service] = {}
            
        self.accountTable[service][account] = at.create_entry()
        self.ui.accountTableWidget.addItem(service, account)
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
        self.initNewAccountTable()
        self.fileName = None
        self.dataChanged = False
        self.selectedService = None
        self.selectedAccount = None
        self.selectedEntry = None
        
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
        self.initNewAccountTable()
    
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
            
    def requestPassword(self, service=None, account=None, makeNewEntry=False):
        '''
        Make a password request using the given service and account combination.
        If no service and account are submitted the currently selected item from the account table
        widget is used
        If makeNewEntry is set to True a non-existing service-account tuple will be added to the
        account table if necessary
        '''
        if not service:
            service = self.selectedService
            account = self.selectedAccount
        self.checkCommit()
        
        if not usb_comm.is_device_available():
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                 QMessageBox.Ok)
            return
        
        if not self.entryExists(service, account):
            logger.info('Password request with unknown service-account combination')
            if makeNewEntry:
                logger.info('Creating new entry')
                self.addEntry(service, account)
            else:
                logger.warning('Unknown service-account but no new entry created')
                return
        
        password_iteration = self.accountTable[service][account]['password_iteration']
        password_length = self.accountTable[service][account]['password_length']
        rules = self.accountTable[service][account]['rules']
        appendix = self.accountTable[service][account]['appendix']
        keymap = self.accountTable[service][account]['keymap']
        
        req_msg = requests.combine_standard_request(service.encode(), account.encode(),
                                                    self.masterPassphrase, password_iteration)
        
        req = usb_comm.build_request_message(req_msg, password_length, rules, appendix, keymap)
        dev = usb_comm.get_standard_device()
        if not dev:
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.', QMessageBox.Ok)
            return
        
        try:
            usb_comm.send_message(dev, req)
        except USBError as e:
            QMessageBox.critical(self, 'USB error', 'Cannot send to USB device. %s' % str(e), 
                                 QMessageBox.Ok)
            logger.error('USB Error', exc_info=sys.exc_info())
        
    def setKeyboardDelay(self):
        '''Set the keyboard delay for a connected snopf device'''
        delay, ok = QInputDialog.getInt(self, 'Set Keyboard Delay', 'Delay in ms', 10, 0, 255)
        if ok:
            if not usb_comm.is_device_available():
                QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                     QMessageBox.Ok)
                return
            dev = usb_comm.get_standard_device()
            msg = usb_comm.build_set_keyboard_delay_message(delay)
            usb_comm.send_message(dev, msg)
            QMessageBox.information(self, 'Setting Keyboard Delay',
                                    'Press the Button on the device to set the new delay.',
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
