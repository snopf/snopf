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
import keyboard_layouts
from account_table_model import AccountTableModel, AccountTableViewProxyModel

import logging
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
import appdirs

logger = logging.getLogger('main')

class SnopfManager(QMainWindow):

# TODO Add last date changed entry (+ what was changed?)
# TODO test cases with mockup
# TODO undo / redo
# TODO make backups of loaded account tables
# TODO autosave every n minutes / after every new entry
# TODO secure websocket connection (whitelisting)
# TODO option for allowing/disallowing new entries from websockets
    
    def __init__(self, configPath=None):
        super().__init__()
        self.ui = Ui_SnopfManager()
        self.ui.setupUi(self)
        
        # Log uncaught exceptions
        sys.excepthook = self.logException
        
        logger.info('Application started')
        
        # Setting up directories for app
        self.user_data_dir = appdirs.user_data_dir('snopf-manager', 'snopf')
        if not os.path.exists(self.user_data_dir):
            logger.info('Creating user data dir: %s' % str(self.user_data_dir))
            os.makedirs(self.user_data_dir)
            
        self.user_config_dir = configPath
        if not self.user_config_dir:
            self.user_config_dir = appdirs.user_config_dir('snopf-manager', 'snopf')
        if not os.path.exists(self.user_config_dir):
            logger.info('Creating user config dir: %s' % str(self.user_config_dir))
            os.makedirs(self.user_config_dir)
        logger.info('Working with user config dir: %s' % str(self.user_config_dir))
            
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
        
        # Master passphrase for current account table
        self.masterPassphrase = None
        
        # Filename of open account table
        self.__fileName = None
        
        # Model for Account Table data
        self.atModel = None
        # Mapper for widgets <> model
        self.atMapper = None
        
        # Software version
        self.commitHash = get_commit_hash()
        logger.info('Git hash: %s' % self.commitHash)
        
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
        self.ui.actionSetKeyboardLayout.triggered.connect(self.setKeyboardLayout)
        
        # Account table
        self.ui.deleteEntryButton.clicked.connect(self.deleteEntry)
        self.ui.requestPasswordButton.clicked.connect(lambda x: self.requestPassword())
        self.ui.accountTableView.activated.connect(self.entrySelected)
        self.ui.entropyEdit.textChanged.connect(self.decorateEntropy)
        
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
        
        # Load snopf options file
        self.loadOptions()
        
        # Load last loaded file if available
        if self.options['last-filename']:
            try:
                self.openAccountTable(self.options['last-filename'])
            except FileNotFoundError:
                logger.warning('Last file % s not found, skipping auto load' % lastFileName)
        
        # Init websocket server
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
        '''Load options from options file'''
        self.options_file_path = os.path.join(self.user_config_dir, 'snopf_options.json')
        if not Path(self.options_file_path).exists():
            logger.info('snopf_options not found, creating new file')
            with open(self.options_file_path, 'w') as f:
                json.dump({}, f)
        with open(self.options_file_path, 'r') as f:
            logger.info('loading snopf options')
            self.options = json.load(f)
        
        # Initialize to default values if not set
        self.options['last-filename'] = self.options.get('last-filename', None)
        self.options['websocket-port'] = self.options.get('websocket-port', 60100)
    
    def getFileName(self):
        '''Getter for filename property'''
        return self.__fileName
    
    def setFileName(self, fileName):
        '''Setter for filename property'''
        self.__fileName = fileName
        self.setWindowTitle('Snopf %s' % self.__fileName)
    
    # Filename of currently loaded file
    fileName = property(getFileName, setFileName)
    
    def fillKeymapCombobox(self):
        '''Fill Keymap combobox with presets, e.h. hex, alphanumerical etc'''
        for name in pg.keymap_names.keys():
            self.ui.selectKeymapComboBox.addItem(name)
            
    def selectPresetKeymap(self, index):
        '''Fill in corresponding keymap'''
        self.ui.keymapEdit.setKeymap(pg.keymaps[pg.keymap_names[self.ui.selectKeymapComboBox.currentText()]])
            
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
        self.ui.appendixEdit.setValidator(validator)
        
    def decorateEntropy(self, value):
        '''Set warning for entropy edit if necessary'''
        if value.startswith('\N{WARNING SIGN}'):
            self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(240, 125, 125); }')
            self.ui.entropyEdit.setToolTip('Warning: The entropy might be lower than shown due to selected rules.')
        else:
            self.ui.entropyEdit.setStyleSheet('QLineEdit { background: rgb(255, 255, 255); }')
            self.ui.entropyEdit.setToolTip('')
            
    def initNewAccountTable(self, accountTable):
        '''Initialize models and widgets for new account table'''
        self.atModel = AccountTableModel(accountTable, self)
        self.atModel.invalidNewData.connect(
            lambda s: QMessageBox.warning(self, 'Invalid change', s, QMessageBox.Ok))
        proxyModel = AccountTableViewProxyModel(self)
        proxyModel.setSourceModel(self.atModel)
        self.ui.accountTableView.setModel(proxyModel)
        self.atMapper = QDataWidgetMapper()
        self.atMapper.setModel(self.atModel)
        self.atMapper.addMapping(self.ui.serviceEdit, self.atModel.keyColumns['service'])
        self.atMapper.addMapping(self.ui.accountEdit, self.atModel.keyColumns['account'])
        self.atMapper.addMapping(self.ui.commentEdit, self.atModel.keyColumns['comment'])
        self.atMapper.addMapping(self.ui.lengthSpinner, self.atModel.keyColumns['password_length'])
        self.atMapper.addMapping(self.ui.iterationSpinner, self.atModel.keyColumns['password_iteration'])
        self.atMapper.addMapping(self.ui.includeLowercaseCB, self.atModel.keyColumns['include_lowercase'])
        self.atMapper.addMapping(self.ui.includeUppercaseCB, self.atModel.keyColumns['include_uppercase'])
        self.atMapper.addMapping(self.ui.includeDigitCB, self.atModel.keyColumns['include_digit'])
        self.atMapper.addMapping(self.ui.includeSpecialCB, self.atModel.keyColumns['include_special'])
        self.atMapper.addMapping(self.ui.avoidRepCB, self.atModel.keyColumns['no_repetitions'])
        self.atMapper.addMapping(self.ui.avoidSeqCB, self.atModel.keyColumns['no_sequences'])
        self.atMapper.addMapping(self.ui.keymapEdit, self.atModel.keyColumns['keymap'], b'keymap')
        self.atMapper.addMapping(self.ui.appendixEdit, self.atModel.keyColumns['appendix'], b'keys')
        self.atMapper.addMapping(self.ui.entropyEdit, self.atModel.keyColumns['entropy'])
        self.atMapper.setSubmitPolicy(QDataWidgetMapper.AutoSubmit)
        
        # Enable account table editing
        self.ui.actionNewEntry.setEnabled(True)
        self.ui.actionDeleteEntry.setEnabled(True)
        self.ui.actionSave.setEnabled(True)
        self.ui.actionSaveAs.setEnabled(True)
        
        self.ui.tabWidget.setCurrentIndex(0)
        if len(accountTable):
            self.ui.accountTableView.selectRow(0)
            self.entrySelected(self.ui.accountTableView.currentIndex())
            
    def entrySelected(self, _index):
        index = self.ui.accountTableView.model().mapToSource(_index)
        self.atMapper.setCurrentModelIndex(index)
        
    def mapSelectedEntryIndex(self):
        '''Map selected entry of account table view to model index'''
        return self.ui.accountTableView.model().mapToSource(self.ui.accountTableView.currentIndex())
    
    def deleteEntry(self):
        '''Delete the entry from the account table'''
        self.atModel.removeRow(self.mapSelectedEntryIndex())
        
    def getAccounts(self):
        '''Just return a service: accounts dictionary without additional information (passsword length etc.)'''
        return self.atModel.getServiceAccounts()
            
    def newEntry(self):
        '''Create a new entry'''
        d = NewEntryDialog()
        if d.exec_() == QDialog.Accepted:
            service = d.service()
            account = d.account()
            
            try:
                self.atModel.newEntry(service, account)
            except KeyError:
                QMessageBox.critical(self, 'Entry exists',
                                     'An entry for the same service and account already exists',
                                     QMessageBox.Ok)
                return
            
    def checkCurrentDataSave(self):
        '''Check if current account table has been changed and whether changes should be saved'''
        if self.atModel and self.atModel.tableChanged():
            if self.askUser('Account table has been changed',
                            'Save current account table?'):
                logger.info('Saving current account table')
                self.saveAccountTable()
        
    def newAccountTable(self):
        '''Create an empty account table'''
        # Set a master key for the new account table
        passphrase_one = self.getPassphrase()
        if passphrase_one == None:
            # dialog cancelled
            return
        if passphrase_one == b'':
            # empty passphrase chosen
            msg = 'Do you really want to create a new account table without a passphrase?'
            if not self.askUser('Empty Passphrase', msg):
                return
        passphrase_two = self.getPassphrase('Repeat Passphrase')
        if not passphrase_one == passphrase_two:
            QMessageBox.critical(self, 'Wrong Passphrase', 'Passphrases do not match',
                                 QMessageBox.Ok)
            return
        self.masterPassphrase = passphrase_one
        self.initNewAccountTable(at.new_account_table())
        self.fileName = None
        
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
            if self.fileName:
                path = os.path.dirname(self.fileName)
            else:
                path = self.user_data_dir        
            fileName,_ = QFileDialog.getOpenFileName(
                self, 'Open Account Table', path, 'Account table (*.snopf)')
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
            accountTable = json.loads(data['table'])
        except json.JSONDecodeError:
            logger.error('Could not decode json', exc_info=sys.exc_info())
            QMessageBox.critical(self, 'Error', 'Cannot read file', QMessageBox.Ok)
            return
        # All went well, update data to loaded table
        self.masterPassphrase = passphrase
        self.fileName = fileName
        self.initNewAccountTable(accountTable)
    
    def saveAccountTable(self):
        '''Save curent account table to hard disk'''
        if not self.fileName:
            self.saveAccountTableAs()
            return
            
        if not self.fileName.endswith('.snopf'):
            self.fileName += '.snopf'
        # We have to update the mapping even if we don't change focus
        self.atMapper.submit()
        try:
            with open(self.fileName, 'wb') as f:
                at.save_account_table(f, self.atModel.getSaveData(), self.masterPassphrase,
                                      self.commitHash.encode()[:at.GIT_HASH_SIZE])
                logger.info('Saving file')
        except IOError:
            logger.error('Could not save to file', exc_info=sys.exc_info())
            QMessageBox.critical(self, 'Error', 'Cannot write to file %s' % self.fileName,
                                 QMessageBox.Ok)
            return
        
        self.atModel.commitData()
        
        
    def saveAccountTableAs(self):
        '''Save under new name'''
        if self.fileName:
            path = os.path.dirname(self.fileName)
        else:
            path = self.user_data_dir
        fileName,_ = QFileDialog.getSaveFileName(self, 'Save Account Table',
                                                 self.user_data_dir, 'Account table (*.snopf)')
        if not fileName:
            return
        self.fileName = fileName
        self.saveAccountTable()
        
    def requestPassword(self, service=None, account=None, makeNewEntry=False):
        '''
        Make a password request using the given service and account combination.
        If no service and account are submitted the currently selected item from the account table
        widget is used
        If makeNewEntry is set to True a non-existing service-account tuple will be added to the
        account table if necessary
        '''
        if not service:
            entry = self.atModel.table[self.mapSelectedEntryIndex().row()]
        else:
            try:
                entry = self.atModel.getEntry(service, account)
            except KeyError:
                logger.info('Password request with unknown service-account combination')
                if makeNewEntry:
                    logger.info('Creating new entry')
                    self.atModel.newEntry(service, account)
                    entry = self.atModel.getEntry(service, account)
                else:
                    logger.warning('Unknown service-account but no new entry created')
                    return
                
        if not usb_comm.is_device_available():
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                 QMessageBox.Ok)
            return
        
        req_msg = requests.combine_standard_request(entry['service'].encode(),
                                                    entry['account'].encode(),
                                                    self.masterPassphrase,
                                                    entry['password_iteration'])
        
        req = usb_comm.build_request_message(req_msg, entry['password_length'],
                                             pg.bool_to_rules(entry), entry['appendix'],
                                             entry['keymap'])
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
    
    def setKeyboardLayout(self):
        '''Set a new keyboard layout on a connected Snopf device'''
        fileName,_ = QFileDialog.getOpenFileName(self, 'Open Keyboard Layout File',
                                                 str(Path.home()), 'Json (*.json)')
        if not fileName:
            return
        layout = json.load(open(fileName))
        try:
            keyboard_layouts.check_keyboard_layout(layout)
        except ValueError as e:
            logger.info('Invalid keyboard layout file. Reason: %s' % e)
            QMessageBox.critical(self, 'Invalid Keyboard Layout File', str(e), QMessageBox.Ok)
            return
        bytesLayout = keyboard_layouts.to_bytes(layout)
        if not usb_comm.is_device_available():
            QMessageBox.critical(self, 'Device not found', 'The device is not plugged in.',
                                 QMessageBox.Ok)
            return
        dev = usb_comm.get_standard_device()
        msg = usb_comm.build_new_keyboard_keycodes_message(bytesLayout)
        usb_comm.send_message(dev, msg)
        QMessageBox.information(self, 'Setting Keyboard Layout',
                                'Press the Button on the device for five seconds to set new keyboard layout.',
                                QMessageBox.Ok)
        logger.info('New Keyboard layout set')
    
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
        with open(self.options_file_path, 'w') as f:
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
