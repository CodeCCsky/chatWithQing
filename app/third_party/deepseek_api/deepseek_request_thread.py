from typing import Union

from PyQt5.QtCore import QThread, pyqtSignal

from app.third_party.deepseek_api import deepseek_model, historyManager


class PyQt_deepseek_request_thread(QThread):
    text_update = pyqtSignal(str)
    finish_signal = pyqtSignal(str)

    def __init__(self, model: deepseek_model, history_manager: historyManager) -> None:
        super().__init__()
        self.model = model
        self.history_manager = history_manager
        self.response = None
        self.finish_reason = None

    def run(self) -> None:
        self.response, self.finish_reason, _ = self.model.send_message()
        # self.history_manager.add_assistant_message(self.response)
        # self.history_manager.save_history()
        self.finish_signal.emit(self.finish_reason)

    def get_status(self) -> Union[str, None]:
        return self.model.is_done()

    def get_response(self) -> str:
        return self.response


from openai import OpenAI


class PyQt_deepseek_request_prefix_thread(QThread):
    finish_signal = pyqtSignal(str)

    def __init__(self, model: deepseek_model, prefix_message: str, history_manager: historyManager):
        super().__init__()
        self.client = OpenAI(api_key=model.get_api_key(), base_url="https://api.deepseek.com/beta")
        self.prefix_message = prefix_message
        self.temperature = model.get_temperature()
        self.frequency_penalty = model.get_frequency_penalty()
        self.presence_penalty = model.get_presence_penalty()
        self.request_data = history_manager.get_current_history()
        self.request_data.insert(0, {"role": "system", "content": model.get_system_prompt()})
        self.request_data.append({"role": "assistant", "content": self.prefix_message, "prefix": True})

    def run(self) -> None:
        self.response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=self.request_data,
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stream=False,
        )
        self.finish_signal.emit(self.response.choices[0].finish_reason)

    def get_full_response(self) -> str:
        return self.prefix_message + self.response.choices[0].message.content
