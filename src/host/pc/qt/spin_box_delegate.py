# Copyright (c) 2019-2020 Hajo Kortmann <hajo.kortmann@gmx.de>
# License: GNU GPL v2 (see License.txt)

"""
Delegate for the password length and iteration settings in the table view
"""

import sys
sys.path.append('..')

import usb_comm
from account_table_model import columnToKey

from PySide2 import QtCore, QtWidgets

class SpinBoxDelegate(QtWidgets.QItemDelegate):
    
    def createEditor(self, parent, option, index):
        editor = QtWidgets.QSpinBox(parent)
        key = columnToKey(index.column())
        if key == 'password_length':
            editor.setMinimum(usb_comm.MIN_PW_LENGTH)
            editor.setMaximum(usb_comm.MAX_PW_LENGTH)
        if key == 'password_iteration':
            editor.setMinimum(0)
            editor.setMaximum(255)
        return editor
    
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setValue(value)
        
    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, QtCore.Qt.EditRole)
        
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
