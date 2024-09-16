import logging
import random
from third_party.deepseek_api import historyManager
from third_party.setting import settingManager
from third_party.chat_activity_manager.topic_complete_check import topic_check_thread
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


logger = logging.getLogger(__name__)


class chat_activity_manager(QObject):
    chatActivityTimeout = pyqtSignal(int)

    def __init__(
        self,
        history_manager: historyManager,
        setting_manager: settingManager,
        wakeup_time: list = [5, 5, 10, 10, 15, 15, 20, 20, 20],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.history_manager = history_manager
        self.setting_manager = setting_manager
        self.wakeup_time = wakeup_time
        self.current_wait_index = 0
        self.is_complete_topic = False
        self.check_thread = None
        self.wait_timer = QTimer()
        self.wait_timer.timeout.connect(self.start_check_complete_topic)

    def start_timer(self):
        logger.info("自激活模块开启")
        self.wait_timer.start(int(self.wakeup_time[self.current_wait_index] * 60 * 1000))

    def reset_wakeup(self, *args) -> None:
        self.wait_timer.stop()
        self.current_wait_index = 0
        self.wait_timer.start(int(self.wakeup_time[self.current_wait_index] * 60 * 1000))

    def start_check_complete_topic(self) -> None:
        logger.info(f"自激活时间节点到达 {self.current_wait_index+1}/{len(self.wakeup_time)}")
        self.wait_timer.stop()
        if self.current_wait_index == 0:
            self.check_thread = topic_check_thread(self.history_manager, self.setting_manager)
            self.check_thread.result.connect(self.progress_wakeup)
            self.check_thread.start()
        else:
            self.progress_wakeup(self.is_complete_topic)

    def progress_wakeup(self, is_complete_topic: bool) -> None:
        self.is_complete_topic = is_complete_topic
        # wait_time = sum(self.wakeup_time[: self.current_wait_index])
        wait_time = (self.current_wait_index + 1) * 10  # TESE
        if self.current_wait_index == len(self.wakeup_time) - 2:
            logger.info("自激活中...已达最大自激活次数，在这次自激活后将关闭该模块。下次需要输入文本来重启自激活模块")
            self.chatActivityTimeout.emit(-1)
            return None
        self.current_wait_index += 1
        if self.is_complete_topic:
            if random.randint(0, wait_time) > min(wait_time, 30) * 0.6:
                logger.info("自激活中")
                self.chatActivityTimeout.emit(wait_time)
        else:
            logger.info("自激活中")
            self.chatActivityTimeout.emit(wait_time)
        self.wait_timer.start(int(self.wakeup_time[self.current_wait_index] * 60 * 1000))
