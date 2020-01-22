# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pin_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_PinDialog(object):
    def setupUi(self, PinDialog):
        if PinDialog.objectName():
            PinDialog.setObjectName(u"PinDialog")
        PinDialog.resize(216, 134)
        self.gridLayout = QGridLayout(PinDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pinEdit = QLineEdit(PinDialog)
        self.pinEdit.setObjectName(u"pinEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pinEdit.sizePolicy().hasHeightForWidth())
        self.pinEdit.setSizePolicy(sizePolicy)
        self.pinEdit.setMinimumSize(QSize(200, 0))
        self.pinEdit.setMaximumSize(QSize(50, 16777215))
        self.pinEdit.setEchoMode(QLineEdit.Password)
        self.pinEdit.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.pinEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.line = QFrame(PinDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.savePinCheckBox = QCheckBox(PinDialog)
        self.savePinCheckBox.setObjectName(u"savePinCheckBox")

        self.verticalLayout.addWidget(self.savePinCheckBox)

        self.line_2 = QFrame(PinDialog)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.buttonBox = QDialogButtonBox(PinDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(PinDialog)
        self.buttonBox.accepted.connect(PinDialog.accept)
        self.buttonBox.rejected.connect(PinDialog.reject)

        QMetaObject.connectSlotsByName(PinDialog)
    # setupUi

    def retranslateUi(self, PinDialog):
        PinDialog.setWindowTitle(QCoreApplication.translate("PinDialog", u"Dialog", None))
        self.pinEdit.setText("")
        self.pinEdit.setPlaceholderText(QCoreApplication.translate("PinDialog", u"Pin", None))
        self.savePinCheckBox.setText(QCoreApplication.translate("PinDialog", u"Save Pin for Session", None))
    # retranslateUi

