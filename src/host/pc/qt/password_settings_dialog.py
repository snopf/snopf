# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ui_password_settings_dialog import Ui_PasswordSettingsDialog

from PySide2 import QtCore, QtWidgets


class PasswordSettingsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, passwordLength=40, passwordIteration=0):
        super().__init__(parent)
        
        self.ui = Ui_PasswordSettingsDialog()
        self.ui.setupUi(self)
        
        self.passwordLength = passwordLength
        self.passwordIteration = passwordIteration
        
        self.ui.passwordLengthSpinner.setValue(passwordLength)
        self.ui.passwordIterationSpinner.setValue(passwordIteration)
        
        self.ui.buttonBox.accepted.connect(self._accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        self.setWindowTitle("Password Settings")

    def _accept(self):
        self.passwordLength = self.ui.passwordLengthSpinner.value()
        self.passwordIteration = self.ui.passwordIterationSpinner.value()
        
        self.accept()
