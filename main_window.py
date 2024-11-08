# -*- coding: utf-8 -*-
import copy
import datetime
import logging
import logging.handlers
import os
import re
import sys
import time

now_dir = os.getcwd()
sys.path.insert(0, now_dir)

from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtGui import QIcon, QFontDatabase, QCloseEvent
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QAction,
    QSystemTrayIcon,
    QMenu,
    QStyleFactory,
    QMessageBox,
)


from app.GUI import (
    DesktopPet,
    SettingWidget,
    inputLabel,
    loadWidget,
    talkBubble,
    RetryMessageDialog,
)
from app.Threads import (
    no_tts_sound_manager,
    summaryWorker,
    tts_thread,
    fixJSONThread,
)
from third_party.deepseek_api import (
    deepseek_model,
    historyManager,
    PyQt_deepseek_request_thread,
    PyQt_deepseek_request_prefix_thread,
)
from third_party.setting_manager import settingManager
from third_party.tts import TTSAudio
from third_party.FixJSON import fixJSON
from third_party.chat_activity_manager import chat_activity_manager
from third_party.emo_manager import emo_manager
from third_party.memory_focus_manager import MemoryFocusManager

# setting = settingManager()
tts_cache_path = r"cache/"
no_tts_sound_path = r"app/asset/sound/speak.wav"
default_history_path = r"history/"
check_pattern = re.compile(r"[\d\u4e00-\u9fff]")

SPEAK_GAP = 50

TIMESENDGAP = 3


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
        self.init_chat_activity_manager()
        self.setting.tts_setting.use_setting(self.tts_model)
        self.setting.deepseek_model.use_setting(self.llm_interface, self.setting.get_system_prompt())

    ### 初始化部分
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
            int(300 * self.setting.show_setting.img_show_zoom),
            int(400 * self.setting.show_setting.img_show_zoom),
        )
        self.desktop_pet.move(
            int(self.screen().geometry().width() * 0.95 - self.desktop_pet.width()),
            int(self.screen().geometry().height() * 0.95 - self.desktop_pet.height()),
        )
        self.emo_manager = emo_manager()
        self.desktop_pet.show()

    def init_setting(self, history_path: str):
        self.setting = settingManager()
        status = self.setting.load_from_file()
        if status[0] != 0:
            logger.error("设置加载失败", exc_info=(status))
            reply = QMessageBox.critical(
                None,
                "设置加载错误",
                "设置加载失败，请尝试重新启动本程序或尝试手动修改位于setting文件夹的private_setting.yaml。\n若问题不能解决，欢迎向作者反馈。(联系方式在'README.md'或'请先读我.pdf'中)",
            )
            sys.exit(-1)
        self.setting.history_path = history_path
        self.setting_widget = SettingWidget()
        self.setting_widget.setting_manager.history_path = history_path
        self.setting_widget.setting_manager_backup.history_path = history_path
        self.setting_widget.changeSetting.connect(self.change_setting)
        self.setting_widget.changeEmoSetting.connect(self.change_emo_setting)
        logger.info(f"加载设置。选择的历史记录{self.setting.history_path}")

    def init_talk(self):
        self.current_time_counter = 0
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
        self.input_label.requestSend.connect(self.start_talk_after_add_user_msg)
        self.input_label.requestRetry.connect(self.retry_talk)
        self.fix_json_interface: fixJSONThread = None
        self.prefix_message_interface: PyQt_deepseek_request_prefix_thread = None
        self.retry_message_dialog: RetryMessageDialog = None
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
        # summary_interface = deepseek_summary(self.setting.get_api_key(),self.setting.get_user_name())
        self.summary_threadpool = QThreadPool()
        if self.setting.chatting_setting.add_same_day_summary:
            logger.info("加载历史记录中")
            today_summary_worker = summaryWorker(
                api_key=self.setting.get_api_key(),
                user_name=self.setting.get_user_name(),
                history_path=self.setting.history_path,
                generate_day_summary=False,
            )
            total_task_num = today_summary_worker.get_task_num()
            if self.setting.chatting_setting.add_x_day_ago_summary:
                now_date = datetime.datetime.now()
                list_of_worker: list[summaryWorker] = []
                for i in range(1, self.setting.chatting_setting.value_of_x_day_ago + 1):
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
            if self.setting.chatting_setting.add_x_day_ago_summary:
                for worker in list_of_worker:
                    worker.signals.finish_a_task.connect(self.load_widget.finish_a_task)
                    self.summary_threadpool.start(worker)
            self.load_widget.show()
        self.init_timer.timeout.connect(self.check_summary_thread_pool)
        self.init_timer.start(100)

    def check_summary_thread_pool(self):
        if self.summary_threadpool.activeThreadCount() == 0:
            self.init_timer.stop()
            self.focus_memory_manager = MemoryFocusManager()
            self.history_manager = historyManager()
            self.history_manager.set_user_name(self.setting.get_user_name())
            self.history_manager.load_from_file(self.setting.history_path)

            # 处理是否继续上次对话
            if self.history_manager.get_last_index() != -1:
                last_time = datetime.datetime.strptime(
                    self.history_manager.get_update_time_by_index(self.history_manager.get_last_index()),
                    "%Y-%m-%d %H:%M:%S",
                )
                twenty_min = datetime.timedelta(minutes=20)
                current_time = datetime.datetime.now()
                time_diff = current_time - last_time
                if time_diff > twenty_min:
                    self.history_manager.create_new_chat()
                else:
                    self.history_manager.set_current_index(self.history_manager.get_last_index())
                    self.history_manager.set_current_summary(None)
                    min_diff = time_diff.total_seconds() / 60
                    self.history_manager.add_user_message(
                        user_input="",
                        sys_input=f"{self.setting.get_user_name()}重新启动了程序。距上次关闭过去了{min_diff:.1f}分钟",
                    )
            else:
                self.history_manager.create_new_chat()

            self.focus_memory_manager.update_cache_clear()
            if self.focus_memory_manager.get_important_memory() != []:
                self.history_manager.add_user_message(
                    user_input="",
                    sys_input=f"加载的历史重要记忆:{'|'.join(self.focus_memory_manager.get_important_memory())}",
                )
            if self.focus_memory_manager.get_cache_memory() != {}:
                list_of_cache_memeory = []
                for key, value in self.focus_memory_manager.get_cache_memory().items():
                    list_of_cache_memeory.append(f"{key}: {'# '.join([content for content, _ in value])}")
                joined_cache_memory = "\n".join(list_of_cache_memeory)
                self.history_manager.add_user_message("", f"加载的部分历史缓存记忆:{joined_cache_memory}")

            if self.setting.chatting_setting.add_same_day_summary:
                full_summary_str = ""
                now_date = datetime.datetime.now()
                if self.setting.chatting_setting.add_x_day_ago_summary:
                    for i in range(1, self.setting.chatting_setting.value_of_x_day_ago + 1):
                        current_date = now_date - datetime.timedelta(days=i)
                        current_date_str = current_date.strftime("%Y%m%d")
                        file_path = os.path.join(default_history_path, f"{current_date_str}.json")
                        if not os.path.exists(file_path):
                            continue
                        summary = historyManager(
                            user_name=self.setting.get_user_name(),
                            history_path=file_path,
                        ).get_overall_summary()

                        full_summary_str += f"|{current_date.year}年{current_date.month}月{current_date.day}日对话记录总结: {summary}|\n"
                if self.history_manager.current_history_index > 0:
                    full_summary_str += "|今日对话记录总结:"
                    for i in range(self.history_manager.current_history_index):
                        crt_time = datetime.datetime.strptime(
                            self.history_manager.get_create_time_by_index(i),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        upd_time = datetime.datetime.strptime(
                            self.history_manager.get_update_time_by_index(i),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        full_summary_str += f"\n{crt_time.hour}:{crt_time.minute}到{upd_time.hour}:{upd_time.minute} 你与{self.setting.get_user_name()}对话历史总结:{self.history_manager.get_summary_by_index(i)}"
                    full_summary_str += "|"
                self.history_manager.set_current_summaried_history(full_summary_str)
            self.load_widget.close()
            self.load_widget = None
            self.llm_interface = deepseek_model(self.setting.get_api_key(), self.setting.get_system_prompt())
            self.response_content = {}
            self.llm_thread = None
            self.init_2()

    def init_chat_activity_manager(self):
        # TODO 自定义等待时间列表？
        self.chat_activity_manager = chat_activity_manager(
            self.history_manager,
            self.setting,
        )
        self.chat_activity_manager.chatActivityTimeout.connect(self.progress_wakeup)
        self.input_label.requestSend.connect(self.chat_activity_manager.reset_wakeup)
        self.input_label.input_edit.textChanged.connect(self.chat_activity_manager.reset_wakeup)
        if self.setting.chatting_setting.enable_self_activation:
            self.chat_activity_manager.start_timer()

    ### '显示组件'选项部分
    def show_setting_window_event(self):
        self.setting_widget.show_window()

    def show_talk_bubble_event(self):
        self.talk_bubble.show_window()

    def show_input_event(self):
        self.input_label.show_window()

    def show_desktop_pet(self):
        self.desktop_pet.show_window()

    ### 更换设置
    def change_setting(self, setting_manager: settingManager):
        logger.info("已更新设置")
        if setting_manager.user != self.setting.user:
            diff_list = []
            for (key1, value1), (key2, value2) in zip(
                self.setting.user.get_dict().items(),
                setting_manager.user.get_dict().items(),
            ):
                diff_list.append(f"{key1}:{value1}->{value2}")
            self.history_manager.add_user_message(
                user_input="",
                sys_input=f"检测到对{self.setting.get_user_name()}认知设置变更: {', '.join(diff_list)}",
            )

            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            cache_memory = self.focus_memory_manager.get_cache_memory()
            value_list = cache_memory.get(current_date, [])
            if value_list != []:
                value_list = [value for value in value_list if not value[0].startswith(f"认知设置变更: ")]
            value_list.append(
                (
                    f"认知设置变更: {', '.join(diff_list)}",
                    int(self.setting.chatting_setting.value_of_x_day_ago),
                )
            )
            cache_memory[current_date] = value_list
            self.focus_memory_manager.set_cache_memory(cache_memory)
            self.focus_memory_manager.save_file()
            if self.setting.get_user_name() != setting_manager.get_user_name():
                self.history_manager.change_user_name(setting_manager.get_user_name())
        if (
            not self.setting.chatting_setting.enable_self_activation
            and setting_manager.chatting_setting.enable_self_activation
        ):
            self.chat_activity_manager.start_timer()
        self.setting = copy.deepcopy(setting_manager)
        self.setting.load_system_prompt_main()
        # TODO 认知更改后处理
        self.setting.tts_setting.use_setting(self.tts_model)
        self.setting.deepseek_model.use_setting(self.llm_interface, self.setting.get_system_prompt())
        self.desktop_pet.resize(
            int(300 * self.setting.show_setting.img_show_zoom),
            int(400 * self.setting.show_setting.img_show_zoom),
        )
        self.setting.write_yaml()

    def change_emo_setting(self, emotion_setting: emo_manager):
        self.emo_manager = copy.deepcopy(emotion_setting)
        self.emo_manager.write_yaml()

    ### 处理摸摸部分
    def progress_stroke(self, max_index: int):
        matching_dict = {0: "头", 1: "胡萝卜发卡", 2: "头发", 3: "头发", 4: "脸"}
        if self.pet_part is None:
            self.pet_part = matching_dict[max_index]
            self.input_label.statusBar.showMessage(f"你摸了摸晴的{self.pet_part}. 该状态会在下一次发送信息时携带.")

    ### 处理自激活部分

    def progress_wakeup(self, wait_time: int):
        input_text = self.input_label.input_edit.toPlainText()
        self.input_label.sendButton.setEnabled(False)
        if wait_time != -1:
            sys_text = f"{self.setting.get_user_name()}超过{wait_time}分钟未更新输入|"
        else:
            sys_text = f"{self.setting.get_user_name()}超过{wait_time}分钟未更新输入。超过自激活功能最大时间，自激活功能关闭，你需要等待到下一次{self.setting.get_user_name()}输入时才能重启自激活功能|"
        # 考虑换个更好的功能？（也许是屏幕识别？）
        # if input_text and random.randint(1, 10) > 3:
        #    sys_text += f"你偷看了{self.setting.get_user_name()}的输入框,已输入的文本如下:{input_text}|"
        self.start_talk_after_add_user_msg("", sys_text)

    ### 实现对话部分
    def progress_sys_msg(self, sys: str, clear_pet_state: bool = True) -> str:
        sys = str(sys)
        _time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sys_input = f"|当前时间{_time}(24时制)|{sys}" if self.current_time_counter == 0 else f"|{sys}"
        self.current_time_counter = (self.current_time_counter + 1) % TIMESENDGAP
        # status_bar_hint = ''
        if self.pet_part is not None:
            sys_input += f"{self.setting.get_user_name()}摸了摸你的{self.pet_part}|"
            if clear_pet_state:
                self.pet_part = None
        return sys_input

    def start_talk_after_add_user_msg(self, input_text: str, sys: str = ""):
        sys_input = self.progress_sys_msg(sys)
        self.history_manager.add_user_message(user_input=input_text, sys_input=sys_input)
        self.history_manager.save_history()
        self.start_talk()

    def start_talk(self):
        self.llm_interface.load_history(self.history_manager.get_current_history())
        self.llm_thread = PyQt_deepseek_request_thread(self.llm_interface, self.history_manager)
        self.llm_thread.start()
        self.llm_thread.finish_signal.connect(self.progress_decode_response)

    def retry_talk(self):
        self.llm_interface.load_history(self.history_manager.get_current_history())
        self.llm_thread = PyQt_deepseek_request_thread(self.llm_interface, self.history_manager)
        self.llm_thread.start()
        self.llm_thread.finish_signal.connect(self.progress_decode_response)

    def progress_decode_response(self, finish_state: str):
        def _get_response() -> str:
            if self.llm_thread is not None:
                _response = self.llm_thread.get_response()
            elif self.prefix_message_interface is not None:
                _response = self.prefix_message_interface.get_full_response()
            else:
                raise ValueError("llm_thread and prefix_message_interface is None")
            self.llm_thread.disconnect()
            self.llm_thread = None
            self.prefix_message_interface = None
            return _response

        # finish_reason: stop, length, content_filter, tool_calls, insufficient_system_resource
        if finish_state == "stop":
            response = _get_response()
            try:
                self.response_content = fixJSON.loads(response)
                self.history_manager.add_assistant_message(self.response_content)
                self.history_manager.save_history()
                self.progress_thinking()
            except (ValueError, KeyError):
                self.talk_bubble._setTextLabel("", "返回格式有误，尝试修复中")
                self.fix_json_interface = fixJSONThread(response, self.setting.get_api_key())
                self.fix_json_interface.isFixed.connect(self.progress_failed_auto_json_fix)
                self.fix_json_interface.start()
        elif finish_state == "tool_calls":
            # TODO
            self.finish_this_round_of_talk()
        elif finish_state == "length":
            response = _get_response()
            self.prefix_message_interface = PyQt_deepseek_request_prefix_thread(
                self.llm_interface, response, self.history_manager
            )
            self.prefix_message_interface.finish_signal.connect(self.progress_decode_response)
            self.prefix_message_interface.start()
        else:
            if finish_state == "content_filter":
                self.talk_bubble._setTextLabel("", "**错误：回复被过滤**")
            elif finish_state == "insufficient_system_resource":
                self.talk_bubble._setTextLabel("", "**错误：API推理资源不足，回复被打断**")
            last_user_msg = {}
            while last_user_msg.get("role", None) != "user":
                last_user_msg = self.history_manager.pop_to_wait_to_del_msgs()
            if self.retry_message_dialog:
                QApplication.setQuitOnLastWindowClosed(False)
                self.retry_message_dialog.continueRetry.disconnect(self.progress_retry_message_dialog_retruns)
                self.retry_message_dialog.ignoreRetry.disconnect(self.ignore_retry_message_dialog_returns)
                self.retry_message_dialog.close()
                self.retry_message_dialog.deleteLater()
                self.retry_message_dialog = None
            QTimer.singleShot(0, self.create_retry_message_dialog)  # TODO test

    def create_retry_message_dialog(self):
        QApplication.setQuitOnLastWindowClosed(True)
        self.retry_message_dialog = RetryMessageDialog(self.history_manager)
        self.retry_message_dialog.continueRetry.connect(self.progress_retry_message_dialog_retruns)
        self.retry_message_dialog.ignoreRetry.connect(self.ignore_retry_message_dialog_returns)
        self.retry_message_dialog.show()

    def ignore_retry_message_dialog_returns(self):
        self.history_manager.clear_wait_to_del_msgs()
        self.finish_this_round_of_talk()

    def progress_retry_message_dialog_retruns(self, continue_retry: list):  # TODO   <=== 未完成
        for msg_data in continue_retry[::-1]:
            if msg_data["role"] == "user":
                self.history_manager.add_user_message(
                    msg_data["content"][self.setting.get_user_name()], msg_data["content"]["sys"]
                )
            elif msg_data["role"] == "assistant":
                self.history_manager.add_assistant_message(msg_data["content"])
            elif msg_data["role"] == "tool":
                self.history_manager.add_assistant_message(msg_data["content"])
        self.history_manager.clear_wait_to_del_msgs()
        self.start_talk()

    def progress_failed_auto_json_fix(self, is_fixed: bool):
        self.fix_json_interface.isFixed.disconnect()
        self.response_content = self.fix_json_interface.get_response()
        self.history_manager.add_assistant_message(self.response_content)
        self.history_manager.save_history()
        if is_fixed:
            self.progress_thinking()
        else:
            self.talk_bubble.update_text(self.response_content)
            self.finish_this_round_of_talk()

    def progress_thinking(self):
        self.talk_bubble.update_text(self.response_content["role_thoughts"], is_thinking=True)
        if not self.setting.emo_setting.show_in_text:
            self.response_content["role_response"] = self.emo_manager.process_string(
                self.response_content["role_response"]
            )
        self.emo_manager.write_yaml()
        if self.setting.tts_setting.use_tts:
            self.tts_thread = tts_thread(self.tts_model, self.response_content["role_response"])
            self.tts_thread.startSpeak.connect(self.start_typing)
            self.tts_thread.start()
        else:
            self.wait_until_start_talking.start(2000)

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
                r"[\d\u4e00-\u9fff]",
                self.response_content["role_response"][0][self.on_read_text],
            ):
                self.no_tts_sound_manager.play_audio()
            vaild_emo_key = [key for key in self.response_content["role_response"][1] if key <= self.on_read_text]
            if not vaild_emo_key:
                current_emo = 0
            else:
                current_emo = self.response_content["role_response"][1][max(vaild_emo_key)]
                current_emo = current_emo if current_emo != -1 else 0
            self.desktop_pet.change_emo(current_emo)
            self.on_read_text += 1
            self.talk_bubble.update_text(self.response_content["role_response"][0][: self.on_read_text])
            if self.on_read_text > len(self.response_content["role_response"][0]):
                self.finish_this_round_of_talk()
        except IndexError:
            self.finish_this_round_of_talk()

    def finish_this_round_of_talk(self):
        self.desktop_pet.stop_speak()
        self.text_update_timer.stop()
        self.input_label.enabled_send_text()

    ### 其他

    def closeEvent(self, event: QCloseEvent) -> None:
        """重写closeEvent，添加确认框"""
        msgbox = QMessageBox()
        msgbox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgbox.setWindowIcon(self.QUIT_ICON_BLACK)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setWindowTitle("退出")
        msgbox.setText("真的要退出吗？")
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
        self.history_manager.add_user_message(user_input="", sys_input=f"{self.setting.get_user_name()}退出了程序。")
        self.history_manager.save_history()

    def user_try_to_quit(self):
        pass
