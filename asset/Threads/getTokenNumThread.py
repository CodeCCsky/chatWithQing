from PyQt5.QtCore import QThread, pyqtSignal
from deepseek_api import offline_tokenizer

class get_token_num_thread(QThread):
    responseTokenNum = pyqtSignal(int)
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self.ofl_tokenizer = offline_tokenizer()
        self.text = text

    def run(self):
        print('run')
        num_of_tokens = self.ofl_tokenizer.count_tokens(self.text)
        self.responseTokenNum.emit(num_of_tokens)