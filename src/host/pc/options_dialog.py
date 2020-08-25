#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Dialog for option editing
'''

from ui_options_dialog import Ui_OptionsDialog

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import logging
from add_new_client_dialog import AddNewClientDialog
import copy

logger = logging.getLogger('options-dialog')

class OptionsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_OptionsDialog()
        self.ui.setupUi(self)
        logger.info('Options dialog started')

        self.options = copy.deepcopy(parent.options)

        self.ui.websocketPortSpinBox.setValue(self.options['websocket-port'])
        self.ui.websocketEnableCheckbox.setChecked(self.options['websocket-enabled'])

        self.whiteListSeparator = ' | '
        self.webSocketWhitelist = []
        for origin in self.options['websocket-whitelist'].keys():
            self.webSocketWhitelist.append(origin + self.whiteListSeparator
                                           + self.options['websocket-whitelist'][origin])
        model = QStringListModel()
        model.setStringList(self.webSocketWhitelist)
        self.ui.websocketWhiteListView.setModel(model)

        self.ui.websocketAddClientButton.clicked.connect(self.websocketAddClient)
        self.ui.websocketRemoveClientButton.clicked.connect(self.websocketRemoveClient)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def websocketAddClient(self):
        diag = AddNewClientDialog(self)
        if diag.exec_() == QDialog.Accepted:
            if diag.origin() in self.options['websocket-whitelist'].keys():
                logger.info('Trying to add second entry for websocket origin %s' % diag.origin())
                QMessageBox.warning(self, 'Entry exists', 'Entry for origin already exists',
                                    QMessageBox.Ok)
                return
            self.options['websocket-whitelist'][diag.origin()] = diag.originId()
            self.webSocketWhitelist.append(diag.origin() + self.whiteListSeparator + diag.originId())
            self.ui.websocketWhiteListView.model().setStringList(self.webSocketWhitelist)

    def websocketRemoveClient(self):
        index = self.ui.websocketWhiteListView.currentIndex().row()
        entry = self.webSocketWhitelist.pop(index)
        self.options['websocket-whitelist'].pop(self.websocketGetOrigin(entry))
        self.ui.websocketWhiteListView.model().setStringList(self.webSocketWhitelist)

    def websocketGetOrigin(self, entryString):
        return entryString.split(' | ')[0]

    def websocketGetId(self, entryString):
        return entryString.split(' | ')[1]

    def getOptions(self):
        self.options['websocket-enabled'] = self.ui.websocketEnableCheckbox.isChecked()
        self.options['websocket-port'] = self.ui.websocketPortSpinBox.value()
        return self.options
