from typing import Union

from PyQt5.QtCore import QThread, pyqtSignal

from third_party.FixJSON import fixJSONwithLLM, fixJSON

class fixJSONThread(QThread):
    isFixed = pyqtSignal(bool)
    def __init__(self, json_str: str, api_key: str) -> None:
        super().__init__()
        self.json_str = json_str
        self.api_key = api_key

    def run(self) -> None:
        self.response = fixJSONwithLLM.loads(json_str=self.json_str, api_key=self.api_key)
        try:
            self.response = fixJSON.loads(self.response)
            self.isFixed.emit(True)
        except ValueError:
            self.isFixed.emit(False)

    def get_response(self) -> Union[str, dict]:
        return self.response