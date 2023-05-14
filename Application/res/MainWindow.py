# -*- coding: utf-8 -*-
# Created by: PyQt5 UI code generator 5.15.7

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.sideMenuLayout = QtWidgets.QVBoxLayout()
        self.sideMenuLayout.setObjectName("sideMenuLayout")
        
    # ------------------

        self.overlayWidget = QtWidgets.QWidget(self.centralwidget)
        self.overlayWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.overlayWidget.sizePolicy().hasHeightForWidth())
        self.overlayWidget.setSizePolicy(sizePolicy)
        self.overlayWidget.setMinimumSize(QtCore.QSize(400, 100))
        self.overlayWidget.setObjectName("overlayWidget")

        self.label = QtWidgets.QLabel(self.overlayWidget)
        self.label.setGeometry(QtCore.QRect(15, 5, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.overColorLabel = QtWidgets.QLabel(self.overlayWidget)
        self.overColorLabel.setGeometry(QtCore.QRect(10, 45, 84, 40))
        self.overColorLabel.setText("")
        self.overColorLabel.setObjectName("overColorLabel")

        self.overColorButton = QtWidgets.QPushButton(self.overlayWidget)
        self.overColorButton.setGeometry(QtCore.QRect(200, 45, 180, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.overColorButton.setFont(font)
        self.overColorButton.setObjectName("overColorButton")
        self.sideMenuLayout.addWidget(self.overlayWidget)
        
    # ------------------

        self.webcamWidget = QtWidgets.QWidget(self.centralwidget)
        self.webcamWidget.setMinimumSize(QtCore.QSize(0, 214))
        self.webcamWidget.setMaximumSize(QtCore.QSize(16777215, 225))
        self.webcamWidget.setObjectName("webcamWidget")

        self.label_2 = QtWidgets.QLabel(self.webcamWidget)
        self.label_2.setGeometry(QtCore.QRect(15, 5, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_5 = QtWidgets.QLabel(self.webcamWidget)
        self.label_5.setGeometry(QtCore.QRect(66, 45, 280, 160))
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        
    # ------------------

        self.topLeftButton = QtWidgets.QPushButton(self.webcamWidget)
        self.topLeftButton.setGeometry(QtCore.QRect(66, 45, 75, 51))
        self.topLeftButton.setText("")
        self.topLeftButton.setObjectName("topLeftButton")

        self.botLeftButton = QtWidgets.QPushButton(self.webcamWidget)
        self.botLeftButton.setGeometry(QtCore.QRect(66, 155, 75, 51))
        self.botLeftButton.setText("")
        self.botLeftButton.setObjectName("botLeftButton")

        self.topRightButton = QtWidgets.QPushButton(self.webcamWidget)
        self.topRightButton.setGeometry(QtCore.QRect(270, 45, 75, 51))
        self.topRightButton.setText("")
        self.topRightButton.setObjectName("topRightButton")
        
        self.botRightButton = QtWidgets.QPushButton(self.webcamWidget)
        self.botRightButton.setGeometry(QtCore.QRect(270, 155, 75, 51))
        self.botRightButton.setText("")
        self.botRightButton.setObjectName("botRightButton")

        self.sideMenuLayout.addWidget(self.webcamWidget)

    # ------------------

        self.otherWidget = QtWidgets.QWidget(self.centralwidget)
        self.otherWidget.setMinimumSize(QtCore.QSize(0, 275))
        self.otherWidget.setObjectName("otherWidget")

        self.label_3 = QtWidgets.QLabel(self.otherWidget)
        self.label_3.setGeometry(QtCore.QRect(15, 5, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.otherWidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 40, 381, 225))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        
    # ------------------

        self.themeButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.themeButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.themeButton.setFont(font)
        self.themeButton.setObjectName("themeButton")
        self.verticalLayout.addWidget(self.themeButton)

        self.folderButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.folderButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.folderButton.setFont(font)
        self.folderButton.setObjectName("folderButton")
        self.verticalLayout.addWidget(self.folderButton)

        self.changeDirButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.changeDirButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.changeDirButton.setFont(font)
        self.changeDirButton.setObjectName("changeDirButton")
        self.verticalLayout.addWidget(self.changeDirButton)

        self.calibrButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.calibrButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.calibrButton.setFont(font)
        self.calibrButton.setObjectName("calibrButton")
        self.verticalLayout.addWidget(self.calibrButton)

        self.exitButton = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.exitButton.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.exitButton.setFont(font)
        self.exitButton.setObjectName("exitButton")
        self.verticalLayout.addWidget(self.exitButton)
        
    # ------------------

        self.sideMenuLayout.addWidget(self.otherWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.sideMenuLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.sideMenuLayout, 0, 1, 1, 1)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")

        self.frame = QtWidgets.QLabel(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(930, 580))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.mainLayout.addWidget(self.frame)

        self.recControlLayout = QtWidgets.QHBoxLayout()
        self.recControlLayout.setContentsMargins(-1, 10, -1, -1)
        self.recControlLayout.setSpacing(0)
        self.recControlLayout.setObjectName("recControlLayout")

        self.recHintLabel = QtWidgets.QLabel(self.centralwidget)
        self.recHintLabel.setIndent(20)
        self.recHintLabel.setObjectName("recHintLabel")
        self.recControlLayout.addWidget(self.recHintLabel)

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setCheckable(True)
        self.startButton.setIcon(QtGui.QIcon("res/playIcon.png"))
        self.startButton.setIconSize(QtCore.QSize(20, 20))
        self.startButton.setObjectName("startButton")
        self.recControlLayout.addWidget(self.startButton)

        self.recStatLabel = QtWidgets.QLabel(self.centralwidget)
        self.recStatLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.recStatLabel.setIndent(22)
        self.recStatLabel.setObjectName("recStatLabel")
        self.recControlLayout.addWidget(self.recStatLabel)

        self.recControlLayout.setStretch(0, 40)
        self.recControlLayout.setStretch(1, 20)
        self.recControlLayout.setStretch(2, 40)
        self.mainLayout.addLayout(self.recControlLayout)

        self.gridLayout.addLayout(self.mainLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1366, 21))
        self.menubar.setObjectName("menubar")

        self.helpMenu = QtWidgets.QMenu(self.menubar)
        self.helpMenu.setObjectName("helpMenu")
        self.helpContent = QtWidgets.QAction("About and FAQ", self.helpMenu)
        self.helpMenu.addAction(self.helpContent)
        MainWindow.setMenuBar(self.menubar)
        self.menubar.addAction(self.helpMenu.menuAction())

        self.showFullScreen()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ThirdEye"))
        self.label.setText(_translate("MainWindow", "Overlay"))
        self.overColorButton.setText(_translate("MainWindow", "Change Color"))
        self.label_2.setText(_translate("MainWindow", "Web camera"))
        self.label_3.setText(_translate("MainWindow", "Other"))
        self.themeButton.setText(_translate("MainWindow", "Change Theme"))
        self.folderButton.setText(_translate("MainWindow", "Open output folder"))
        self.changeDirButton.setText(_translate("MainWindow", "Change output folder"))
        self.calibrButton.setText(_translate("MainWindow", "Start Calibration"))
        self.exitButton.setText(_translate("MainWindow", "Exit"))
        self.recHintLabel.setText(_translate("MainWindow", "Press to start recording --->"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.recStatLabel.setText(_translate("MainWindow", "Recording stopped"))
        self.helpMenu.setTitle(_translate("MainWindow", "Help"))
