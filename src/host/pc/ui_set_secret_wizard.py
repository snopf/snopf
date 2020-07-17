# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'set_secret_wizard.ui'
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


class Ui_SetSecretWizard(object):
    def setupUi(self, SetSecretWizard):
        if not SetSecretWizard.objectName():
            SetSecretWizard.setObjectName(u"SetSecretWizard")
        SetSecretWizard.resize(500, 360)
        SetSecretWizard.setWizardStyle(QWizard.ClassicStyle)
        self.page1 = QWizardPage()
        self.page1.setObjectName(u"page1")
        self.gridLayout_2 = QGridLayout(self.page1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.useExistingMnemonicRadio = QRadioButton(self.page1)
        self.useExistingMnemonicRadio.setObjectName(u"useExistingMnemonicRadio")
        self.useExistingMnemonicRadio.setChecked(True)

        self.gridLayout_2.addWidget(self.useExistingMnemonicRadio, 0, 0, 1, 1)

        self.createNewMnemonicRadio = QRadioButton(self.page1)
        self.createNewMnemonicRadio.setObjectName(u"createNewMnemonicRadio")

        self.gridLayout_2.addWidget(self.createNewMnemonicRadio, 1, 0, 1, 1)

        SetSecretWizard.addPage(self.page1)
        self.page2 = QWizardPage()
        self.page2.setObjectName(u"page2")
        self.gridLayout = QGridLayout(self.page2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_4 = QLabel(self.page2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.mnemonicEdit = QTextEdit(self.page2)
        self.mnemonicEdit.setObjectName(u"mnemonicEdit")

        self.gridLayout.addWidget(self.mnemonicEdit, 1, 0, 1, 1)

        SetSecretWizard.addPage(self.page2)
        self.page3 = QWizardPage()
        self.page3.setObjectName(u"page3")
        self.gridLayout_4 = QGridLayout(self.page3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label = QLabel(self.page3)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.page3)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_4.addWidget(self.label_2, 1, 0, 1, 1)

        SetSecretWizard.addPage(self.page3)
        self.page4 = QWizardPage()
        self.page4.setObjectName(u"page4")
        self.gridLayout_3 = QGridLayout(self.page4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_3 = QLabel(self.page4)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)

        self.passwordEdit = QLineEdit(self.page4)
        self.passwordEdit.setObjectName(u"passwordEdit")
        self.passwordEdit.setInputMethodHints(Qt.ImhNoAutoUppercase)
        self.passwordEdit.setInputMask(u"")
        self.passwordEdit.setText(u"")
        self.passwordEdit.setFrame(True)
        self.passwordEdit.setPlaceholderText(u"")

        self.gridLayout_3.addWidget(self.passwordEdit, 1, 0, 1, 1)

        self.expectedPasswordLabel = QLabel(self.page4)
        self.expectedPasswordLabel.setObjectName(u"expectedPasswordLabel")

        self.gridLayout_3.addWidget(self.expectedPasswordLabel, 2, 0, 1, 1)

        SetSecretWizard.addPage(self.page4)

        self.retranslateUi(SetSecretWizard)

        QMetaObject.connectSlotsByName(SetSecretWizard)
    # setupUi

    def retranslateUi(self, SetSecretWizard):
        SetSecretWizard.setWindowTitle(QCoreApplication.translate("SetSecretWizard", u"Set Snopf Secret", None))
        self.useExistingMnemonicRadio.setText(QCoreApplication.translate("SetSecretWizard", u"&Type in existing mnemonic", None))
        self.createNewMnemonicRadio.setText(QCoreApplication.translate("SetSecretWizard", u"Create new &mnemonic", None))
        self.label_4.setText(QCoreApplication.translate("SetSecretWizard", u"Make sure to keep these 24 words at a safe place!", None))
        self.label.setText(QCoreApplication.translate("SetSecretWizard", u"Keep the button on Snopf pressed for five seconds.", None))
        self.label_2.setText(QCoreApplication.translate("SetSecretWizard", u"After the blinking LED stopped, click Next.", None))
        self.label_3.setText(QCoreApplication.translate("SetSecretWizard", u"Press the button on Snopf to type in a test password:", None))
        self.expectedPasswordLabel.setText(QCoreApplication.translate("SetSecretWizard", u"<expected result>", None))
    # retranslateUi

