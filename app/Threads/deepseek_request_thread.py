from typing import Union

from PyQt5.QtCore import QThread, pyqtSignal

from deepseek_api import deepseek_model, historyManager


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