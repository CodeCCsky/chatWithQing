# -*- coding: utf-8 -*-
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# TODO
class SettingWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.VLayout = QVBoxLayout(self)
        self.listsWidget = QWidget(self)
        self.VLayout.addWidget(self.listsWidget)
        self.listsHLayout = QHBoxLayout(self.listsWidget)
        self.sideListWidget = QListWidget(self.listsWidget)
        
        self.listsHLayout.addWidget(self.sideListWidget)
        self.mainOptionWidget = QWidget(self.listsWidget)
        self.listsHLayout.addWidget(self.mainOptionWidget)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    v0 = SettingWidget()
    v0.show()
    sys.exit(app.exec_())