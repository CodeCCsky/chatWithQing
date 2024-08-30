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
        self.sideListWidget = QListWidget(self)
        self.VLayout.addWidget(self.sideListWidget)
        self.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    v0 = SettingWidget()
    v0.show()
    sys.exit(app.exec_())