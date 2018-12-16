# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(706, 403)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Open Sans SemiBold")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        MainWindow.setFont(font)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Open Sans Light")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.v_layout_btn = QtWidgets.QVBoxLayout()
        self.v_layout_btn.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.v_layout_btn.setContentsMargins(0, -1, 0, -1)
        self.v_layout_btn.setObjectName("v_layout_btn")
        self.btn_search = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_search.sizePolicy().hasHeightForWidth())
        self.btn_search.setSizePolicy(sizePolicy)
        self.btn_search.setObjectName("btn_search")
        self.v_layout_btn.addWidget(self.btn_search)
        self.btn_new_save = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_new_save.sizePolicy().hasHeightForWidth())
        self.btn_new_save.setSizePolicy(sizePolicy)
        self.btn_new_save.setObjectName("btn_new_save")
        self.v_layout_btn.addWidget(self.btn_new_save)
        self.gridLayout.addLayout(self.v_layout_btn, 2, 1, 1, 1)
        self.txt_title = QtWidgets.QLineEdit(self.centralwidget)
        self.txt_title.setObjectName("txt_title")
        self.gridLayout.addWidget(self.txt_title, 0, 0, 1, 1)
        self.st_widget = QtWidgets.QStackedWidget(self.centralwidget)
        self.st_widget.setObjectName("st_widget")
        self.edit = QtWidgets.QWidget()
        self.edit.setObjectName("edit")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.edit)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txt_main = QtWidgets.QPlainTextEdit(self.edit)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txt_main.sizePolicy().hasHeightForWidth())
        self.txt_main.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(12)
        font.setKerning(False)
        self.txt_main.setFont(font)
        self.txt_main.setAutoFillBackground(False)
        self.txt_main.setStyleSheet("")
        self.txt_main.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.txt_main.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.txt_main.setPlainText("")
        self.txt_main.setObjectName("txt_main")
        self.horizontalLayout.addWidget(self.txt_main)
        self.st_widget.addWidget(self.edit)
        self.search = QtWidgets.QWidget()
        self.search.setObjectName("search")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.search)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tr_search = QtWidgets.QTreeView(self.search)
        self.tr_search.setObjectName("tr_search")
        self.horizontalLayout_2.addWidget(self.tr_search)
        self.st_widget.addWidget(self.search)
        self.gridLayout.addWidget(self.st_widget, 1, 0, 2, 1)
        self.grp_tags = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.grp_tags.sizePolicy().hasHeightForWidth())
        self.grp_tags.setSizePolicy(sizePolicy)
        self.grp_tags.setMinimumSize(QtCore.QSize(110, 0))
        self.grp_tags.setBaseSize(QtCore.QSize(0, 0))
        self.grp_tags.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.grp_tags.setFlat(False)
        self.grp_tags.setObjectName("grp_tags")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grp_tags)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tags_layout = QtWidgets.QVBoxLayout()
        self.tags_layout.setContentsMargins(5, -1, -1, -1)
        self.tags_layout.setObjectName("tags_layout")
        self.checkBox_2 = QtWidgets.QCheckBox(self.grp_tags)
        self.checkBox_2.setObjectName("checkBox_2")
        self.tags_layout.addWidget(self.checkBox_2)
        self.checkBox = QtWidgets.QCheckBox(self.grp_tags)
        self.checkBox.setObjectName("checkBox")
        self.tags_layout.addWidget(self.checkBox)
        self.verticalLayout_2.addLayout(self.tags_layout)
        self.gridLayout.addWidget(self.grp_tags, 0, 1, 2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 706, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.st_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Notes"))
        self.btn_search.setText(_translate("MainWindow", "Search"))
        self.btn_new_save.setText(_translate("MainWindow", "New"))
        self.grp_tags.setTitle(_translate("MainWindow", "Tags"))
        self.checkBox_2.setText(_translate("MainWindow", "CheckBox"))
        self.checkBox.setText(_translate("MainWindow", "CheckBox"))

