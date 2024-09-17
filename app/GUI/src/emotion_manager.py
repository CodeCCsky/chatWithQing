import sys
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QListWidget


class emotionManager(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
    def initUI(self):
        self.vLayout = QHBoxLayout(self)
        self.menuListWidget = QListWidget(self)
        
        #self.setLayout(self.vLayout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = emotionManager()
    a.show()
    sys.exit(app.exec_())
