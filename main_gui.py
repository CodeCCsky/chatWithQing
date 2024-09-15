# -*- coding: utf-8 -*-
import copy
import datetime
import logging
import logging.handlers
import os
import re
import sys
import time

from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtGui import QIcon, QFontDatabase, QCloseEvent
from PyQt5.QtWidgets import QWidget, QApplication, QAction, QSystemTrayIcon, QMenu, QStyleFactory, QMessageBox


from app.GUI import (
    DesktopPet,
    SettingWidget,
    initialzationWidget,
    inputLabel,
    loadWidget,
    talkBubble,
)
from app.Threads import (
    PyQt_deepseek_request_thread,
    no_tts_sound_manager,
    summaryWorker,
    tts_thread,
)
from deepseek_api import deepseek_model, historyManager
from setting.setting_colletions import settingManager
from tts import TTSAudio
from FixJSON import fixJSON

# setting = settingManager()
tts_cache_path = r"cache/"
no_tts_sound_path = r"app/asset/sound/speak.wav"
default_history_path = r"history/"
check_pattern = re.compile(r"[\d\u4e00-\u9fff]")

SPEAK_GAP = 50

file_handler = logging.handlers.TimedRotatingFileHandler(
    "log/app.log", when="midnight", backupCount=10, encoding="utf8"
)
stream_hanlder = logging.StreamHandler()
logging.basicConfig(
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[file_handler, stream_hanlder],
)

logger = logging.getLogger(__name__)


class mainWidget(QWidget):
    S_NORMAL = 0
    S_INTENSE = 1
    S_SURPRISE = 2
    S_EYE_HALF_CLOSED = 3
    S_EYE_CLOSE_NORMAL = 4
    S_EYE_CLOSE_DEPRESSED = 5
    S_EYE_CLOSE_SMILE = 6

    def __init__(self, history_path: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.init_timer = QTimer()
        self.init_resource()

        self.is_speaking = False
        self.facial_expr_state = self.S_NORMAL
        self.init_setting(history_path)
        self.init_llm()

    def init_2(self):
        self.init_tray()
        self.init_desktop_pet()
        self.init_talk()
        self.init_stroke()
        self.setting.tts_setting.use_setting(self.tts_model)
        self.setting.deepseek_model.use_setting(self.llm_inferance)

    ### <初始化部分>
    def init_resource(self):
        """加载资源"""
        # icon
        self.BASE_ICON = QIcon(":/Icon/icon.png")
        self.QUIT_ICON = QIcon(":/Icon/exit.png")
        self.SETTING_ICON = QIcon(":/Icon/setting.png")
        self.QUIT_ICON_BLACK = QIcon(":/Icon/exit_black.png")
        self.SETTING_ICON_BLACK = QIcon(":/Icon/setting_black.png")
        # font
        fontDb = QFontDatabase()
        fontDb.addApplicationFont(":/font/荆南波波黑.ttf")

    def init_tray(self) -> None:
        """初始化托盘栏设置"""
        quit_action = QAction("退出", self)
        quit_action.setIcon(self.QUIT_ICON)
        quit_action.triggered.connect(lambda p=QCloseEvent(): self.closeEvent(p))

        setting_action = QAction("设置", self)
        setting_action.setIcon(self.SETTING_ICON)
        setting_action.triggered.connect(self.show_setting_window_event)

        show_portrait_action = QAction("显示立绘", self)
        show_portrait_action.setIcon(self.BASE_ICON)
        show_portrait_action.triggered.connect(self.show_desktop_pet)

        show_talk_bubble_action = QAction("显示气泡框", self)
        show_talk_bubble_action.setIcon(self.BASE_ICON)
        show_talk_bubble_action.triggered.connect(self.show_talk_bubble_event)

        show_input_action = QAction("显示输入框", self)
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
        self.tray_menu.setStyleSheet(
            """
            QMenu {
                background-color: black;
                color: white;
                border: 1px solid #ff0084;
            }
            QMenu::item:selected {
                background-color: gray;
            }
        """
        )

        # 托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.BASE_ICON)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def init_desktop_pet(self):
        self.desktop_pet = DesktopPet(use_tts=self.setting.tts_setting.use_tts)
        self.desktop_pet.closeEvent = self.closeEvent
        self.desktop_pet.resize(
            int(300 * self.setting.show_setting.img_show_zoom), int(400 * self.setting.show_setting.img_show_zoom)
        )
        self.desktop_pet.move(
            int(self.screen().geometry().width() * 0.95 - self.desktop_pet.width()),
            int(self.screen().geometry().height() * 0.95 - self.desktop_pet.height()),
        )
        self.desktop_pet.show()

    def init_setting(self, history_path: str):
        self.setting = settingManager()
        self.setting.load_from_file()
        self.setting.history_path = history_path
        self.setting_widget = SettingWidget()
        self.setting_widget.setting_manager.history_path = history_path
        self.setting_widget.setting_manager_backup.history_path = history_path
        self.setting_widget.changeSetting.connect(self.change_setting)
        logger.info(f"加载设置。选择的历史记录{self.setting.history_path}")

    def init_talk(self):
        self.talk_bubble = talkBubble()
        self.talk_bubble.closeEvent = self.closeEvent
        self.input_label = inputLabel()
        self.input_label.move(
            int(
                min(
                    self.desktop_pet.x() + self.desktop_pet.width() / 2 - self.input_label.width() / 2,
                    self.screen().geometry().width() - self.input_label.width(),
                )
            ),
            int(self.desktop_pet.y() - self.input_label.height() * 1.2),
        )
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
        # TTS
        self.tts_model = TTSAudio(cache_path=tts_cache_path, is_play=True)  # TODO EMOTION
        self.tts_thread: tts_thread = None
        # no TTS
        self.no_tts_sound_path = no_tts_sound_path
        self.no_tts_sound_manager = no_tts_sound_manager(self.no_tts_sound_path)

    def init_stroke(self):
        self.pet_part = None
        self.desktop_pet.stroke_area.stroked_area_signal.connect(self.progress_stroke)

    def init_llm(self):
        # summary_inference = deepseek_summary(self.setting.get_api_key(),self.setting.get_user_name())
        if self.setting.chat_summary_setting.add_same_day_summary:
            logger.info("加载历史记录中")
            self.summary_threadpool = QThreadPool()
            today_summary_worker = summaryWorker(
                api_key=self.setting.get_api_key(),
                user_name=self.setting.get_user_name(),
                history_path=self.setting.history_path,
                generate_day_summary=False,
            )
            total_task_num = today_summary_worker.get_task_num()
            if self.setting.chat_summary_setting.add_x_day_ago_summary:
                now_date = datetime.datetime.now()
                list_of_worker: list[summaryWorker] = []
                for i in range(1, self.setting.chat_summary_setting.value_of_x_day_ago + 1):
                    current_date = now_date - datetime.timedelta(days=i)
                    current_date_str = current_date.strftime("%Y%m%d")
                    file_path = os.path.join(default_history_path, f"{current_date_str}.json")
                    if not os.path.exists(file_path):
                        continue
                    current_date_worker = summaryWorker(
                        api_key=self.setting.get_api_key(),
                        user_name=self.setting.get_user_name(),
                        history_path=file_path,
                        generate_day_summary=True,
                    )
                    total_task_num += current_date_worker.get_task_num()
                    list_of_worker.append(current_date_worker)

            self.load_widget = loadWidget(total_task_num)
            today_summary_worker.signals.finish_a_task.connect(self.load_widget.finish_a_task)
            self.summary_threadpool.start(today_summary_worker)
            if self.setting.chat_summary_setting.add_x_day_ago_summary:
                for worker in list_of_worker:
                    worker.signals.finish_a_task.connect(self.load_widget.finish_a_task)
                    self.summary_threadpool.start(worker)
            self.load_widget.show()
            self.init_timer.timeout.connect(self.check_summary_thread_pool)
        self.init_timer.start(100)

    def check_summary_thread_pool(self):
        if self.summary_threadpool.activeThreadCount() == 0:
            self.init_timer.stop()
            self.history_manager = historyManager(
                user_name=self.setting.get_user_name(), history_path=self.setting.history_path
            )
            if self.setting.chat_summary_setting.add_same_day_summary:
                full_summary_str = ""
                now_date = datetime.datetime.now()
                if self.setting.chat_summary_setting.add_x_day_ago_summary:
                    for i in range(1, self.setting.chat_summary_setting.value_of_x_day_ago + 1):
                        current_date = now_date - datetime.timedelta(days=i)
                        current_date_str = current_date.strftime("%Y%m%d")
                        file_path = os.path.join(default_history_path, f"{current_date_str}.json")
                        if not os.path.exists(file_path):
                            continue
                        summary = historyManager(user_name=self.setting.get_user_name(), history_path=file_path).summary
                        full_summary_str += f"|{current_date.year}年{current_date.month}月{current_date.day}日对话记录总结: {summary}|\n"
                if self.history_manager.current_history_index > 0:
                    full_summary_str += "|今日对话记录总结:"
                    for i in range(self.history_manager.current_history_index):
                        crt_time = datetime.datetime.strptime(
                            self.history_manager.get_create_time_by_index(i), "%Y-%m-%d %H:%M:%S"
                        )
                        upd_time = datetime.datetime.strptime(
                            self.history_manager.get_update_time_by_index(i), "%Y-%m-%d %H:%M:%S"
                        )
                        full_summary_str += f"\n{crt_time.hour}:{crt_time.minute}到{upd_time.hour}:{upd_time.minute} 你与{self.setting.get_user_name()}对话历史总结:{self.history_manager.get_summary_by_index(i)}"
                    full_summary_str += "|"
                self.history_manager.set_current_summaried_history(full_summary_str)
            self.load_widget.close()
            self.load_widget = None
            self.llm_inferance = deepseek_model(self.setting.get_api_key(), self.setting.get_system_prompt())
            self.response_content = {}
            self.llm_thread = None
            self.init_2()

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
        self.setting = setting_manager
        self.setting.tts_setting.use_setting(self.tts_model)
        self.setting.deepseek_model.use_setting(self.llm_inferance)
        self.setting.load_system_prompt_main()
        self.desktop_pet.resize(
            int(300 * self.setting.show_setting.img_show_zoom), int(400 * self.setting.show_setting.img_show_zoom)
        )
        # if self.history_manager.history_path != self.setting.history_path:
        #    self.history_manager = historyManager(user_name=self.setting.user.user_name, history_path=self.setting.history_path)
        #    logger.info(f"加载 {self.setting.history_path}")
        self.setting.write_yaml()

    ### </更换设置>
    ### <处理摸摸部分>
    def progress_stroke(self, max_index: int):
        matching_dict = {0: "头", 1: "胡萝卜发卡", 2: "头发", 3: "头发", 4: "脸"}
        if self.pet_part is None:
            self.pet_part = matching_dict[max_index]
            self.input_label.statusBar.showMessage(f"你摸了摸晴的{self.pet_part}. 该状态会在下一次发送信息时携带.")

    ### </处理摸摸部分>

    ### <实现对话部分>
    def progress_sys_msg(self, clear_pet_state: bool = True) -> str:
        _time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sys_input = f"|当前时间:{_time}(24时制)|"
        # status_bar_hint = ''
        if self.pet_part is not None:
            sys_input += f"| {setting.get_user_name()}摸了摸你的{self.pet_part} |"
            if clear_pet_state:
                self.pet_part = None
        return sys_input

    def start_talk(self, input_text: str):
        # TODO 更多系统提示
        sys_input = self.progress_sys_msg()
        self.history_manager.add_user_message(user_input=input_text, sys_input=sys_input)
        self.llm_inferance.load_history(self.history_manager.get_current_history())
        self.llm_thread = PyQt_deepseek_request_thread(self.llm_inferance, self.history_manager)
        self.llm_thread.start()
        self.llm_thread.finish_signal.connect(self.progress_thinking)

    def progress_thinking(self, finish_state: str):
        response = self.llm_thread.get_response()
        try:
            self.response_content = fixJSON.loads(response)
            self.talk_bubble.update_text(self.response_content["role_thoughts"], is_thinking=True)
            if self.setting.tts_setting.use_tts:
                self.tts_thread = tts_thread(self.tts_model, self.response_content["role_response"])
                self.tts_thread.start()
                self.tts_thread.startSpeak.connect(self.start_typing)
            else:
                self.wait_until_start_talking.start(2000)
        except ValueError:
            self.talk_bubble.update_text(response)
            self.finish_this_round_of_talk()
        except KeyError:
            self.talk_bubble.update_text(response)
            self.finish_this_round_of_talk()

    def start_typing(self):
        if self.setting.tts_setting.use_tts:
            self.tts_thread.disconnect()
        self.wait_until_start_talking.stop()
        self.desktop_pet.set_speak()
        self.on_read_text = 0
        self.text_update_timer.start(150)

    def process_typing_effect(self):
        try:
            if not self.setting.tts_setting.use_tts and re.match(
                r"[\d\u4e00-\u9fff]", self.response_content["role_response"][self.on_read_text]
            ):
                self.no_tts_sound_manager.play_audio()
            self.on_read_text += 1
            self.talk_bubble.update_text(self.response_content["role_response"][: self.on_read_text])
            if self.on_read_text > len(self.response_content["role_response"]):
                self.finish_this_round_of_talk()
        except IndexError:
            self.finish_this_round_of_talk()

    def finish_this_round_of_talk(self):
        self.desktop_pet.stop_speak()
        self.text_update_timer.stop()
        self.input_label.enabled_send_text()

    ### <实现对话部分>

    def closeEvent(self, event: QCloseEvent) -> None:
        """重写closeEvent，添加确认框"""
        msgbox = QMessageBox()
        msgbox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgbox.setWindowIcon(self.QUIT_ICON_BLACK)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setWindowTitle("?")
        msgbox.setText("真的要退出吗？")
        msgbox.setInformativeText("晴小姐会伤心的。")
        _yes = msgbox.addButton("确认", QMessageBox.AcceptRole)
        _no = msgbox.addButton("取消", QMessageBox.RejectRole)
        msgbox.setDefaultButton(_no)
        # 防止托盘程序在关闭确认关闭窗口后直接关闭托盘程序
        QApplication.setQuitOnLastWindowClosed(False)
        # self.portraitView.change_emo(self.S_INTENSE, True)
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


def main():
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y%m%d")
    logger.info("设置加载完成，启动主程序中")
    pet = mainWidget(history_path=os.path.join(default_history_path, f"{current_time}.json"))
    sys.exit(main_app.exec_())


def set_setting(_setting: settingManager):
    _setting.load_system_prompt_main()
    global setting
    setting = copy.deepcopy(_setting)
    state = setting.write_yaml()
    logger.info(f"设置写入状态：{state}")


def initize():
    init = initialzationWidget()
    init.changeSetting.connect(set_setting)
    init.show()
    main_app.exec_()
    setting_check = setting.check()
    if setting_check == []:
        logger.info("成功加载设置")
        main()
    else:
        logger.warning(f'设置加载失败：存在未填入的值：{"，".join(setting_check)}')
        sys.exit()


if __name__ == "__main__":
    logger.info("程序启动")
    main_app = QApplication(sys.argv)
    setting = settingManager()
    state_num = setting.load_from_file()
    if state_num[0] == 0:
        logger.info("成功加载设置")
        main()
    else:
        logger.warning(f"err: {state_num[1]}。启动初始化。")
        initize()
