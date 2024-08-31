# -*- coding: utf-8 -*-
import os
import time
import queue
import json
import re
from typing import Union
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from asset.GUI import DesktopPet, inputLabel, talkBubble, SettingWidget
from asset.Threads import tts_thread, no_tts_sound_manager, PyQt_deepseek_request_thread, get_token_num_thread
import asset.GUI.res_rc

from deepseek_api import deepseek_model, historyManager, offline_tokenizer
from setting.setting_colletions import settingManager
from tts import TTSAudio

setting = settingManager()
history_path = None
tts_cache_path = r"cache/"
no_tts_sound_path = r"asset\sound\speak.wav"
check_pattern = re.compile(r'[\d\u4e00-\u9fff]')

SPEAK_GAP = 50

class mainWidget(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6
    def __init__(self, parent: QWidget = None, use_tts:bool = False) -> None: #TODO use_tts 由设置面板控制
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
        self.init_stroke()
        self.init_text2token()

### <初始化部分>
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
        self.setting_widget.changeSetting.connect(self.change_setting)

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
            self.tts_model = TTSAudio(cache_path=tts_cache_path,is_play=True) # TODO EMOTION
            self.tts_thread:tts_thread = None
        else:
            self.no_tts_sound_path = no_tts_sound_path
            self.no_tts_sound_manager = no_tts_sound_manager(self.no_tts_sound_path)

    def init_stroke(self):
        self.pet_part = None
        self.desktop_pet.stroke_area.stroked_area_signal.connect(self.progress_stroke)

    def init_llm(self):
        self.history_manager = historyManager(setting.get_user_name(), history_path)
        self.llm_inferance = deepseek_model(setting.get_api_key(), setting.get_system_prompt())
        self.response_content = {}
        self.llm_thread = None

    def init_text2token(self):
        self.tokenizer = offline_tokenizer()
        self.input_label.getTokens.connect(self.progress_text2token)
        self.text2token_thread = None
### </初始化部分>

### <'显示组件'选项部分>
    def show_setting_window_event(self):
        self.setting_widget.setVisible(True)

    def show_talk_bubble_event(self):
        self.talk_bubble.show_window()

    def show_input_event(self):
        self.input_label.show_window()

    def show_desktop_pet(self):
        self.desktop_pet.show_window()
### </'显示组件'选项部分>
### <更换设置>
    def change_setting(self, setting_manager: settingManager):
        global setting
        setting = setting_manager
        if self.history_manager.history_path != setting.histoy_path:
            self.history_manager = historyManager(setting.user.user_name, setting.histoy_path)
            print(f"加载 {setting.histoy_path}") #TODO logger

### </更换设置>
### <处理摸摸部分>
    def progress_stroke(self, max_index: int):
        matching_dict = {
            0 : '头',
            1 : '胡萝卜发卡',
            2 : '头发',
            3 : '头发',
            4 : '脸'
        }
        if self.pet_part is None:
            self.pet_part = matching_dict[max_index]
            self.input_label.statusBar.showMessage(f"你摸了摸晴的{self.pet_part}. 该状态会在下一次发送信息时携带.")
### </处理摸摸部分>
### <处理预计token数部分>
    def progress_text2token(self, text: str):
        sys_msg = self.progress_sys_msg(False)
        tpl_text = self.history_manager.get_user_message_template(setting.get_user_name(), text, sys_msg)
        self.text2token_thread = get_token_num_thread(text=tpl_text, tokenizer=self.tokenizer)
        self.text2token_thread.responseTokenNum.connect(self.input_label.show_token)
        self.text2token_thread.run()
### </处理预计token数部分>

### <实现对话部分>
    def progress_sys_msg(self, clear_pet_state: bool = True) -> str:
        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        sys_input = f'|当前时间:{_time}(24时制)|'
        #status_bar_hint = ''
        if self.pet_part is not None:
            sys_input += f'| {setting.get_user_name()}摸了摸你的{self.pet_part} |'
            if clear_pet_state:
                self.pet_part = None
        return sys_input

    def start_talk(self,input_text: str):
        # TODO 更多系统提示
        sys_input = self.progress_sys_msg()
        self.history_manager.add_user_message(user_input=input_text, sys_input=sys_input)
        self.llm_inferance.load_history(self.history_manager.get_history())
        self.llm_thread = PyQt_deepseek_request_thread(self.llm_inferance, self.history_manager)
        self.llm_thread.start()
        self.llm_thread.finish_signal.connect(self.progress_thinking)

    def progress_thinking(self, finish_state: str):
        response = self.llm_thread.get_response()
        try:
            self.response_content = json.loads(response)
            self.talk_bubble.update_text(self.response_content['role_thoughts'], is_thinking=True)
            
            if self.use_tts:
                self.tts_thread = tts_thread(self.tts_model,self.response_content['role_response'])
                self.tts_thread.start()
                self.tts_thread.startSpeak.connect(self.start_typing)
            else:
                self.wait_until_start_talking.start(2000)
        except ValueError:
            self.talk_bubble.update_text(response)
        except KeyError:
            self.talk_bubble.update_text(response)

    def start_typing(self):
        if self.use_tts:
            self.tts_thread.disconnect()
        self.wait_until_start_talking.stop()
        self.desktop_pet.set_speak()
        self.on_read_text = 0
        self.text_update_timer.start(150)

    def process_typing_effect(self):
        try:
            if not self.use_tts and re.match(r'[\d\u4e00-\u9fff]',self.response_content['role_response'][self.on_read_text]):
                self.no_tts_sound_manager.play_audio()
            self.on_read_text += 1
            self.talk_bubble.update_text(self.response_content['role_response'][:self.on_read_text])
            if self.on_read_text > len(self.response_content['role_response']):
                self.finish_this_round_of_talk()
        except IndexError:
            self.finish_this_round_of_talk()

    def finish_this_round_of_talk(self):
        self.desktop_pet.stop_speak()
        self.text_update_timer.stop()
        self.input_label.enabled_send_text()
### <实现对话部分>

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
    setting.load_from_file()
    pet = mainWidget()
    sys.exit(app.exec_())
