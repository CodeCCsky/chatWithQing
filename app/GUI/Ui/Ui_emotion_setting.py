# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\Administrator\Desktop\workspace\chatWithQing\app\asset\xml\emotion_setting.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from  app.GUI.src.pet_view import PetGraphicsView


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 400)
        MainWindow.setMaximumSize(QtCore.QSize(750, 400))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget_5 = QtWidgets.QWidget(self.widget_4)
        self.widget_5.setObjectName("widget_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.widget_5)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.line = QtWidgets.QFrame(self.widget_5)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.categoryMenuListWidget = QtWidgets.QListWidget(self.widget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.categoryMenuListWidget.sizePolicy().hasHeightForWidth())
        self.categoryMenuListWidget.setSizePolicy(sizePolicy)
        self.categoryMenuListWidget.setMinimumSize(QtCore.QSize(140, 200))
        self.categoryMenuListWidget.setMaximumSize(QtCore.QSize(140, 16777215))
        self.categoryMenuListWidget.setStyleSheet("")
        self.categoryMenuListWidget.setFrameShape(QtWidgets.QFrame.Panel)
        self.categoryMenuListWidget.setFrameShadow(QtWidgets.QFrame.Raised)
        self.categoryMenuListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.categoryMenuListWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.categoryMenuListWidget.setObjectName("categoryMenuListWidget")
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        item.setFont(font)
        self.categoryMenuListWidget.addItem(item)
        self.verticalLayout_3.addWidget(self.categoryMenuListWidget)
        self.horizontalLayout_2.addWidget(self.widget_5)
        self.widget = QtWidgets.QWidget(self.widget_4)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(6, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_2 = QtWidgets.QWidget(self.widget)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout.setContentsMargins(0, 3, 0, 3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.moveButton = QtWidgets.QPushButton(self.widget_2)
        self.moveButton.setObjectName("moveButton")
        self.horizontalLayout.addWidget(self.moveButton)
        self.copyButton = QtWidgets.QPushButton(self.widget_2)
        self.copyButton.setObjectName("copyButton")
        self.horizontalLayout.addWidget(self.copyButton)
        self.delButton = QtWidgets.QPushButton(self.widget_2)
        self.delButton.setObjectName("delButton")
        self.horizontalLayout.addWidget(self.delButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.widget_2)
        self.strShowListWidget = QtWidgets.QListWidget(self.widget)
        self.strShowListWidget.setObjectName("strShowListWidget")
        self.verticalLayout.addWidget(self.strShowListWidget)
        self.widget_6 = QtWidgets.QWidget(self.widget)
        self.widget_6.setObjectName("widget_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lineEdit = QtWidgets.QLineEdit(self.widget_6)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_4.addWidget(self.lineEdit)
        self.addItemButton = QtWidgets.QPushButton(self.widget_6)
        self.addItemButton.setObjectName("addItemButton")
        self.horizontalLayout_4.addWidget(self.addItemButton)
        self.verticalLayout.addWidget(self.widget_6)
        self.widget_3 = QtWidgets.QWidget(self.widget)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout.addWidget(self.widget_3)
        self.horizontalLayout_2.addWidget(self.widget)
        self.previewWidget = QtWidgets.QWidget(self.widget_4)
        self.previewWidget.setMinimumSize(QtCore.QSize(170, 250))
        self.previewWidget.setMaximumSize(QtCore.QSize(170, 16777215))
        self.previewWidget.setStyleSheet("QWidget{border: 1px dashed black;}")
        self.previewWidget.setObjectName("previewWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.previewWidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.previewWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setStyleSheet("QLabel{border: 0px;}")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.graphicsView = PetGraphicsView(self.previewWidget)
        self.graphicsView.setMinimumSize(QtCore.QSize(150, 200))
        self.graphicsView.setMaximumSize(QtCore.QSize(300, 400))
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout_4.addWidget(self.graphicsView)
        spacerItem1 = QtWidgets.QSpacerItem(20, 321, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.horizontalLayout_2.addWidget(self.previewWidget)
        self.verticalLayout_2.addWidget(self.widget_4)
        self.ensureButtonBox = QtWidgets.QDialogButtonBox(self.centralwidget)
        self.ensureButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.ensureButtonBox.setObjectName("ensureButtonBox")
        self.verticalLayout_2.addWidget(self.ensureButtonBox)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "表情差分标识管理"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">表情差分标识 分类</span></p></body></html>"))
        __sortingEnabled = self.categoryMenuListWidget.isSortingEnabled()
        self.categoryMenuListWidget.setSortingEnabled(False)
        item = self.categoryMenuListWidget.item(0)
        item.setText(_translate("MainWindow", "未分类"))
        item = self.categoryMenuListWidget.item(1)
        item.setText(_translate("MainWindow", "(･◡･) 默认"))
        item = self.categoryMenuListWidget.item(2)
        item.setText(_translate("MainWindow", "(@_@)"))
        item = self.categoryMenuListWidget.item(3)
        item.setText(_translate("MainWindow", " ⁄(⁄⁄•⁄Д⁄•⁄⁄)⁄"))
        item = self.categoryMenuListWidget.item(4)
        item.setText(_translate("MainWindow", "(罒▽罒)"))
        item = self.categoryMenuListWidget.item(5)
        item.setText(_translate("MainWindow", "(─‿─)"))
        item = self.categoryMenuListWidget.item(6)
        item.setText(_translate("MainWindow", "(>_<)"))
        item = self.categoryMenuListWidget.item(7)
        item.setText(_translate("MainWindow", "(￣▽￣)"))
        item = self.categoryMenuListWidget.item(8)
        item.setText(_translate("MainWindow", "忽略的标识"))
        self.categoryMenuListWidget.setSortingEnabled(__sortingEnabled)
        self.moveButton.setText(_translate("MainWindow", "移动到..."))
        self.copyButton.setText(_translate("MainWindow", "复制到.."))
        self.delButton.setText(_translate("MainWindow", "删除"))
        self.addItemButton.setText(_translate("MainWindow", "添加"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">当前表情预览</span></p></body></html>"))