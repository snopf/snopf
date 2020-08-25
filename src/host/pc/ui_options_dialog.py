# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'options_dialog.ui'
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


class Ui_OptionsDialog(object):
    def setupUi(self, OptionsDialog):
        if not OptionsDialog.objectName():
            OptionsDialog.setObjectName(u"OptionsDialog")
        OptionsDialog.resize(550, 442)
        self.gridLayout_2 = QGridLayout(OptionsDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(OptionsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabGeneral = QWidget()
        self.tabGeneral.setObjectName(u"tabGeneral")
        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabWebsocket = QWidget()
        self.tabWebsocket.setObjectName(u"tabWebsocket")
        self.gridLayout = QGridLayout(self.tabWebsocket)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.websocketEnableCheckbox = QCheckBox(self.tabWebsocket)
        self.websocketEnableCheckbox.setObjectName(u"websocketEnableCheckbox")

        self.verticalLayout.addWidget(self.websocketEnableCheckbox)

        self.label = QLabel(self.tabWebsocket)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.websocketPortSpinBox = QSpinBox(self.tabWebsocket)
        self.websocketPortSpinBox.setObjectName(u"websocketPortSpinBox")
        self.websocketPortSpinBox.setMinimum(1024)
        self.websocketPortSpinBox.setMaximum(65535)

        self.verticalLayout.addWidget(self.websocketPortSpinBox)

        self.label_2 = QLabel(self.tabWebsocket)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.websocketWhiteListView = QListView(self.tabWebsocket)
        self.websocketWhiteListView.setObjectName(u"websocketWhiteListView")

        self.verticalLayout.addWidget(self.websocketWhiteListView)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.websocketRemoveClientButton = QPushButton(self.tabWebsocket)
        self.websocketRemoveClientButton.setObjectName(u"websocketRemoveClientButton")

        self.horizontalLayout_2.addWidget(self.websocketRemoveClientButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.websocketAddClientButton = QPushButton(self.tabWebsocket)
        self.websocketAddClientButton.setObjectName(u"websocketAddClientButton")

        self.horizontalLayout_2.addWidget(self.websocketAddClientButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tabWebsocket, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.buttonBox = QDialogButtonBox(OptionsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(OptionsDialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(OptionsDialog)
    # setupUi

    def retranslateUi(self, OptionsDialog):
        OptionsDialog.setWindowTitle(QCoreApplication.translate("OptionsDialog", u"Options", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), QCoreApplication.translate("OptionsDialog", u"General", None))
        self.websocketEnableCheckbox.setText(QCoreApplication.translate("OptionsDialog", u"Enable Websocket Server", None))
        self.label.setText(QCoreApplication.translate("OptionsDialog", u"Port", None))
        self.label_2.setText(QCoreApplication.translate("OptionsDialog", u"Permitted Clients", None))
        self.websocketRemoveClientButton.setText(QCoreApplication.translate("OptionsDialog", u"Remove Client", None))
        self.websocketAddClientButton.setText(QCoreApplication.translate("OptionsDialog", u"Add Client", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWebsocket), QCoreApplication.translate("OptionsDialog", u"Websocket", None))
    # retranslateUi

