# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
#from asset.GUI.Ui_setting import Ui_MainWindow
from Ui_setting import Ui_MainWindow


# TODO

class SettingWidget(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super(SettingWidget, self).__init__()
        self.setupUi(self)
        self.initConnect()

    def initConnect(self):
        self.listWidget.itemClicked.connect(self.sideListWidgetClicked)

    def sideListWidgetClicked(self, item):
        index = self.listWidget.indexFromItem(item)
        self.stackedWidget.setCurrentIndex(index.row())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    v0 = SettingWidget()
    v0.show()
    sys.exit(app.exec_())
