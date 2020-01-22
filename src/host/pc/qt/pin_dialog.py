# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

from ui_pin_dialog import Ui_PinDialog

from PySide2 import QtCore, QtWidgets, QtGui

class PinDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui = Ui_PinDialog()
        self.ui.setupUi(self)
