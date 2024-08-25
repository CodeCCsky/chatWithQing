from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl, QTimer
import sys
from PyQt5.QtWidgets import QApplication

class SoundPlayer:
    def __init__(self, sound_file):
        self.sound_file = sound_file

    def play_sound(self):
        sound_effect = QSoundEffect()
        sound_effect.setSource(QUrl.fromLocalFile(self.sound_file))
        sound_effect.play()

index = 0
def play(a):
    global index
    if index < 5:
        a[index].play()
        index += 1

def main():
    app = QApplication(sys.argv)

    # 音频文件路径
    sound_file = r"asset\sound\speak.wav"

    # 创建 SoundPlayer 实例
    # 模拟多次调用 play_sound 方法
    a = []
    for _ in range(5):
        sound_effect = QSoundEffect()
        sound_effect.setSource(QUrl.fromLocalFile(sound_file))
        a.append(sound_effect)
    timer = QTimer()
    timer.timeout.connect(lambda p=a: play(a))
    timer.start(100)
    # 进入应用程序的主循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()