#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
QT Wizard for setting the secret 
'''

# TODO dice rolls etc.

from ui_set_secret_wizard import Ui_SetSecretWizard

import mnemonic
import requests
import usb_comm
import password_generator as pg
import snopf_logging

from PySide2.QtCore import *
from PySide2.QtWidgets import *

import os

logger = snopf_logging.get_logger('set-secret-wizard')

class SetSecretWizard(QWizard):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SetSecretWizard()
        self.ui.setupUi(self)
        logger.info('Secret Setting Wizard started')
        
        self.mnemonic = []
        
        for i in self.pageIds():
            self.page(i).setCommitPage(True)
            self.page(i).setButtonText(QWizard.CommitButton, 'Next')
            
        self.rejected.connect(lambda: logger.info('Cancelled'))
        
    def initializePage(self, _id):
        logger.info('Initializing page with id %d' % _id)
        if (_id) == 1:
            if self.ui.createNewMnemonicRadio.isChecked():
                logger.info('Creating new mnemonic from urandom')
                self.mnemonic = mnemonic.to_mnemonic(os.urandom(32))
            self.ui.mnemonicEdit.setPlainText(' '.join(self.mnemonic))
                        
        elif (_id) == 2:
            logger.info('Writing secret')
            if not usb_comm.is_device_available():
                logger.info('No device found')
                QMessageBox.critical(self, 'Device not found',
                                               'No Snopf device found.',
                                               QMessageBox.Ok)
                self.reject()
                return
            
            self.dev = usb_comm.get_standard_device()
            usb_comm.write_secret(self.dev, mnemonic.to_entropy(self.mnemonic))
        
        elif (_id) == 3:
            logger.info('Starting challenge response')
            rq = os.urandom(16)
            msg = usb_comm.build_request(rq, 42, 0, [], pg.keymaps['all'])
            usb_comm.send_message(self.dev, msg)
            expected = pg.get_mapped_password(
                mnemonic.to_entropy(self.mnemonic), rq, 42, 0, pg.keymaps['all'])
            self.ui.expectedPasswordLabel.setText(pg.map_to_characters(expected))
            
    def validateCurrentPage(self):
        if self.currentId() == 1:
            self.mnemonic = self.ui.mnemonicEdit.toPlainText().split()
            if not len(self.mnemonic) == 24:
                logger.warning('Mnemonic too short')
                QMessageBox.information(
                    self, 'Invalid Mnemonic',
                    'The Mnemonic must be 24 words long.',
                    QMessageBox.Ok)
                return False
            try:
                e = mnemonic.to_entropy(self.mnemonic)
            except Exception:
                logger.warning('Mnemonic invalid')
                QMessageBox.information(
                    self, 'Invalid Mnemonic',
                    'Mnemonic is invalid.',
                    QMessageBox.Ok)
                return False
            return True
        
        if self.currentId() == 3:
            logger.error('Checking challenge response')
            if self.ui.expectedPasswordLabel.text() != self.ui.passwordEdit.text():
                logger.error('Challenge response failed %s != %s' % (
                    self.ui.expectedPasswordLabel.text(), self.ui.passwordEdit.text()))
                QMessageBox.information(
                    self, 'Invalid Passwords',
                    'The passwords do not match. Something went wrong.',
                    QMessageBox.Ok)
                return False
            logger.error('Check ok')
            return True
        
        return True
