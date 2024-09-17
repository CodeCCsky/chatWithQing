from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSignal, Qt
from app.GUI.src.pet_view import PetGraphicsView

# from pet_view import PetGraphicsView


class image_preview(QWidget):
    closeSignal = pyqtSignal()

    def __init__(self, zoom_factor: float, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(int(300 * zoom_factor), int(400 * zoom_factor))
        self.VLayout = QVBoxLayout(self)
        self.pet_image = PetGraphicsView(self)
        self.VLayout.addWidget(self.pet_image)

    def resize_(self, zoom_factor: float):
        self.setFixedSize(int(300 * zoom_factor), int(400 * zoom_factor))

    def closeEvent(self, a0: QCloseEvent):
        self.closeSignal.emit()
        self.hide()
        a0.ignore()

    def hide(self):
        self.setWindowFlags(Qt.Tool)
        super().hide()

    def show(self):
        self.setWindowFlags(Qt.Window)
        super().show()