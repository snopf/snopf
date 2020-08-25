#!/usr/bin/env python3

# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

'''
Dialog for adding a new client to the websocket whitelist
'''

from ui_add_new_client_dialog import Ui_AddNewClientDialog

from PySide2.QtCore import *
from PySide2.QtWidgets import *
import logging


logger = logging.getLogger('options-dialog')

class AddNewClientDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_AddNewClientDialog()
        self.ui.setupUi(self)
        logger.info('Add new client dialog started')

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def origin(self):
        return self.ui.originEdit.text()

    def originId(self):
        return self.ui.idEdit.text()
