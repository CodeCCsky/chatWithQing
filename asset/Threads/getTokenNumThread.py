from PyQt5.QtCore import QThread, pyqtSignal
from deepseek_api import offline_tokenizer

class get_token_num_thread(QThread):
    responseTokenNum = pyqtSignal(int)
    def __init__(self, text: str, tokenizer: offline_tokenizer, parent=None) -> None:
        super().__init__(parent)
        self.tokenizer = tokenizer
        self.text = text

    def run(self):
        num_of_tokens = self.tokenizer.count_tokens(self.text)
        self.responseTokenNum.emit(num_of_tokens)
