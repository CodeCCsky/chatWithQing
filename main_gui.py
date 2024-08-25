# -*- coding: utf-8 -*-
import os
import time
import json
import re
from typing import Union
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from asset.GUI.setting_gui import SettingWidget
from asset.GUI.PetView import PetGraphicsView
from asset.GUI.talk_bubble import talkBubble
from asset.GUI.input_label import inputLabel
import asset.GUI.res_rc

from deepseek_api import deepseek_model, historyManager
from deepseek_api.deepseek_tools import ds_tool
from setting_reader import settingReader
from tts import TTSAudio

setting = settingReader()
history_path = None
tts_cache_path = r"cache/"
no_tts_sound_path = r"asset\sound\speak.wav"
check_pattern = re.compile(r'[\d\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF\u0041-\u005A\u0061-\u007A]')

SPEAK_GAP = 50

class PyQt_deepseek_request_thread(QThread):
    text_update = pyqtSignal(str)
    finish_signal = pyqtSignal(str)

    def __init__(self, model: deepseek_model, history_namager: historyManager) -> None:
        super().__init__()
        self.model = model
        self.history_manager = history_namager
        self.response = None
        self.finish_reason = None

    def run(self) -> None:
        self.response, self.finish_reason, _ = self.model.send_message()
        self.history_manager.add_assistant_message(self.response)
        self.finish_signal.emit(self.finish_reason)

    def get_status(self) -> Union[str, None]:
        return self.model.is_done()

    def get_response(self) -> str:
        return self.response

class tts_thread(QThread):# TODO test
    def __init__(self, tts_model: TTSAudio, tts_text: str) -> None:
        super().__init__()
        self.tts_model = tts_model
        self.tts_text = tts_text
    def run(self) -> None:
        self.tts_model.tts_request(self.tts_text)

class noTTSAudioPlayer:
    def __init__(self, max_players=5):
        self.max_players = max_players
        self.media_players = [QMediaPlayer() for _ in range(max_players)]
        self.audio_file = no_tts_sound_path
        self.audio_queue = []

    def play_audio(self):
        self.audio_queue.append(self.audio_file)
        self._play_next_audio()

    def _play_next_audio(self):
        if self.audio_queue:
            for player in self.media_players:
                if player.state() == QMediaPlayer.StoppedState:
                    next_audio = self.audio_queue.pop(0)
                    player.setMedia(QMediaContent(QUrl.fromLocalFile(next_audio)))
                    player.play()
                    break

    def _check_queue(self):
        self._play_next_audio()

class DesktopPet(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6
    def __init__(self, parent: QWidget = None, use_tts:bool = False) -> None:
        super().__init__(parent)
        self.init_resource()
        self.init_subWindow()
        self.use_tts = use_tts

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
        self.init_talk()
        self.init_llm()

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
        self.move(QPoint(int(screen.width()*0.95-self.width()), int(screen.height()*0.95-self.height())))

    def init_talk(self):#TODO
        self.talk_bubble = talkBubble()
        self.input_label = inputLabel()
        self.input_label.requestSend.connect(self.start_talk)
        # 链接信号和槽
        self.text_update_timer = QTimer()
        self.text_update_timer.timeout.connect(self.process_typing_effect)
        self.wait_until_start_talking = QTimer()
        self.wait_until_start_talking.timeout.connect(self.start_typing)
        self.on_read_text = 0
        self.talk_bubble.show()
        self.input_label.show()
        if self.use_tts:
            self.tts_model = TTSAudio(tts_cache_path,is_play=True) # TODO EMOTION
            self.tts_thread:tts_thread = None
        else:
            self.no_tts_sound = noTTSAudioPlayer()

    def init_llm(self):
        self.history_manager = historyManager(setting.get_user_name(), history_path)
        self.llm_inferance = deepseek_model(setting.get_api_key(), setting.get_system_prompt())
        self.response_content = {}
        self.llm_thread = None

    def show_setting_window_event(self):
        #TODO
        QApplication.setQuitOnLastWindowClosed(False)
        reply = QMessageBox.information(None,'施工中','该功能暂未完成')
        QApplication.setQuitOnLastWindowClosed(True)

    def show_talk_bubble_event(self):
        self.talk_bubble.show_window()

    def start_talk(self,input_text: str):
        #TODO
        self.history_manager.add_user_message(input_text)
        self.llm_inferance.load_history(self.history_manager.get_history())
        self.llm_thread = PyQt_deepseek_request_thread(self.llm_inferance, self.history_manager)
        self.llm_thread.start()
        self.llm_thread.finish_signal.connect(self.progress_thinking)

    def progress_thinking(self, finish_state: str):
        response = self.llm_thread.get_response()
        try:
            self.response_content = json.loads(response)
            self.talk_bubble.update_text(self.response_content['role_thoughts'], is_thinking=True)
            self.wait_until_start_talking.start(2000)
        except ValueError:
            self.talk_bubble.update_text(response)
        except KeyError:
            self.talk_bubble.update_text(response)

    def start_typing(self):
        self.wait_until_start_talking.stop()
        self.portraitView.set_speak()
        if self.use_tts:
            self.tts_thread = tts_thread(self.tts_model,self.response_content['role_response'])
        self.on_read_text = 0
        self.text_update_timer.start(150)

    def process_typing_effect(self):        #TODO
        try:
            if check_pattern.match(self.response_content['role_response'][self.on_read_text]) and self.use_tts is False:
                self.no_tts_sound.play_audio()
            self.on_read_text += 1
            self.talk_bubble.update_text(self.response_content['role_response'][:self.on_read_text])
        except IndexError:
            self.finish_this_round_of_talk()

    def finish_this_round_of_talk(self):
        #TODO
        self.portraitView.stop_speak()
        self.text_update_timer.stop()
        self.input_label.enabled_send_text()
        pass 

    def show_portrait_event(self):
        self.setWindowOpacity(0.99)

    def hide_portrait_event(self):
        self.setWindowOpacity(0)

    def show_input_event(self):
        self.input_label.show_window()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'portraitView'):
            self.portraitView.setGeometry(self.rect())

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
