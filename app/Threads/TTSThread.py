import logging
from PyQt5.QtCore import QThread, pyqtSignal

from app.third_party.tts import TTSAudio
from requests.exceptions import ConnectionError


logger = logging.getLogger(__name__)


class tts_thread(QThread):
    startSpeak = pyqtSignal(bool)

    def __init__(self, tts_model: TTSAudio, tts_text: str) -> None:
        super().__init__()
        self.tts_model = tts_model
        self.tts_text = tts_text

    def run(self) -> None:
        try:
            for is_speak in self.tts_model.tts_request(self.tts_text):
                if is_speak:
                    self.startSpeak.emit(True)
        except ConnectionError:
            logger.error("TTS请求失败，请检查TTS是否正常启动")
            self.startSpeak.emit(True)
