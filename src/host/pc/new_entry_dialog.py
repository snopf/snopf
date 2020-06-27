# Copyright (c) 2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ui_new_entry_dialog import Ui_NewEntryDialog

from PySide2 import QtCore, QtWidgets 

class NewEntryDialog(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_NewEntryDialog()
        self.ui.setupUi(self)
        
        self.ui.accountEdit.returnPressed.connect(self.accept)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.focusNextChild()
            return
        super().keyPressEvent(event)
        
    def service(self):
        return str(self.ui.serviceEdit.text())
    
    def account(self):
        return str(self.ui.accountEdit.text())
