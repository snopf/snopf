# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_entry_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_NewEntryDialog(object):
    def setupUi(self, NewEntryDialog):
        if not NewEntryDialog.objectName():
            NewEntryDialog.setObjectName(u"NewEntryDialog")
        NewEntryDialog.resize(186, 122)
        self.gridLayout = QGridLayout(NewEntryDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.serviceEdit = QLineEdit(NewEntryDialog)
        self.serviceEdit.setObjectName(u"serviceEdit")

        self.gridLayout.addWidget(self.serviceEdit, 0, 0, 1, 1)

        self.accountEdit = QLineEdit(NewEntryDialog)
        self.accountEdit.setObjectName(u"accountEdit")

        self.gridLayout.addWidget(self.accountEdit, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(NewEntryDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)


        self.retranslateUi(NewEntryDialog)
        self.buttonBox.accepted.connect(NewEntryDialog.accept)
        self.buttonBox.rejected.connect(NewEntryDialog.reject)

        QMetaObject.connectSlotsByName(NewEntryDialog)
    # setupUi

    def retranslateUi(self, NewEntryDialog):
        NewEntryDialog.setWindowTitle(QCoreApplication.translate("NewEntryDialog", u"New Entry", None))
        self.serviceEdit.setPlaceholderText(QCoreApplication.translate("NewEntryDialog", u"Service", None))
        self.accountEdit.setPlaceholderText(QCoreApplication.translate("NewEntryDialog", u"Account", None))
    # retranslateUi

