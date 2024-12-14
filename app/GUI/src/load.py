import sys

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QWidget

import app.asset.res_rc
from app.GUI.Ui.Ui_load import Ui_Form


class loadWidget(QWidget, Ui_Form):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        fontDb = QFontDatabase()
        fontID = fontDb.addApplicationFont(":/font/荆南波波黑.ttf")
        self.setFont(QFont("荆南波波黑", 14, QFont.Bold))
        self.setupUi(self)
        self.finished_task_num = 0
        self.text_counter = 0
        self.text_timer = QTimer()
        self.text_timer.timeout.connect(self.update_loadLabel)
        self.text_timer.start(500)

    def update_loadLabel(self) -> None:
        self.text_counter = (self.text_counter + 1) % 3
        self.loadLabel.setText("加载中" + "." * (self.text_counter + 1))

    def set_detailLabel_text(self, text: str) -> None:
        self.detailLabel.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v0 = loadWidget()
    v0.show()
    sys.exit(app.exec_())
