from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QSoundEffect

class no_tts_sound_manager(QObject):
    def __init__(self, path, max_list_len = 5):
        super().__init__()
        self.file_path = path
        self.max_list_len = max_list_len
        self.sounds = []
        for _ in range(self.max_list_len):
            _player = QSoundEffect()
            _player.setSource(QUrl.fromLocalFile(self.file_path))
            self.sounds.append(_player)

    def play_audio(self):
        for i in range(self.max_list_len):
            if not self.sounds[i].isPlaying():
                self.sounds[i].play()
                break