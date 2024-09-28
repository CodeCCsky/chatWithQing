import datetime
import logging
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

from third_party.deepseek_api import deepseek_summary, historyManager

logger = logging.getLogger(__name__)

class summaryWorker(QRunnable):
    class Signals(QObject):
        all_finished = pyqtSignal()
        finish_a_task = pyqtSignal()

    def __init__(self, api_key: str, user_name: str, history_path: str, generate_day_summary: bool) -> None:
        super().__init__()
        self.user_name = user_name
        self.history_path = history_path
        self.history_manager = historyManager()
        self.history_manager.set_user_name(user_name)
        self.history_manager.load_from_file(history_path)
        self.history_manager.create_new_chat()
        self.interface = deepseek_summary(api_key, user_name)
        self.generate_day_summary = generate_day_summary
        self.signals = self.Signals()

    def get_task_num(self):
        return self.history_manager.current_history_index

    def run(self):
        logger.debug(f"处理{self.history_path}的子线程已启动")
        current_day_summary_list = []
        for i in range(self.history_manager.get_last_index()):
            if not self.history_manager.get_summary_by_index(i):
                logger.debug(f"处理{self.history_path}的子线程 - 第{i}项未检测到总结，生成中")
                self.history_manager.set_summary_by_index(
                    i, self.interface.get_chat_summary(self.history_manager.get_history_dict_by_index(i))[0]
                )
                self.history_manager.save_history()
            crt_time = datetime.datetime.strptime(self.history_manager.get_create_time_by_index(i), "%Y-%m-%d %H:%M:%S")
            upd_time = datetime.datetime.strptime(self.history_manager.get_update_time_by_index(i), "%Y-%m-%d %H:%M:%S")
            current_day_summary_list.append(
                f"|{crt_time.hour}:{crt_time.minute}到{upd_time.hour}:{upd_time.minute} 你与{self.user_name}对话历史总结:{self.history_manager.get_summary_by_index(i)}|"
            )
            if self.signals is not None:
                self.signals.finish_a_task.emit()
        if self.generate_day_summary and not self.history_manager.summary:
            logger.debug(f"处理{self.history_path}的子线程 - 未检测到当天总结，生成中")
            self.history_manager.set_overall_summary(
                self.interface.get_day_summary(self.history_manager.get_full_data())[0]
            )
            self.history_manager.save_history()
        logger.debug(f"处理{self.history_path}的子线程 处理完成")
        if self.signals is not None:
            self.signals.all_finished.emit()
            self.signals.finish_a_task.emit()
