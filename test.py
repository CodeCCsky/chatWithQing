import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from app.GUI import DesktopPet

index = 0

def change():
    global index
    index = (index + 1) % 7
    d.change_emo(index)

app = QApplication(sys.argv)
d = DesktopPet()
timer = QTimer()
timer.timeout.connect(change)
d.show()
timer.start(10000)

app.exec_()