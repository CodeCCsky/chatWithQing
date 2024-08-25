# -*- coding: utf-8 -*-
import os
import time
from collections import deque
import json
import re
from typing import Union
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSoundEffect

from asset.GUI.setting_gui import SettingWidget
from asset.GUI.desktop_pet import DesktopPet
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

class no_tts_sound_thread(QThread):
    def __init__(self):
        super().__init__()
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(no_tts_sound_path))
    def run(self):
        self.sound.play()


class mainWidget(QWidget):
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
        self.use_tts = use_tts

        self.is_speaking = False
        self.facial_expr_state = self.S_NORMAL
        self.init_tray()
        self.init_setting()
        self.init_desktop_pet()
        self.init_talk()
        self.init_llm()

### 初始化部分
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
        show_portrait_action.triggered.connect(self.show_desktop_pet)

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

    def init_desktop_pet(self):
        self.desktop_pet = DesktopPet(use_tts=self.use_tts)
        self.desktop_pet.closeEvent = self.closeEvent
        self.desktop_pet.show()

    def init_setting(self):
        # TODO
        self.setting_widget = SettingWidget()

    def init_talk(self):#TODO
        self.talk_bubble = talkBubble()
        self.talk_bubble.closeEvent = self.closeEvent
        self.input_label = inputLabel()
        self.input_label.closeEvent = self.closeEvent
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

    def init_llm(self):
        self.history_manager = historyManager(setting.get_user_name(), history_path)
        self.llm_inferance = deepseek_model(setting.get_api_key(), setting.get_system_prompt())
        self.response_content = {}
        self.llm_thread = None
### 初始化部分

### '显示组件'选项部分
    def show_setting_window_event(self):
        #TODO
        QApplication.setQuitOnLastWindowClosed(False)
        reply = QMessageBox.information(None,'施工中','该功能暂未完成')
        QApplication.setQuitOnLastWindowClosed(True)

    def show_talk_bubble_event(self):
        self.talk_bubble.show_window()

    def show_input_event(self):
        self.input_label.show_window()

    def show_desktop_pet(self):
        self.desktop_pet.show_window()
### '显示组件'选项部分

### 实现对话部分
    def start_talk(self,input_text: str):
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
        self.desktop_pet.set_speak()
        if self.use_tts:
            self.tts_thread = tts_thread(self.tts_model,self.response_content['role_response'])
        else:
            self.no_tts_list = []
        self.on_read_text = 0
        self.text_update_timer.start(150)

    def process_typing_effect(self):
        try:
            if check_pattern.match(self.response_content['role_response'][self.on_read_text]) and self.use_tts is False:
                self.no_tts_list.append(no_tts_sound_thread())
                self.no_tts_list[-1].start()
            self.on_read_text += 1
            self.talk_bubble.update_text(self.response_content['role_response'][:self.on_read_text])
        except IndexError:
            self.finish_this_round_of_talk()

    def finish_this_round_of_talk(self):
        self.desktop_pet.stop_speak()
        self.text_update_timer.stop()
        self.input_label.enabled_send_text()
### 实现对话部分

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

if __name__ == '__main__' :
    
    app = QApplication(sys.argv)
    pet = mainWidget()
    sys.exit(app.exec_())
