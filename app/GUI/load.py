import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QWidget

#from Ui_load import Ui_Form
#import res_rc
import app.asset.res_rc
from app.GUI.Ui_load import Ui_Form


class loadWidget(QWidget, Ui_Form):
    def __init__(self, all_task_num: int, text: str = "少女祈祷中") -> None:
        super(loadWidget, self).__init__()
        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(':/font/荆南波波黑.ttf')
        self.setFont(QFont("荆南波波黑", 14, QFont.Bold))
        self.setupUi(self)
        self.all_task_num = all_task_num
        self.finished_task_num = 0
        self.text = text
        self.text_counter = 0
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.progress_text)
        self.text_timer.start(500)

    def progress_text(self) -> None:
        self.text_counter = (self.text_counter + 1) % 3
        self.label.setText(self.text + "." * (self.text_counter + 1))

    def finish_a_task(self) -> None:
        if self.finished_task_num < self.all_task_num:
            self.finished_task_num += 1
            self.progressBar.setValue(int(self.finished_task_num * 100 / self.all_task_num))

    def set_finish_task_num(self, value: int) -> None:
        if self.finished_task_num < self.all_task_num:
            self.finished_task_num = value
            self.progressBar.setValue(int(self.finished_task_num * 100 / self.all_task_num))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    v0 = loadWidget(1)
    v0.show()
    v0.finish_a_task()
    v0.set_finish_task_num(2)
    sys.exit(app.exec_())
