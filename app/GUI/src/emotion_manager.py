from PyQt5.QtWidgets import QMainWindow

from app.GUI.Ui.Ui_emotion_setting import Ui_MainWindow
from third_party.emo_manager import emo_manager

class emotionManagerWidget(QMainWindow, Ui_MainWindow):
    def __init__(self, emo_manager_: emo_manager, parent=None) -> None:
        super(emotionManagerWidget, self).__init__(parent)
        self.emotion_manager = emo_manager_
        self.setupUi(self)

    def init_connect(self):
        self.categoryMenuListWidget.itemClicked.connect(self.sideListWidgetClicked)
        pass

    def progress_menu_selected(self, item):
        index = (self.categoryMenuListWidget.indexFromItem(item) - 1) / 2
        print(index)

