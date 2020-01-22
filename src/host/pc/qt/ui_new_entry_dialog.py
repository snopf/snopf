# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_entry_dialog.ui',
# licensing of 'new_entry_dialog.ui' applies.
#
# Created: Tue Jan 21 13:52:23 2020
#      by: pyside2-uic  running on PySide2 5.12.3
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_NewEntryDialog(object):
    def setupUi(self, NewEntryDialog):
        NewEntryDialog.setObjectName("NewEntryDialog")
        NewEntryDialog.resize(312, 170)
        self.gridLayout_3 = QtWidgets.QGridLayout(NewEntryDialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(NewEntryDialog)
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.hostnameEdit = QtWidgets.QLineEdit(self.tab)
        self.hostnameEdit.setObjectName("hostnameEdit")
        self.gridLayout.addWidget(self.hostnameEdit, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.accountEdit = QtWidgets.QLineEdit(self.tab)
        self.accountEdit.setObjectName("accountEdit")
        self.gridLayout.addWidget(self.accountEdit, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.passwordLengthSpinner = QtWidgets.QSpinBox(self.tab_2)
        self.passwordLengthSpinner.setMinimum(6)
        self.passwordLengthSpinner.setMaximum(40)
        self.passwordLengthSpinner.setProperty("value", 40)
        self.passwordLengthSpinner.setObjectName("passwordLengthSpinner")
        self.gridLayout_2.addWidget(self.passwordLengthSpinner, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.passwordIterationSpinner = QtWidgets.QSpinBox(self.tab_2)
        self.passwordIterationSpinner.setMinimum(0)
        self.passwordIterationSpinner.setMaximum(9999)
        self.passwordIterationSpinner.setProperty("value", 0)
        self.passwordIterationSpinner.setObjectName("passwordIterationSpinner")
        self.gridLayout_2.addWidget(self.passwordIterationSpinner, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewEntryDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_3.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(NewEntryDialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewEntryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewEntryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewEntryDialog)
        NewEntryDialog.setTabOrder(self.hostnameEdit, self.accountEdit)
        NewEntryDialog.setTabOrder(self.accountEdit, self.tabWidget)
        NewEntryDialog.setTabOrder(self.tabWidget, self.passwordIterationSpinner)
        NewEntryDialog.setTabOrder(self.passwordIterationSpinner, self.passwordLengthSpinner)

    def retranslateUi(self, NewEntryDialog):
        NewEntryDialog.setWindowTitle(QtWidgets.QApplication.translate("NewEntryDialog", "New Entry", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("NewEntryDialog", "Hostname:", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("NewEntryDialog", "Account:", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtWidgets.QApplication.translate("NewEntryDialog", "Password Entry", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("NewEntryDialog", "Password Length:", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("NewEntryDialog", "Password Iteration:", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtWidgets.QApplication.translate("NewEntryDialog", "Additional Settings", None, -1))

