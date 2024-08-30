# -*- coding: utf-8 -*-
import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QStatusBar
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import asset.GUI.res_rc
#import res_rc

class inputLabel(QWidget):
    requestSend = pyqtSignal(str)
    getTokens = pyqtSignal(str)
    def __init__(self,parent = None, is_calc_token = True, update_token_time = 1000):
        super().__init__(parent)
        self.input_font_size = 16
        self.button_font_size = 16
        self.input_font = QFont('SimHei',self.input_font_size)
        self.button_font = QFont('SimHei',self.button_font_size)
        self.init_token_calc(update_token_time, is_calc_token)
        self.init_window_opacity_control()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)

        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(':/font/荆南波波黑.ttf')
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(int(screen.width()*0.95-400),int(screen.height()*0.3),400,300)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 0, 5, 0)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_2 = QtWidgets.QWidget(self)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(753, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(32, 32))
        self.pushButton.setMaximumSize(QtCore.QSize(32, 32))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.widget_2)
        self.input_edit = QtWidgets.QPlainTextEdit(self)
        self.input_edit.setObjectName("input_edit")
        self.verticalLayout.addWidget(self.input_edit)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(557, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.clearButton = QtWidgets.QPushButton(self.widget)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout.addWidget(self.clearButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.sendButton = QtWidgets.QPushButton(self.widget)
        self.sendButton.setObjectName("sendButton")
        self.horizontalLayout.addWidget(self.sendButton)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.verticalLayout.addWidget(self.widget)
        self.statusBar = QStatusBar(self)
        self.verticalLayout.addWidget(self.statusBar)

        self.input_edit.setFont(self.input_font)
        self.input_edit.textChanged.connect(self.set_keep_opacity)
        self.input_edit.textChanged.connect(lambda :self.update_text2token(self.input_edit.toPlainText()))
        #self.input_edit.setStyleSheet("background: transparent;color: white;border: 4px solid lightgreen;padding: 1px;")
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
        self.is_hide = False

    def init_window_opacity_control(self) -> None:
        self.keep_opacity = False
        self.is_mouse_over = True
        self.keep_opacity_timer = QTimer()
        self.keep_opacity_timer.timeout.connect(self.reset_keep_opacity)
        self.window_opacity_timer = QTimer()
        self.window_opacity_timer.timeout.connect(self.window_opacity_control)
        self.window_opacity_timer.start(25) # 25 毫秒更新一次窗口透明度
        self.set_mouse_over_timer = QTimer() # 鼠标离开/进入窗口后多久更新 is_mouse_over

    def init_token_calc(self, update_token_time: int, is_calc_token: bool) -> None:
        self.wait_to_send_text = ''
        self.is_calc_token = is_calc_token
        self.update_token_time = update_token_time
        self.text2token_timer = QTimer()
        self.text2token_timer.timeout.connect(self.send_text2token)

    def set_keep_opacity(self, keep_time:int = 3000):
        self.keep_opacity = True
        self.keep_opacity_timer.start(keep_time)

    def reset_keep_opacity(self):
        self.keep_opacity = False
        self.keep_opacity_timer.stop()

    def update_text2token(self, text: str):
        self.text2token_timer.start(self.update_token_time)
        self.wait_to_send_text = text

    def send_text2token(self):
        if self.is_calc_token:
            self.getTokens.emit(self.wait_to_send_text)
            self.text2token_timer.stop()

    def show_token(self, token_num: int):
        self.statusBar.showMessage(f'输入预计消耗的token数量(包含后台提示): {token_num} Tokens')
        self.text2token_timer.start(self.update_token_time)

    def clear_text(self):
        self.input_edit.setPlainText('')
        self.text2token_timer.stop()

    def send_text(self):
        self.sendButton.setEnabled(False)
        self.input_edit.setEnabled(False)
        self.statusBar.showMessage('发送中...',1000)
        self.requestSend.emit(self.input_edit.toPlainText())
        self.clear_text()

    def hide_window(self):
        self.is_hide = True
        self.setWindowOpacity(0)

    def show_window(self):
        self.is_hide = False
        self.setWindowOpacity(0.99)

    def set_mouse_over(self, status: bool):
        self.set_mouse_over_timer.stop()
        self.is_mouse_over = status

    def window_opacity_control(self):
        if self.is_hide is False and self.keep_opacity is False:
            if self.is_mouse_over:
                opacity_value = min(0.99, self.windowOpacity()+0.1)
                self.setWindowOpacity(opacity_value)
            else :
                opacity_value = max(0.3, self.windowOpacity()-0.1)
                self.setWindowOpacity(opacity_value)
        elif self.is_hide:
            self.setWindowOpacity(0)
        elif self.keep_opacity:
            self.setWindowOpacity(0.99)

    def enabled_send_text(self):
        self.sendButton.setEnabled(True)
        self.input_edit.setEnabled(True)
        self.statusBar.showMessage('')

    def enterEvent(self, event):
        self.set_mouse_over_timer.stop()
        self.set_mouse_over_timer.timeout.connect(lambda p=True: self.set_mouse_over(p))
        self.set_mouse_over_timer.start(10)

    def leaveEvent(self, event):
        self.set_mouse_over_timer.stop()
        self.set_mouse_over_timer.timeout.connect(lambda p=False: self.set_mouse_over(p))
        self.set_mouse_over_timer.start(1000)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = inputLabel()
    ex.show()
    sys.exit(app.exec_())