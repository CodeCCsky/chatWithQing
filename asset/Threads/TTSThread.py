from tts import TTSAudio
from PyQt5.QtCore import QThread, pyqtSignal

class tts_thread(QThread):# TODO test
    startSpeak = pyqtSignal(bool)
    def __init__(self, tts_model: TTSAudio, tts_text: str) -> None:
        super().__init__()
        self.tts_model = tts_model
        self.tts_text = tts_text
    def run(self) -> None:
        for is_speak in self.tts_model.tts_request(self.tts_text):
            if is_speak:
                self.startSpeak.emit(True)