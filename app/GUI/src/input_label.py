# -*- coding: utf-8 -*-
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QIcon, QMouseEvent, QPainterPath, QRegion
from PyQt5.QtWidgets import QApplication

import app.asset.res_rc
from app.GUI.Ui.Ui_input_label import Ui_Form
from app.GUI.src.opacity_controller import opacity_controller

# import res_rc


class inputLabel(opacity_controller, Ui_Form):
    requestSend = pyqtSignal(str)
    requestRetry = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_opacity_controller(opacity_next_mode_list={"normal": "await", "await": "await", "hide": "hide"})
        self.initUI()

    def initUI(self):
        self.radius = 20
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)

        self.setupUi(self)
        self.input_edit.textChanged.connect(
            lambda: self.set_opacity_mode(mode="normal", clear_keep_opacity_status=True)
        )
        self.input_edit.setPlaceholderText("输入文本...")
        self.input_edit.setPlainText("")

        # self.sendButton.setText("发送")
        self.sendButton.setIcon(QIcon(":/Icon/send.png"))
        self.sendButton.setIconSize(self.sendButton.size())
        self.sendButton.clicked.connect(self.send_text)

        self.pushButton.setIcon(QIcon(":/Icon/minimize.png"))
        self.pushButton.setIconSize(self.pushButton.size())
        self.pushButton.clicked.connect(self.hide_window)

    def set_placeholder_text(self, text: str):
        self.input_edit.setPlaceholderText(text)

    def clear_text(self):
        self.input_edit.setPlaceholderText("输入文本...")
        self.input_edit.setPlainText("")

    def retry_send(self):
        self.sendButton.setEnabled(False)
        self.input_edit.setEnabled(False)
        # self.statusBar.showMessage("重试中...", 1000)
        self.requestRetry.emit()

    def send_text(self):
        self.sendButton.setEnabled(False)
        self.input_edit.setEnabled(False)
        # self.statusBar.showMessage("发送中...", 1000)
        self.requestSend.emit(self.input_edit.toPlainText())
        self.clear_text()

    def enabled_send_text(self):
        self.sendButton.setEnabled(True)
        self.input_edit.setEnabled(True)
        # self.statusBar.showMessage("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.radius, self.radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

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
