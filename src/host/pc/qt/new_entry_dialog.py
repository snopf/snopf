# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ui_new_entry_dialog import Ui_NewEntryDialog

from PySide2 import QtCore, QtWidgets 

class NewEntryDialog(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_NewEntryDialog()
        self.ui.setupUi(self)
        
    def getNewEntry(self):
        return {
            'hostname': str(self.ui.hostnameEdit.text()),
            'account': str(self.ui.accountEdit.text()),
            'password_length': int(self.ui.passwordLengthSpinner.value()),
            'password_iteration': int(self.ui.passwordIterationSpinner.value())
            }
