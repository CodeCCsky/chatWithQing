import sys
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QStatusBar
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import asset.GUI.res_rc
#import res_rc

class inputLabel(QWidget):
    requestSend = pyqtSignal(str)

    def __init__(self,parent = None):
        super().__init__(parent)
        self.input_font_size = 16
        self.button_font_size = 16
        self.input_font = QFont('SimHei',self.input_font_size)
        self.button_font = QFont('SimHei',self.button_font_size)
        self.initUI()
    
    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(':/font/荆南波波黑.ttf')
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(int(screen.width()*0.8-400/2),int(screen.height()*0.5),400,300)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
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
        self.input_edit.textChanged.connect(self.show_token)
        #self.input_edit.setStyleSheet("background: transparent;color: white;border: 4px solid lightgreen;padding: 1px;")
        self.clearButton.setFont(self.button_font)
        self.sendButton.setFont(self.button_font)

        self.clearButton.setText("清除文本")
        self.clearButton.clicked.connect(self.clear_text)
        self.sendButton.setText("发送")
        self.sendButton.clicked.connect(self.send_text)
        

        self.pushButton.setIcon(QIcon(":/Icon/minimize.png"))
        self.pushButton.setIconSize(self.pushButton.size())
        self.pushButton.setStyleSheet("background: none; border: none;")

    def show_token(self):
        if len(self.input_edit.toPlainText()) != 0:
            self.statusBar.showMessage(f'预计输入的token数(不准确，仅供参考): {int(len(self.input_edit.toPlainText())*0.6)} Tokens')

    def clear_text(self):
        self.input_edit.setPlainText('')

    def send_text(self):
        self.sendButton.setEnabled(False)
        self.input_edit.setEnabled(False)
        if self.input_edit.toPlainText():
            self.statusBar.showMessage(f'发送中...')
            self.requestSend.emit(self.input_edit.toPlainText())
            self.clear_text()

    def enabled_send_text(self):
        self.sendButton.setEnabled(True)
        self.input_edit.setEnabled(True)

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