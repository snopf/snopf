# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'password_settings_dialog.ui',
# licensing of 'password_settings_dialog.ui' applies.
#
# Created: Tue Jan 21 13:52:23 2020
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_PasswordSettingsDialog(object):
    def setupUi(self, PasswordSettingsDialog):
        PasswordSettingsDialog.setObjectName("PasswordSettingsDialog")
        PasswordSettingsDialog.resize(235, 124)
        self.gridLayout_2 = QtWidgets.QGridLayout(PasswordSettingsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(PasswordSettingsDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.passwordLengthSpinner = QtWidgets.QSpinBox(PasswordSettingsDialog)
        self.passwordLengthSpinner.setMinimum(6)
        self.passwordLengthSpinner.setMaximum(40)
        self.passwordLengthSpinner.setProperty("value", 40)
        self.passwordLengthSpinner.setObjectName("passwordLengthSpinner")
        self.gridLayout.addWidget(self.passwordLengthSpinner, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(PasswordSettingsDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.passwordIterationSpinner = QtWidgets.QSpinBox(PasswordSettingsDialog)
        self.passwordIterationSpinner.setMinimum(0)
        self.passwordIterationSpinner.setMaximum(99999999)
        self.passwordIterationSpinner.setProperty("value", 0)
        self.passwordIterationSpinner.setObjectName("passwordIterationSpinner")
        self.gridLayout.addWidget(self.passwordIterationSpinner, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(PasswordSettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(PasswordSettingsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), PasswordSettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), PasswordSettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PasswordSettingsDialog)

    def retranslateUi(self, PasswordSettingsDialog):
        PasswordSettingsDialog.setWindowTitle(QtWidgets.QApplication.translate("PasswordSettingsDialog", "Password Settings", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("PasswordSettingsDialog", "Password length:", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("PasswordSettingsDialog", "Password iteration:", None, -1))

