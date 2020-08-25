# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_new_client_dialog.ui'
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


class Ui_AddNewClientDialog(object):
    def setupUi(self, AddNewClientDialog):
        if not AddNewClientDialog.objectName():
            AddNewClientDialog.setObjectName(u"AddNewClientDialog")
        AddNewClientDialog.resize(595, 172)
        self.gridLayout = QGridLayout(AddNewClientDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(AddNewClientDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.originEdit = QLineEdit(AddNewClientDialog)
        self.originEdit.setObjectName(u"originEdit")

        self.verticalLayout.addWidget(self.originEdit)

        self.label_2 = QLabel(AddNewClientDialog)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.idEdit = QLineEdit(AddNewClientDialog)
        self.idEdit.setObjectName(u"idEdit")

        self.verticalLayout.addWidget(self.idEdit)

        self.buttonBox = QDialogButtonBox(AddNewClientDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(AddNewClientDialog)
        self.buttonBox.accepted.connect(AddNewClientDialog.accept)
        self.buttonBox.rejected.connect(AddNewClientDialog.reject)

        QMetaObject.connectSlotsByName(AddNewClientDialog)
    # setupUi

    def retranslateUi(self, AddNewClientDialog):
        AddNewClientDialog.setWindowTitle(QCoreApplication.translate("AddNewClientDialog", u"Add New Client", None))
        self.label.setText(QCoreApplication.translate("AddNewClientDialog", u"Origin", None))
        self.label_2.setText(QCoreApplication.translate("AddNewClientDialog", u"ID", None))
    # retranslateUi

