
import datetime
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from deepseek_api import deepseek_summary, historyManager

class summaryWorker(QRunnable):
    class Signals(QObject):
        all_finished = pyqtSignal()
        finish_a_task = pyqtSignal()
    def __init__(self, api_key: str, user_name: str, history_path: str, generate_day_summary: bool) -> None:
        super().__init__()
        self.user_name = user_name
        self.history_manager = historyManager(user_name=self.user_name,history_path=history_path)
        self.inference = deepseek_summary(api_key, user_name)
        self.generate_day_summary = generate_day_summary
        self.signals = self.Signals()

    def get_task_num(self):
        return self.history_manager.current_history_index

    def run(self):
        current_day_summary_list = []
        for i in range(self.history_manager.current_history_index):
            if not self.history_manager.get_summary_by_index(i):
                self.history_manager.set_summary_by_index(i,self.inference.get_chat_summary(self.history_manager.get_history_dict_by_index(i))[0])
            crt_time = datetime.datetime.strptime(self.history_manager.get_create_time_by_index(i), "%Y-%m-%d %H:%M:%S")
            upd_time = datetime.datetime.strptime(self.history_manager.get_update_time_by_index(i), "%Y-%m-%d %H:%M:%S")
            current_day_summary_list.append(f"|{crt_time.hour}:{crt_time.minute}到{upd_time.hour}:{upd_time.minute} 你与{self.user_name}对话历史总结:{self.history_manager.get_summary_by_index(i)}|")
            self.signals.finish_a_task.emit()
        if self.generate_day_summary:
            self.history_manager.set_overall_summary(self.inference.get_day_summary(self.history_manager.get_full_data())[0])
        self.signals.all_finished.emit()
        self.signals.finish_a_task.emit()
            