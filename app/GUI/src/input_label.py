# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QMouseEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QStatusBar

import app.asset.res_rc
from app.GUI.Ui.Ui_input_label import Ui_Form
from app.GUI.src.opacity_controller import opacity_controller

# import res_rc


class inputLabel(opacity_controller, Ui_Form):
    requestSend = pyqtSignal(str)

    def __init__(self, parent=None, is_calc_token=True, update_token_time=1000):
        super().__init__(parent)
        self.input_font_size = 14
        self.button_font_size = 14
        self.keep_opacity_time = 5000
        self.setup_opacity_controller(opacity_next_mode_list={"normal": "await", "await": "await", "hide": "hide"})
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)

        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(":/font/荆南波波黑.ttf")
        self.input_font = QFont("荆南波波黑", self.input_font_size)
        self.button_font = QFont("荆南波波黑", self.button_font_size)
        screen = QDesktopWidget().screenGeometry()

        self.setupUi(self)
        self.statusBar = QStatusBar(self)
        self.verticalLayout.addWidget(self.statusBar)
        self.input_edit.setFont(self.input_font)
        self.input_edit.textChanged.connect(
            lambda: self.set_opacity_mode(mode="normal", clear_keep_opacity_status=True)
        )
        # self.input_edit.setStyleSheet("background: transparent;color: white;border: 4px solid lightgreen;padding: 1px;")
        self.clearButton.setFont(self.button_font)
        self.sendButton.setFont(self.button_font)

        self.clearButton.setText("清除文本")
        self.clearButton.clicked.connect(self.clear_text)
        self.sendButton.setText("发送")
        self.sendButton.clicked.connect(self.send_text)

        self.pushButton.setIcon(QIcon(":/Icon/minimize.png"))
        self.pushButton.setIconSize(self.pushButton.size())
        self.pushButton.clicked.connect(self.hide_window)
        self.pushButton.setStyleSheet("background: none; border: none;")

    def clear_text(self):
        self.input_edit.setPlainText("")

    def send_text(self):
        self.sendButton.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.statusBar.showMessage("发送中...", 1000)
        self.requestSend.emit(self.input_edit.toPlainText())
        self.clear_text()

    def enabled_send_text(self):
        self.sendButton.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.statusBar.showMessage("")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = inputLabel()
    ex.show()
    sys.exit(app.exec_())
