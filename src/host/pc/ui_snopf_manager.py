# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'snopf_manager.ui'
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

from account_table_widget import AccountTableWidget
from keymap_editing import KeymapLineEdit

import resources_rc

class Ui_SnopfManager(object):
    def setupUi(self, SnopfManager):
        if not SnopfManager.objectName():
            SnopfManager.setObjectName(u"SnopfManager")
        SnopfManager.resize(771, 611)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SnopfManager.sizePolicy().hasHeightForWidth())
        SnopfManager.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/icon/icon/icon.svg", QSize(), QIcon.Normal, QIcon.Off)
        SnopfManager.setWindowIcon(icon)
        self.actionSetCurrentFileAsStandard = QAction(SnopfManager)
        self.actionSetCurrentFileAsStandard.setObjectName(u"actionSetCurrentFileAsStandard")
        self.actionNewEntry = QAction(SnopfManager)
        self.actionNewEntry.setObjectName(u"actionNewEntry")
        self.actionDeleteEntry = QAction(SnopfManager)
        self.actionDeleteEntry.setObjectName(u"actionDeleteEntry")
        self.actionSaveChanges = QAction(SnopfManager)
        self.actionSaveChanges.setObjectName(u"actionSaveChanges")
        self.actionVersionInfo = QAction(SnopfManager)
        self.actionVersionInfo.setObjectName(u"actionVersionInfo")
        self.actionSetSnopfSecret = QAction(SnopfManager)
        self.actionSetSnopfSecret.setObjectName(u"actionSetSnopfSecret")
        self.actionOpen = QAction(SnopfManager)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(SnopfManager)
        self.actionSave.setObjectName(u"actionSave")
        self.actionNew = QAction(SnopfManager)
        self.actionNew.setObjectName(u"actionNew")
        self.actionTODO_Write_keyboard_layout = QAction(SnopfManager)
        self.actionTODO_Write_keyboard_layout.setObjectName(u"actionTODO_Write_keyboard_layout")
        self.actionSetKeyboardDelay = QAction(SnopfManager)
        self.actionSetKeyboardDelay.setObjectName(u"actionSetKeyboardDelay")
        self.actionSaveAs = QAction(SnopfManager)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.actionExit = QAction(SnopfManager)
        self.actionExit.setObjectName(u"actionExit")
        self.centralwidget = QWidget(SnopfManager)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_6 = QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.accountTableWidget = AccountTableWidget(self.splitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(1, u"2");
        __qtreewidgetitem.setText(0, u"1");
        self.accountTableWidget.setHeaderItem(__qtreewidgetitem)
        self.accountTableWidget.setObjectName(u"accountTableWidget")
        self.accountTableWidget.setSortingEnabled(True)
        self.accountTableWidget.setHeaderHidden(False)
        self.accountTableWidget.setColumnCount(2)
        self.splitter.addWidget(self.accountTableWidget)
        self.accountTableWidget.header().setVisible(True)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_5 = QVBoxLayout(self.widget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.widget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMinimumSize(QSize(120, 0))

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 0, 1, 1, 1)

        self.serviceEdit = QLineEdit(self.frame_2)
        self.serviceEdit.setObjectName(u"serviceEdit")
        self.serviceEdit.setReadOnly(True)

        self.gridLayout_2.addWidget(self.serviceEdit, 0, 2, 1, 1)

        self.label_2 = QLabel(self.frame_2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(120, 0))

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_3, 1, 1, 1, 1)

        self.accountEdit = QLineEdit(self.frame_2)
        self.accountEdit.setObjectName(u"accountEdit")
        self.accountEdit.setReadOnly(True)

        self.gridLayout_2.addWidget(self.accountEdit, 1, 2, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.line_7 = QFrame(self.frame_2)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.HLine)
        self.line_7.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.line_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.requestPasswordButton = QPushButton(self.frame_2)
        self.requestPasswordButton.setObjectName(u"requestPasswordButton")

        self.horizontalLayout_6.addWidget(self.requestPasswordButton)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)

        self.commitChangesButton = QPushButton(self.frame_2)
        self.commitChangesButton.setObjectName(u"commitChangesButton")

        self.horizontalLayout_6.addWidget(self.commitChangesButton)

        self.deleteEntryButton = QPushButton(self.frame_2)
        self.deleteEntryButton.setObjectName(u"deleteEntryButton")

        self.horizontalLayout_6.addWidget(self.deleteEntryButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)


        self.gridLayout_4.addLayout(self.verticalLayout_3, 0, 0, 1, 1)


        self.verticalLayout_5.addWidget(self.frame_2)

        self.tabWidget = QTabWidget(self.widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.generalTab = QWidget()
        self.generalTab.setObjectName(u"generalTab")
        self.gridLayout_5 = QGridLayout(self.generalTab)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(self.generalTab)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_5.addWidget(self.label_4)

        self.horizontalSpacer_7 = QSpacerItem(15, 18, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_7)

        self.lengthSpinner = QSpinBox(self.generalTab)
        self.lengthSpinner.setObjectName(u"lengthSpinner")
        self.lengthSpinner.setMinimum(6)
        self.lengthSpinner.setMaximum(42)
        self.lengthSpinner.setValue(22)

        self.horizontalLayout_5.addWidget(self.lengthSpinner)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.generalTab)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_4.addWidget(self.label_3)

        self.horizontalSpacer_8 = QSpacerItem(15, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.iterationSpinner = QSpinBox(self.generalTab)
        self.iterationSpinner.setObjectName(u"iterationSpinner")
        self.iterationSpinner.setMaximum(99999)
        self.iterationSpinner.setSingleStep(1)

        self.horizontalLayout_4.addWidget(self.iterationSpinner)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.line_4 = QFrame(self.generalTab)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_6 = QLabel(self.generalTab)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_3.addWidget(self.label_6)

        self.horizontalSpacer_10 = QSpacerItem(15, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_10)

        self.entropyEdit = QLineEdit(self.generalTab)
        self.entropyEdit.setObjectName(u"entropyEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.entropyEdit.sizePolicy().hasHeightForWidth())
        self.entropyEdit.setSizePolicy(sizePolicy2)
        self.entropyEdit.setMaximumSize(QSize(70, 16777215))
        self.entropyEdit.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.entropyEdit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.entropyEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.line_5 = QFrame(self.generalTab)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line_5)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_9 = QLabel(self.generalTab)
        self.label_9.setObjectName(u"label_9")
        sizePolicy1.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy1)
        self.label_9.setMinimumSize(QSize(120, 0))

        self.horizontalLayout_2.addWidget(self.label_9)

        self.horizontalSpacer_9 = QSpacerItem(15, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_9)

        self.commentEdit = QLineEdit(self.generalTab)
        self.commentEdit.setObjectName(u"commentEdit")
        self.commentEdit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.commentEdit)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.generalTab, "")
        self.rulesTab = QWidget()
        self.rulesTab.setObjectName(u"rulesTab")
        self.gridLayout = QGridLayout(self.rulesTab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.includeLowercaseCB = QCheckBox(self.rulesTab)
        self.includeLowercaseCB.setObjectName(u"includeLowercaseCB")

        self.verticalLayout.addWidget(self.includeLowercaseCB)

        self.includeUppercaseCB = QCheckBox(self.rulesTab)
        self.includeUppercaseCB.setObjectName(u"includeUppercaseCB")

        self.verticalLayout.addWidget(self.includeUppercaseCB)

        self.includeNumericalCB = QCheckBox(self.rulesTab)
        self.includeNumericalCB.setObjectName(u"includeNumericalCB")

        self.verticalLayout.addWidget(self.includeNumericalCB)

        self.includeSpecialCB = QCheckBox(self.rulesTab)
        self.includeSpecialCB.setObjectName(u"includeSpecialCB")

        self.verticalLayout.addWidget(self.includeSpecialCB)

        self.line = QFrame(self.rulesTab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.avoidRepCB = QCheckBox(self.rulesTab)
        self.avoidRepCB.setObjectName(u"avoidRepCB")

        self.verticalLayout.addWidget(self.avoidRepCB)

        self.avoidSeqCB = QCheckBox(self.rulesTab)
        self.avoidSeqCB.setObjectName(u"avoidSeqCB")

        self.verticalLayout.addWidget(self.avoidSeqCB)

        self.line_2 = QFrame(self.rulesTab)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_10 = QLabel(self.rulesTab)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout.addWidget(self.label_10)

        self.pwAppendixEdit = QLineEdit(self.rulesTab)
        self.pwAppendixEdit.setObjectName(u"pwAppendixEdit")
        self.pwAppendixEdit.setMaxLength(3)

        self.horizontalLayout.addWidget(self.pwAppendixEdit)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(114, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 121, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.tabWidget.addTab(self.rulesTab, "")
        self.keymapTab = QWidget()
        self.keymapTab.setObjectName(u"keymapTab")
        self.gridLayout_3 = QGridLayout(self.keymapTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(self.keymapTab)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_4.addWidget(self.label_7)

        self.keymapEdit = KeymapLineEdit(self.keymapTab)
        self.keymapEdit.setObjectName(u"keymapEdit")
        self.keymapEdit.setMaxLength(64)

        self.verticalLayout_4.addWidget(self.keymapEdit)

        self.label_8 = QLabel(self.keymapTab)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_4.addWidget(self.label_8)

        self.remainingKeysEdit = QLineEdit(self.keymapTab)
        self.remainingKeysEdit.setObjectName(u"remainingKeysEdit")
        self.remainingKeysEdit.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.remainingKeysEdit)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.addLowercaseButton = QPushButton(self.keymapTab)
        self.addLowercaseButton.setObjectName(u"addLowercaseButton")

        self.horizontalLayout_9.addWidget(self.addLowercaseButton)

        self.addUppercaseButton = QPushButton(self.keymapTab)
        self.addUppercaseButton.setObjectName(u"addUppercaseButton")

        self.horizontalLayout_9.addWidget(self.addUppercaseButton)

        self.addNumericalButton = QPushButton(self.keymapTab)
        self.addNumericalButton.setObjectName(u"addNumericalButton")

        self.horizontalLayout_9.addWidget(self.addNumericalButton)

        self.addSpecialButton = QPushButton(self.keymapTab)
        self.addSpecialButton.setObjectName(u"addSpecialButton")

        self.horizontalLayout_9.addWidget(self.addSpecialButton)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.line_6 = QFrame(self.keymapTab)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.HLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line_6)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_5 = QLabel(self.keymapTab)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_11.addWidget(self.label_5)

        self.selectKeymapComboBox = QComboBox(self.keymapTab)
        self.selectKeymapComboBox.setObjectName(u"selectKeymapComboBox")
        self.selectKeymapComboBox.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_11.addWidget(self.selectKeymapComboBox)

        self.applyKeymapButton = QPushButton(self.keymapTab)
        self.applyKeymapButton.setObjectName(u"applyKeymapButton")

        self.horizontalLayout_11.addWidget(self.applyKeymapButton)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_5)


        self.verticalLayout_4.addLayout(self.horizontalLayout_11)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_3)


        self.gridLayout_3.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.tabWidget.addTab(self.keymapTab, "")

        self.verticalLayout_5.addWidget(self.tabWidget)

        self.splitter.addWidget(self.widget)

        self.gridLayout_6.addWidget(self.splitter, 0, 0, 1, 1)

        SnopfManager.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(SnopfManager)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 771, 30))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEntries = QMenu(self.menubar)
        self.menuEntries.setObjectName(u"menuEntries")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName(u"menuAbout")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        SnopfManager.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(SnopfManager)
        self.statusbar.setObjectName(u"statusbar")
        SnopfManager.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEntries.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionExit)
        self.menuEntries.addAction(self.actionNewEntry)
        self.menuEntries.addAction(self.actionDeleteEntry)
        self.menuAbout.addAction(self.actionVersionInfo)
        self.menuTools.addAction(self.actionSetSnopfSecret)
        self.menuTools.addAction(self.actionSetKeyboardDelay)

        self.retranslateUi(SnopfManager)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SnopfManager)
    # setupUi

    def retranslateUi(self, SnopfManager):
        SnopfManager.setWindowTitle(QCoreApplication.translate("SnopfManager", u"Snopf", None))
        self.actionSetCurrentFileAsStandard.setText(QCoreApplication.translate("SnopfManager", u"&Set Current File as Default", None))
        self.actionNewEntry.setText(QCoreApplication.translate("SnopfManager", u"&New Entry", None))
        self.actionDeleteEntry.setText(QCoreApplication.translate("SnopfManager", u"&Delete Entry", None))
        self.actionSaveChanges.setText(QCoreApplication.translate("SnopfManager", u"Save &Changes", None))
        self.actionVersionInfo.setText(QCoreApplication.translate("SnopfManager", u"&Version Info", None))
        self.actionSetSnopfSecret.setText(QCoreApplication.translate("SnopfManager", u"&Set Snopf Secret", None))
        self.actionOpen.setText(QCoreApplication.translate("SnopfManager", u"&Open", None))
        self.actionSave.setText(QCoreApplication.translate("SnopfManager", u"&Save", None))
        self.actionNew.setText(QCoreApplication.translate("SnopfManager", u"&New", None))
        self.actionTODO_Write_keyboard_layout.setText(QCoreApplication.translate("SnopfManager", u"&TODO Write keyboard layout", None))
        self.actionSetKeyboardDelay.setText(QCoreApplication.translate("SnopfManager", u"Set &Keyboard Delay", None))
        self.actionSetKeyboardDelay.setIconText(QCoreApplication.translate("SnopfManager", u"Set Keyboard Delay", None))
        self.actionSaveAs.setText(QCoreApplication.translate("SnopfManager", u"Sa&ve As", None))
        self.actionExit.setText(QCoreApplication.translate("SnopfManager", u"&Exit", None))
        self.label.setText(QCoreApplication.translate("SnopfManager", u"Service:", None))
        self.label_2.setText(QCoreApplication.translate("SnopfManager", u"Account:", None))
        self.requestPasswordButton.setText(QCoreApplication.translate("SnopfManager", u"Request Password", None))
        self.commitChangesButton.setText(QCoreApplication.translate("SnopfManager", u"Commit Changes", None))
        self.deleteEntryButton.setText(QCoreApplication.translate("SnopfManager", u"Delete Entry", None))
        self.label_4.setText(QCoreApplication.translate("SnopfManager", u"Password Length:", None))
        self.label_3.setText(QCoreApplication.translate("SnopfManager", u"Password Iteration:", None))
        self.label_6.setText(QCoreApplication.translate("SnopfManager", u"Password Entropy:", None))
        self.label_9.setText(QCoreApplication.translate("SnopfManager", u"Comment:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.generalTab), QCoreApplication.translate("SnopfManager", u"General", None))
        self.includeLowercaseCB.setText(QCoreApplication.translate("SnopfManager", u"Include lowercase", None))
        self.includeUppercaseCB.setText(QCoreApplication.translate("SnopfManager", u"Include uppercase", None))
        self.includeNumericalCB.setText(QCoreApplication.translate("SnopfManager", u"Include numerical", None))
        self.includeSpecialCB.setText(QCoreApplication.translate("SnopfManager", u"Include special character", None))
        self.avoidRepCB.setText(QCoreApplication.translate("SnopfManager", u"Avoid repeated characters", None))
        self.avoidSeqCB.setText(QCoreApplication.translate("SnopfManager", u"Avoid sequences", None))
        self.label_10.setText(QCoreApplication.translate("SnopfManager", u"Password appendix:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rulesTab), QCoreApplication.translate("SnopfManager", u"Rules", None))
        self.label_7.setText(QCoreApplication.translate("SnopfManager", u"Keymap:", None))
        self.keymapEdit.setText(QCoreApplication.translate("SnopfManager", u"abcdefghijklmnopqrABCDEFGHIJKLMNOPQR0123456789-@!?$*+=&#[]().:><", None))
        self.label_8.setText(QCoreApplication.translate("SnopfManager", u"Remaining character set:", None))
        self.remainingKeysEdit.setText("")
        self.addLowercaseButton.setText(QCoreApplication.translate("SnopfManager", u"Add a,b,c..", None))
        self.addUppercaseButton.setText(QCoreApplication.translate("SnopfManager", u"Add A,B,C..", None))
        self.addNumericalButton.setText(QCoreApplication.translate("SnopfManager", u"Add 0,1,2..", None))
        self.addSpecialButton.setText(QCoreApplication.translate("SnopfManager", u"Add >,?,!..", None))
        self.label_5.setText(QCoreApplication.translate("SnopfManager", u"Select preset Keymap:", None))
        self.applyKeymapButton.setText(QCoreApplication.translate("SnopfManager", u"Apply", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.keymapTab), QCoreApplication.translate("SnopfManager", u"Keymap", None))
        self.menuFile.setTitle(QCoreApplication.translate("SnopfManager", u"Fi&le", None))
        self.menuEntries.setTitle(QCoreApplication.translate("SnopfManager", u"E&ntries", None))
        self.menuAbout.setTitle(QCoreApplication.translate("SnopfManager", u"Abo&ut", None))
        self.menuTools.setTitle(QCoreApplication.translate("SnopfManager", u"&Tools", None))
    # retranslateUi

