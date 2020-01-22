# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'snopf_manager.ui'
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

class Ui_SnopfManager(object):
    def setupUi(self, SnopfManager):
        if SnopfManager.objectName():
            SnopfManager.setObjectName(u"SnopfManager")
        SnopfManager.resize(600, 450)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SnopfManager.sizePolicy().hasHeightForWidth())
        SnopfManager.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/icon/icon/icon.svg", QSize(), QIcon.Normal, QIcon.Off)
        SnopfManager.setWindowIcon(icon)
        self.actionOpenAccountTable = QAction(SnopfManager)
        self.actionOpenAccountTable.setObjectName(u"actionOpenAccountTable")
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
        self.centralwidget = QWidget(SnopfManager)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.accountTableView = QTableView(self.centralwidget)
        self.accountTableView.setObjectName(u"accountTableView")
        self.accountTableView.setMinimumSize(QSize(0, 0))
        self.accountTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.accountTableView.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.gridLayout.addWidget(self.accountTableView, 0, 0, 1, 1)

        SnopfManager.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(SnopfManager)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 600, 30))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEntries = QMenu(self.menubar)
        self.menuEntries.setObjectName(u"menuEntries")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName(u"menuAbout")
        SnopfManager.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(SnopfManager)
        self.statusbar.setObjectName(u"statusbar")
        SnopfManager.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEntries.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menuFile.addAction(self.actionSaveChanges)
        self.menuEntries.addAction(self.actionNewEntry)
        self.menuEntries.addAction(self.actionDeleteEntry)
        self.menuAbout.addAction(self.actionVersionInfo)

        self.retranslateUi(SnopfManager)

        QMetaObject.connectSlotsByName(SnopfManager)
    # setupUi

    def retranslateUi(self, SnopfManager):
        SnopfManager.setWindowTitle(QCoreApplication.translate("SnopfManager", u"Snopf", None))
        self.actionOpenAccountTable.setText(QCoreApplication.translate("SnopfManager", u"&Open Account Table", None))
        self.actionSetCurrentFileAsStandard.setText(QCoreApplication.translate("SnopfManager", u"&Set Current File as Default", None))
        self.actionNewEntry.setText(QCoreApplication.translate("SnopfManager", u"&New Entry", None))
        self.actionDeleteEntry.setText(QCoreApplication.translate("SnopfManager", u"&Delete Entry", None))
        self.actionSaveChanges.setText(QCoreApplication.translate("SnopfManager", u"Save &Changes", None))
        self.actionVersionInfo.setText(QCoreApplication.translate("SnopfManager", u"&Version Info", None))
        self.menuFile.setTitle(QCoreApplication.translate("SnopfManager", u"Fi&le", None))
        self.menuEntries.setTitle(QCoreApplication.translate("SnopfManager", u"E&ntries", None))
        self.menuAbout.setTitle(QCoreApplication.translate("SnopfManager", u"Abo&ut", None))
    # retranslateUi

