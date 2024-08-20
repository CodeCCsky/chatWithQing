import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import time
from asset.GUI.setting_gui import SettingWidget
from asset.GUI.PetView import PetGraphicsView
from asset.GUI.talk_bubble import talkBubble
from asset.GUI.input_label import inputLabel
import asset.GUI.res_rc

from deepseek_api import deepseek_model
from deepseek_api.deepseek_tools import ds_tool

class PyQt_deepseek_request_thread(QThread):
    text_update = pyqtSignal(str)
    finish_signal = pyqtSignal(str)

    def __init__(self, model: deepseek_model, update_time: int = 50):
        super().__init__()
        self.model = model
        self.total_time = 0.0
        self.response = None
        self.finish_reason = None

    def run(self):
        self.model = deepseek_model(api_key=self.api_key, system_prompt=self.system_prompt)
        self.total_time = time.time()
        self.response, self.finish_reason, _ = self.model.send_message()
        self.total_time = time.time() - self.total_time

    def update_response(self):
        new_response = self.model.get_response()
        self.text_update.emit(new_response)


class DesktopPet(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.init_resource()
        self.init_subWindow()

        # 垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.is_speaking = False
        self.facial_expr_state = self.S_NORMAL
        self.init_tray()
        self.init_setting()
        self.init_pet_image()
        self.init_mouse_click()
        self.init_paint_randnum()
        self.init_talk()

    def init_paint_randnum(self):
        self.randnum_timer = QTimer()

    def init_mouse_click(self):
        self.is_follow_mouse = False
        self.check_mouse_press_time = QTimer()
        self.check_mouse_press_time.timeout.connect(self.start_following_mouse)
        self.portraitView.mousePressEvent = self.onMousePress
        self.portraitView.mouseReleaseEvent = self.onMouseRelease
        self.portraitView.mouseMoveEvent = self.onMouseMove

    def init_resource(self):
        """加载资源"""
        # icon
        self.BASE_ICON = QIcon(':/Icon/icon.png')
        self.QUIT_ICON = QIcon(':/Icon/exit.png')
        self.SETTING_ICON = QIcon(':/Icon/setting.png')
        self.QUIT_ICON_BLACK = QIcon(':/Icon/exit_black.png')
        self.SETTING_ICON_BLACK = QIcon(':/Icon/setting_black.png')
        # font
        fontDb = QFontDatabase()
        fontDb.addApplicationFont(':/font/荆南波波黑.ttf')

    def init_subWindow(self) -> None:
        """初始化窗体
        窗口属性：无标题栏、保持在最上层、透明背景
        """
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent; border: none;")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.repaint()

    def init_tray(self) -> None:
        """初始化托盘栏设置"""

        quit_action = QAction('退出', self)
        quit_action.setIcon(self.QUIT_ICON)
        quit_action.triggered.connect(lambda p=QCloseEvent(): self.closeEvent(p))
        

        setting_action = QAction('设置', self)
        setting_action.setIcon(self.SETTING_ICON)
        setting_action.triggered.connect(self.show_setting_window_event)

        show_portrait_action = QAction('显示立绘', self)
        show_portrait_action.setIcon(self.BASE_ICON)
        show_portrait_action.triggered.connect(self.show_portrait_event)

        show_talk_bubble_action = QAction('显示气泡框', self)
        show_talk_bubble_action.setIcon(self.BASE_ICON)
        show_talk_bubble_action.triggered.connect(self.show_talk_bubble_event)

        show_input_action = QAction('显示输入框', self)
        show_input_action.setIcon(self.BASE_ICON)
        show_input_action.triggered.connect(self.show_input_event)

        # 菜单项
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction(quit_action)
        self.tray_menu.addAction(show_portrait_action)
        self.tray_menu.addAction(show_talk_bubble_action)
        self.tray_menu.addAction(show_input_action)
        self.tray_menu.addAction(setting_action)

        # 设置托盘菜单样式
        self.tray_menu.setStyle(QStyleFactory.create("Fusion"))
        self.tray_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """)

        # 托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.BASE_ICON)
        self.tray_icon.setContextMenu(self.tray_menu)

        self.tray_icon.show()

    def init_setting(self):
        # TODO
        self.setting_widget = SettingWidget()

    def init_pet_image(self):
        # 立绘的显示组件
        self.portraitView = PetGraphicsView(self)
        self.portraitView.setMinimumSize(300, 400)
        self.layout().addWidget(self.portraitView)
        screen = QDesktopWidget().screenGeometry()
        self.adjustSize()
        self.move(QPoint(int(screen.width()-self.width()/2), int(screen.height()-self.height()/2)))

    def init_talk(self):#TODO
        self.talk_bubble = talkBubble()
        self.input_label = inputLabel()
        # 链接信号和槽
        self.text_update_timer = QTimer()
        #self.text_update_timer.timeout.connect(self.talk_bubble.update_text)
        self.talk_bubble.show()

    def show_setting_window_event(self):
        #TODO
        QApplication.setQuitOnLastWindowClosed(False)
        reply = QMessageBox.information(None,'施工中','该功能暂未完成')
        QApplication.setQuitOnLastWindowClosed(True)

    def show_talk_bubble_event(self):
        self.talk_bubble.setWindowOpacity(0.99)


    def show_portrait_event(self):
        self.setWindowOpacity(0.99)

    def show_input_event(self):
        self.input_label.setWindowOpacity(0.99)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'portraitView'):
            self.portraitView.setGeometry(self.rect())

    def hide_event(self):
        self.setWindowOpacity(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        """重写closeEvent，添加确认框
        """
        msgbox = QMessageBox()
        msgbox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgbox.setWindowIcon(self.QUIT_ICON_BLACK)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setWindowTitle('?')
        msgbox.setText('真的要退出吗？')
        msgbox.setInformativeText('晴小姐会伤心的。')
        _yes = msgbox.addButton('确认', QMessageBox.AcceptRole)
        _no = msgbox.addButton('取消', QMessageBox.RejectRole)
        msgbox.setDefaultButton(_no)
        # 防止托盘程序在关闭确认关闭窗口后直接关闭托盘程序
        QApplication.setQuitOnLastWindowClosed(False)
        #self.portraitView.change_emo(self.S_INTENSE, True)
        msgbox.exec_()
        reply = msgbox.clickedButton()
        # 恢复原来设置
        QApplication.setQuitOnLastWindowClosed(True)
        if reply == _yes:
            self.say_goodbye()
            # 退出程序
            QApplication.quit()
        else:
            self.user_try_to_quit()

    def say_goodbye(self):
        self.portraitView.change_emo(self.S_INTENSE, True)
        pass
    def user_try_to_quit(self):
        pass

    def contextMenuEvent(self, event):
        """右键菜单"""
        pet_menu = QMenu()
        pet_menu.setStyleSheet("""
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """)
        quit_action = pet_menu.addAction('退出')
        hide = pet_menu.addAction('隐藏')
        action = pet_menu.exec_(self.mapToGlobal(event.pos()))
        if action == quit_action:
            self.closeEvent(QCloseEvent())
        if action == hide:
            # 设置透明度方式来隐藏宠物
            self.setWindowOpacity(0)

    ### 根据鼠标拖动方法（需手动重写组件的方法）
    def onMousePress(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos = self.pos()
            self.check_mouse_press_time.start(500)

    def onMouseRelease(self, event: QMouseEvent):
        # 释放时停止计时器、鼠标样式
        self.check_mouse_press_time.stop()
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.portraitView.unlock_facial_expr()
        self.portraitView.change_emo(self.facial_expr_state)
        if self.is_follow_mouse:
            self.is_follow_mouse = False

    def onMouseMove(self, event: QMouseEvent):
        # 更新移动时鼠标样式
        self.setCursor(QCursor(Qt.ClosedHandCursor))
        if self.is_follow_mouse:
            new_pos = self.window_pos + (event.globalPos() - self.mouse_press_pos)
            self.move(new_pos)

    def start_following_mouse(self):
        # 更新鼠标样式
        self.setCursor(QCursor(Qt.OpenHandCursor))
        #更新面部表情
        #self.facial_expr_state = self.S_EYE_CLOSE_DEPRESSED
        self.portraitView.change_emo(self.S_EYE_CLOSE_DEPRESSED, True)
        # 更新跟随鼠标状态
        self.is_follow_mouse = True
        # 停止计时器防止重复调用此函数
        self.check_mouse_press_time.stop()

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())
